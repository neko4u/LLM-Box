from flask import Blueprint, request, jsonify
import logging
from src.management.model_manager import ModelManager
from src.management.data_manager import DataManager
from src.core.inference import InferenceEngine
# 从main.py导入sock实例
from src.main import sock 

api_bp = Blueprint('api', __name__)

# 实例化Manager和Engine
model_manager = ModelManager(storage_path='models_data')
data_manager = DataManager(storage_path='user_data') # 假设用户数据存储在不同路径
inference_engine = InferenceEngine(model_manager)

logger = logging.getLogger(__name__)

@sock.route('/api/generate-stream')
def generate_stream(ws):
    """
    通过WebSocket处理流式文本生成。
    客户端应发送一个JSON字符串，例如：
    {
        "model_id": "gpt2",
        "prompt": "Hello, world!",
        "max_length": 256
    }
    """
    logger.info("WebSocket connection established.")
    try:
        while True:
            data = ws.receive()
            if data:
                payload = json.loads(data)
                model_id = payload.get('model_id')
                prompt = payload.get('prompt')
                max_length = payload.get('max_length', 256)

                if not all([model_id, prompt]):
                    ws.send(json.dumps({'error': 'model_id and prompt are required'}))
                    continue
                
                logger.info(f"Streaming generation for model {model_id} with prompt: '{prompt[:50]}...'")
                for token in inference_engine.generate_stream(model_id, prompt, max_length):
                    ws.send(token)
                # 发送一个特殊标记表示生成结束
                ws.send("[END_OF_STREAM]")
    except Exception as e:
        logger.error(f"WebSocket Error: {e}", exc_info=True)
    finally:
        logger.info("WebSocket connection closed.")

@api_bp.route('/generate', methods=['POST'])
def generate_text():
    """
    使用指定模型进行文本生成。
    请求体示例:
    {
        "model_id": "gpt2",
        "prompt": "Hello, world!",
        "max_length": 50,
        "runtime": "pytorch"
    }
    """
    data = request.get_json()
    model_id = data.get('model_id')
    prompt = data.get('prompt')
    max_length = data.get('max_length', 50)
    runtime = data.get('runtime', 'pytorch') # 默认为pytorch

    if not all([model_id, prompt]):
        return jsonify({'error': 'model_id and prompt are required'}), 400

    try:
        generated_text = inference_engine.generate(
            model_id=model_id,
            prompt=prompt,
            max_length=max_length,
            runtime=runtime
        )
        return jsonify({'generated_text': generated_text}), 200
    except Exception as e:
        logger.error(f"Error during text generation for model {model_id}: {e}", exc_info=True)
        return jsonify({'error': 'An internal server error occurred during generation.'}), 500

@api_bp.route('/models', methods=['GET'])
def list_models():
    """列出所有本地可用的模型。"""
    models = model_manager.list_models()
    return jsonify(models), 200

@api_bp.route('/models/download', methods=['POST'])
def download_model():
    """从Hugging Face Hub下载模型。"""
    data = request.get_json()
    model_id = data.get('model_id')
    if not model_id:
        return jsonify({'error': 'model_id is required'}), 400
    
    try:
        metadata = model_manager.download_model(model_id)
        logger.info(f"Model {model_id} downloaded successfully.")
        return jsonify({'message': f'Model {model_id} downloaded successfully.', 'metadata': metadata}), 201
    except Exception as e:
        logger.error(f"Error downloading model {model_id}: {e}", exc_info=True)
        return jsonify({'error': 'An internal server error occurred during download.'}), 500

@api_bp.route('/models/<path:model_id>', methods=['GET'])
def get_model_details(model_id):
    """获取特定模型的详细信息。"""
    model_details = model_manager.get_model(model_id)
    if model_details:
        return jsonify(model_details), 200
    return jsonify({'error': 'Model not found'}), 404

@api_bp.route('/models/load', methods=['POST'])
def load_model():
    """将模型加载到内存中以进行推理。"""
    data = request.get_json()
    model_id = data.get('model_id')
    if not model_id:
        return jsonify({'error': 'model_id is required'}), 400
    
    try:
        model_manager.load_model(model_id)
        return jsonify({'message': f'Model {model_id} loaded into memory.'}), 200
    except Exception as e:
        logger.error(f"Error loading model {model_id}: {e}", exc_info=True)
        return jsonify({'error': 'An internal server error occurred during model loading.'}), 500

@api_bp.route('/models/convert', methods=['POST'])
def convert_model():
    """转换模型格式，例如转换为ONNX。"""
    data = request.get_json()
    model_id = data.get('model_id')
    target_format = data.get('format', 'onnx') # 默认为onnx
    quantize = data.get('quantize', False)

    if not model_id:
        return jsonify({'error': 'model_id is required'}), 400

    try:
        if target_format == 'onnx':
            output_path = model_manager.convert_to_onnx(model_id, quantize=quantize)
            return jsonify({'message': f'Model converted to {target_format}', 'output_path': output_path}), 200
        else:
            return jsonify({'error': f'Unsupported format: {target_format}'}), 400
    except Exception as e:
        logger.error(f"Error converting model {model_id} to {target_format}: {e}", exc_info=True)
        return jsonify({'error': 'An internal server error occurred during conversion.'}), 500

@api_bp.route('/data', methods=['GET'])
def list_data():
    data = data_manager.list_data()
    return jsonify(data), 200

@api_bp.route('/data/<data_id>', methods=['GET'])
def get_data(data_id):
    data = data_manager.get_data(data_id)
    if data:
        return jsonify(data), 200
    return jsonify({'error': 'Data not found'}), 404

@api_bp.route('/data', methods=['POST'])
def upload_data():
    data_file = request.files.get('data')
    if not data_file:
        return jsonify({'error': 'No data file provided'}), 400
    data_id = data_manager.upload_data(data_file)
    return jsonify({'data_id': data_id}), 201