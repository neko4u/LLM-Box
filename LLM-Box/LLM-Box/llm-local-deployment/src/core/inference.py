import torch
import time
import logging
from threading import Thread
from transformers import TextIteratorStreamer
from src.management.model_manager import ModelManager

logger = logging.getLogger(__name__)

class InferenceEngine:
    """
    负责管理和执行模型推理的核心类。
    """
    def __init__(self, model_manager: ModelManager):
        """
        初始化推理引擎。

        Args:
            model_manager (ModelManager): 用于访问和加载模型的管理器实例。
        """
        self.model_manager = model_manager
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"InferenceEngine initialized on device: {self.device}")

    def generate(self, model_id: str, prompt: str, max_length: int = 50, runtime: str = 'pytorch'):
        """
        使用指定的模型生成文本。

        Args:
            model_id (str): 要使用的模型的ID。
            prompt (str): 输入的文本提示。
            max_length (int): 生成文本的最大长度。
            runtime (str): 要使用的运行时 ('pytorch' 或 'onnx')。

        Returns:
            str: 生成的文本。
        """
        start_time = time.time()
        
        # 如果模型尚未加载，则使用指定的运行时加载它
        if model_id not in self.model_manager.loaded_models or self.model_manager.loaded_models[model_id].get('runtime') != runtime:
            logger.info(f"Loading model {model_id} with '{runtime}' runtime...")
            self.model_manager.load_model(model_id, runtime=runtime)
        
        loaded_asset = self.model_manager.loaded_models.get(model_id)
        model = loaded_asset['model']
        tokenizer = loaded_asset['tokenizer']
        
        # 1. 文本预处理：分词和编码
        inputs = tokenizer(prompt, return_tensors="pt")

        # 将输入数据移动到正确的设备
        if runtime == 'pytorch':
            model.to(self.device)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # 2. 模型执行
        generate_start_time = time.time()
        outputs = model.generate(**inputs, max_length=max_length)
        generate_duration = time.time() - generate_start_time
        
        # 3. 输出后处理：解码
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        total_duration = time.time() - start_time
        
        logger.info(f"Model: {model_id}, Runtime: {runtime}, Device: {self.device}")
        logger.info(f"Generation time: {generate_duration:.4f}s, Total request time: {total_duration:.4f}s")
        if self.device == 'cuda':
            memory_allocated = torch.cuda.memory_allocated(self.device) / (1024 ** 2)
            logger.info(f"GPU Memory Allocated: {memory_allocated:.2f} MB")

        return generated_text

    def generate_stream(self, model_id: str, prompt: str, max_length: int = 256):
        """
        以流的形式生成文本，逐个返回词元。
        注意：此功能目前主要为PyTorch运行时优化。
        """
        if model_id not in self.model_manager.loaded_models or self.model_manager.loaded_models[model_id].get('runtime') != 'pytorch':
            logger.info(f"Loading model {model_id} with 'pytorch' runtime for streaming...")
            self.model_manager.load_model(model_id, runtime='pytorch')

        loaded_asset = self.model_manager.loaded_models.get(model_id)
        model = loaded_asset['model']
        tokenizer = loaded_asset['tokenizer']

        model.to(self.device)
        
        streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
        
        inputs = tokenizer(prompt, return_tensors="pt").to(self.device)
        
        generation_kwargs = dict(inputs, streamer=streamer, max_new_tokens=max_length)
        
        # 在单独的线程中运行生成，以便我们可以立即开始迭代
        thread = Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()

        # 从streamer中yield每个生成的词元
        for new_text in streamer:
            yield new_text