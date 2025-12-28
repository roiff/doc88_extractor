# Web界面使用说明

## 功能特性

1. **网页前台界面** - 通过网页输入doc88文档链接
2. **实时进度提示** - 网页显示后台处理过程
3. **自动检查已下载文件** - 如果文档已转换过，直接提供下载，无需重新转换
4. **自动清理缓存** - 转换完成后自动清理临时文件
5. **直接下载** - 转换完成后可在网页直接下载PDF文件

## 启动Web服务

```bash
python3 app.py
```

服务将在 `http://0.0.0.0:5000` 启动，在浏览器中访问即可使用。

## 使用方法

1. 打开浏览器访问 `http://localhost:5000`
2. 在输入框中输入doc88文档链接（例如：`https://www.doc88.com/p-7065033333115.html`）
3. 点击"开始处理"按钮
4. 等待处理完成（网页会实时显示处理进度）
5. 处理完成后，点击"下载PDF"按钮即可下载文件

## 注意事项

- 如果文档已经转换过，系统会自动检测并直接提供下载，无需重新转换
- 转换过程可能需要较长时间，请耐心等待
- 转换完成后，系统会自动清理临时缓存文件
- 确保已安装Java环境（用于文档转换）
- 确保已安装所有Python依赖：`pip install -r requirements.txt`

## API接口

### 提交任务
```
POST /api/submit
Content-Type: application/json

{
  "url": "https://www.doc88.com/p-xxxxx.html"
}

返回: {"task_id": "1234567890"}
```

### 查询状态
```
GET /api/status/<task_id>

返回: {
  "status": "processing|completed|error",
  "message": "处理信息",
  "pdf_name": "文件名.pdf",
  "has_pdf": true|false
}
```

### 下载文件
```
GET /api/download/<task_id>

返回: PDF文件下载
```

