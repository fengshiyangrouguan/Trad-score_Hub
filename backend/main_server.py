from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys


from src.services import ScoreService
from src.api.routes import register_routes # 用于注册 API 路由


# 服务器配置(后续移植入.env)
HOST = '127.0.0.1'
PORT = 8000



def create_app():
    """创建并配置 Flask 应用程序实例。"""
    app = Flask(__name__)
    
    # 初始化核心服务
    score_service = ScoreService()
    
    # 注册 API 路由（注入 score_service） 
    register_routes(app, score_service)
    
    # 允许来自前端的跨域请求
    CORS(app)
    return app


if __name__ == '__main__':
    # 检查是否以独立脚本运行
    app = create_app()
    print(f"Starting Score Cloud Transcribe API server on http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=True) # 在生产环境禁用此调试模式