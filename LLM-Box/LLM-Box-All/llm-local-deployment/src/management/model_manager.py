import os
import json
import hashlib
from pathlib import Path
from huggingface_hub import snapshot_download, HfApi
from transformers import AutoModel, AutoTokenizer, AutoConfig
import torch
from optimum.onnxruntime import ORTModelForCausalLM
from optimum.bettertransformer import BetterTransformer

class ModelManager:
    def __init__(self, storage_path='models_data'):
        self.storage_path = Path(storage_path)
        self.models_dir = self.storage_path / 'models'
        self.metadata_path = self.storage_path / 'models_metadata.json'
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.metadata = self._load_metadata()
        self.loaded_models = {} # 用于内存中加载模型的缓存

    def _load_metadata(self):
        if self.metadata_path.exists():
            with open(self.metadata_path, 'r') as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=4)

    def download_model(self, model_id: str, revision: str = "main"):
        """从Hugging Face Hub下载模型和分词器。"""
        if model_id in self.metadata and self.metadata[model_id].get('revision') == revision:
            return self.metadata[model_id]

        path = snapshot_download(repo_id=model_id, revision=revision, cache_dir=self.models_dir)
        
        self.metadata[model_id] = {
            'model_id': model_id,
            'path': str(path),
            'revision': revision,
            'formats': {'original': str(path)}
        }
        self._save_metadata()
        return self.metadata[model_id]

    def load_model(self, model_id: str, runtime: str = 'pytorch', use_bettertransformer: bool = False):
        """
        根据指定的运行时加载模型到内存中。
        
        Args:
            model_id (str): 模型的ID。
            runtime (str): 'pytorch' 或 'onnx'。
            use_bettertransformer (bool): 是否使用BetterTransformer优化。
        """
        if model_id in self.loaded_models and self.loaded_models[model_id].get('runtime') == runtime:
            return self.loaded_models[model_id]

        if model_id not in self.metadata:
            raise FileNotFoundError(f"Model {model_id} not found in local storage.")

        try:
            if runtime == 'pytorch':
                model_path = self.metadata[model_id]['path']
                model = AutoModel.from_pretrained(model_path)
                tokenizer = AutoTokenizer.from_pretrained(model_path)
                if use_bettertransformer:
                    model = BetterTransformer.transform(model)
            elif runtime == 'onnx':
                onnx_path = self.metadata[model_id].get('formats', {}).get('onnx')
                if not onnx_path or not os.path.exists(onnx_path):
                    raise FileNotFoundError(f"ONNX format for model {model_id} not found. Please convert it first.")
                # ONNX Runtime 会自动选择可用的最佳执行提供者（如CUDA、CPU）
                model = ORTModelForCausalLM.from_pretrained(onnx_path)
                tokenizer = AutoTokenizer.from_pretrained(onnx_path)
            else:
                raise ValueError(f"Unsupported runtime: {runtime}")

            self.loaded_models[model_id] = {'model': model, 'tokenizer': tokenizer, 'runtime': runtime}
            print(f"Successfully loaded {model_id} with {runtime} runtime.")
            return self.loaded_models[model_id]
        except Exception as e:
            raise RuntimeError(f"Failed to load model {model_id} with {runtime} runtime: {e}") from e

    def convert_to_onnx(self, model_id: str, quantize: bool = False):
        """将模型转换为ONNX格式，并可选择进行量化。"""
        if 'onnx' in self.metadata.get(model_id, {}).get('formats', {}):
            return self.metadata[model_id]['formats']['onnx']

        if model_id not in self.metadata:
            raise FileNotFoundError(f"Model {model_id} not found. Please download it first.")

        model_path = self.metadata[model_id]['path']
        output_dir = self.models_dir / f"{model_id.replace('/', '_')}-onnx"
        output_dir.mkdir(exist_ok=True)

        try:
            # 使用optimum进行转换和量化
            model = ORTModelForCausalLM.from_pretrained(model_path, export=True)
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            
            if quantize:
                # 此处可以添加更复杂的量化配置
                from optimum.onnxruntime.configuration import AutoQuantizationConfig
                from optimum.onnxruntime import ORTQuantizer

                qconfig = AutoQuantizationConfig.avx512_vnni(is_static=False, per_channel=False)
                quantizer = ORTQuantizer.from_pretrained(model)
                quantizer.quantize(save_dir=output_dir, quantization_config=qconfig)
            else:
                model.save_pretrained(output_dir)
            
            tokenizer.save_pretrained(output_dir)

            self.metadata[model_id]['formats']['onnx'] = str(output_dir)
            self._save_metadata()
            return str(output_dir)
        except Exception as e:
            raise RuntimeError(f"Failed to convert {model_id} to ONNX: {e}") from e

    def list_models(self):
        return list(self.metadata.keys())

    def get_model(self, model_id):
        return self.metadata.get(model_id)