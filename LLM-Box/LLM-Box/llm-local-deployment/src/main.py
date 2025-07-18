from flask import Flask, render_template
from flask_sock import Sock
from src.api.routes import api_bp
from src.core.logging_config import setup_logging
import logging

# 在创建app之前设置日志
setup_logging()

app = Flask(__name__, template_folder='../templates')
sock = Sock(app) # 初始化Sock

# 注册API蓝图
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    """提供前端UI界面。"""
    return render_template('index.html')

if __name__ == '__main__':
    logging.info("Starting LLM Local Deployment Server...")
    # 运行app，可以通过host='0.0.0.0'使其在网络上可访问
    app.run(debug=True, port=5001)