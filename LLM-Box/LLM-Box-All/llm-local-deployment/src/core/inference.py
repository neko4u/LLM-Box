import torch
from src.management.model_manager import ModelManager

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
        print(f"InferenceEngine initialized on device: {self.device}")

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
        # 如果模型尚未加载，则使用指定的运行时加载它
        if model_id not in self.model_manager.loaded_models:
            print(f"Model {model_id} not loaded. Loading now with '{runtime}' runtime...")
            self.model_manager.load_model(model_id, runtime=runtime)
        
        loaded_asset = self.model_manager.loaded_models.get(model_id)
        if not loaded_asset or loaded_asset.get('runtime') != runtime:
             # 如果模型已加载但运行时不匹配，则重新加载
            print(f"Reloading model {model_id} with '{runtime}' runtime...")
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
        outputs = model.generate(**inputs, max_length=max_length)
        
        # 3. 输出后处理：解码
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return generated_text