

一个简洁高效的 Python 批量文件下载工具，支持并发下载、自动文件名提取和智能 URL 编码。

## ✨ 特性

- ⚡ **并发下载**：可配置线程池，大幅提升下载效率
- 📁 **智能文件名**：自动从 URL path 或 query 参数中提取文件名
- 🔤 **URL 编码**：自动处理 URL 中的非 ASCII 字符（如中文）
- 💾 **防重命名**：自动为重复文件添加序号后缀
- ⏱️ **超时控制**：可自定义下载超时时间
- 📊 **进度友好**：显示每个文件的下载状态和大小信息
- 🛡️ **健壮错误处理**：HTTP 状态码检查与异常捕获

## 🚀 快速开始

### 1. 准备 URL 列表
创建 `urls.txt` 文件，每行一个下载链接：

```
https://example.com/file1.zip
https://example.com/文档.pdf
https://example.com/download?path=image.jpg

```

### 2. 配置参数
在脚本开头修改配置（可选）：
```python
URL_FILE = "urls.txt"      # URL 列表文件
SAVE_DIR = "downloads"     # 保存目录
MAX_WORKERS = 5            # 并发线程数
TIMEOUT = 30               # 超时时间（秒）
```

### 3. 运行
```bash
python batchget.py
```

## 📂 项目结构
```
batchget/
├── batchget.py      # 主脚本
├── urls.txt         # URL 列表（需自建）
└── downloads/       # 下载目录（自动创建）
```

## ⚙️ 工作原理

1. 从 `urls.txt` 读取每行 URL
2. 使用线程池并发下载（最多 `MAX_WORKERS` 个）
3. 对每个 URL：
   - 提取/生成文件名
   - 处理非 ASCII 字符编码
   - 下载并显示进度
   - 自动处理文件重名
4. 汇总显示成功/失败统计

## 💡 最佳实践

- **线程数建议**：普通网络环境 3-5 线程，高速网络可 8-10
- **超时设置**：大文件建议 `TIMEOUT = 60` 或更高
- **URL 格式**：确保 URL 可直链访问，无需登录验证

## 📝 示例输出
```
[1/3] https://example.com/file.zip -> file.zip (12.5 MB) ✓
[2/3] https://example.com/文档.pdf -> 文档.pdf (3.2 MB) ✓
[3/3] https://invalid-url -> 失败: HTTP 状态码: 404
---
完成: 成功 2, 失败 1
```

## 🔧 自定义

可通过修改 `get_filename()` 和 `encode_url()` 函数适配特殊 URL 格式。

## 📄 许可证

MIT License - 自由使用，随意修改
