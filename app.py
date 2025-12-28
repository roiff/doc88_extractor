# -*- coding: utf-8 -*-

import os
import json
import threading
import time
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from config import *
from main import get_cfg, main, clean
from utils import ospath, special_path, read_file
from coder import decode
import sys

app = Flask(__name__)
CORS(app)

# 存储任务状态
tasks = {}

def check_existing_pdf(p_code, p_name):
    """检查是否已经存在转换好的PDF文件"""
    pdf_name = cfg2.o_dir_path + special_path(p_name) + ".pdf"
    if os.path.exists(ospath(pdf_name)):
        return pdf_name
    return None

def process_document(url, task_id):
    """处理文档的后台任务"""
    try:
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["message"] = "正在获取文档信息..."
        
        # 获取配置（非交互模式）
        try:
            cfg_obj = get_cfg(url, interactive=False)
        except Exception as e:
            raise Exception(f"获取文档配置失败: {str(e)}")
        
        # 检查data是否为空（添加更详细的检查）
        if not cfg_obj.data:
            raise Exception("无法获取文档配置数据：data为空，可能是网络问题、文档已被删除或页面格式已更改")
        
        if cfg_obj.data.strip() == "":
            raise Exception("无法获取文档配置数据：data为空字符串，可能是页面格式已更改")
        
        # 数据是编码后的字符串，需要先解码
        try:
            decoded_data = decode(cfg_obj.data)
        except Exception as e:
            raise Exception(f"解码文档配置数据失败: {str(e)}")
        
        # 尝试解析JSON
        try:
            config = json.loads(decoded_data)
        except json.JSONDecodeError as e:
            # 记录实际的数据内容（前100个字符）以便调试
            data_preview = decoded_data[:100] if len(decoded_data) > 100 else decoded_data
            raise Exception(f"解析文档配置数据失败，数据格式错误: {str(e)}\n解码后的数据预览: {repr(data_preview)}")
        
        # 从配置中获取基本信息（不调用init，避免交互问题）
        p_code = config.get("p_code", "")
        p_name = config.get("p_name", "")
        
        # 检查是否已存在PDF（提前检查可以更快返回）
        pdf_name = cfg2.o_dir_path + special_path(p_name) + ".pdf"
        if os.path.exists(ospath(pdf_name)):
            tasks[task_id]["status"] = "completed"
            tasks[task_id]["message"] = f"文档已存在，无需重新转换\n文档名：{p_name}\n文档ID：{p_code}"
            tasks[task_id]["pdf_path"] = pdf_name
            tasks[task_id]["pdf_name"] = os.path.basename(pdf_name)
            return
        
        tasks[task_id]["message"] = f"文档名：{p_name}\n文档ID：{p_code}\n开始处理..."
        
        # 调用main函数处理（非交互模式，main函数内部会检查PDF是否存在）
        result = main(cfg_obj.data, cfg2.get_more, interactive=False, debug_mode=False)
        
        if result:
            # 再次检查PDF文件（main函数中已经清理了缓存，所以需要重新检查）
            if os.path.exists(ospath(pdf_name)):
                tasks[task_id]["status"] = "completed"
                tasks[task_id]["message"] = "转换完成！"
                tasks[task_id]["pdf_path"] = pdf_name
                tasks[task_id]["pdf_name"] = os.path.basename(pdf_name)
            else:
                tasks[task_id]["status"] = "error"
                tasks[task_id]["message"] = "转换完成但未找到PDF文件"
        else:
            tasks[task_id]["status"] = "error"
            tasks[task_id]["message"] = "处理失败"
            
    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["message"] = f"错误: {str(e)}"
        import traceback
        traceback.print_exc()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/submit', methods=['POST'])
def submit():
    """提交处理任务"""
    data = request.json
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({"error": "URL不能为空"}), 400
    
    # 验证URL
    if url.find("doc88.com/p-") == -1 and url.find("doc88.piglin.eu.org/p-") == -1:
        return jsonify({"error": "无效的URL，请输入doc88.com的文档链接"}), 400
    
    # 生成任务ID
    task_id = str(int(time.time() * 1000))
    tasks[task_id] = {
        "status": "pending",
        "message": "任务已创建",
        "pdf_path": None,
        "pdf_name": None
    }
    
    # 启动后台任务
    thread = threading.Thread(target=process_document, args=(url, task_id))
    thread.daemon = True
    thread.start()
    
    return jsonify({"task_id": task_id})

@app.route('/api/status/<task_id>')
def get_status(task_id):
    """获取任务状态"""
    if task_id not in tasks:
        return jsonify({"error": "任务不存在"}), 404
    
    task = tasks[task_id]
    return jsonify({
        "status": task["status"],
        "message": task["message"],
        "pdf_name": task.get("pdf_name"),
        "has_pdf": task.get("pdf_path") is not None
    })

@app.route('/api/download/<task_id>')
def download(task_id):
    """下载PDF文件"""
    if task_id not in tasks:
        return jsonify({"error": "任务不存在"}), 404
    
    task = tasks[task_id]
    if task["status"] != "completed" or not task.get("pdf_path"):
        return jsonify({"error": "文件尚未准备好"}), 400
    
    pdf_path = task["pdf_path"]
    if not os.path.exists(ospath(pdf_path)):
        return jsonify({"error": "文件不存在"}), 404
    
    return send_file(
        ospath(pdf_path),
        as_attachment=True,
        download_name=task["pdf_name"]
    )

if __name__ == '__main__':
    # 初始化检查
    from updater import Update
    update = Update(cfg2)
    if not update.check_java():
        print("警告: 未检测到Java，转换功能可能无法使用")
    update.check_ffdec_update()
    if cfg2.check_update:
        update.check_update()
    update.upgrade()
    
    app.run(host='0.0.0.0', port=5002, debug=False)

