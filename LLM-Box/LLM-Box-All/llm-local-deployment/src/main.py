from flask import Flask, render_template
from src.api.routes import api_bp

app = Flask(__name__, template_folder='../templates')

# 注册API蓝图
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    """提供前端UI界面。"""
    return render_template('index.html')

if __name__ == '__main__':
    # 运行app，可以通过host='0.0.0.0'使其在网络上可访问
    app.run(debug=True, port=5001)