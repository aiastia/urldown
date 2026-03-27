import os
import sys
import threading
from urllib.request import urlopen, Request
from urllib.parse import urlparse, unquote, quote, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置
URL_FILE = "urls.txt"       # URL 列表文件，每行一个链接
SAVE_DIR = "downloads"      # 下载保存目录
MAX_WORKERS = 5             # 并发线程数
TIMEOUT = 30                # 超时时间（秒）


def get_filename(url: str) -> str:
    """从 URL 中提取文件名，无法提取时用序号代替"""
    parsed = urlparse(url)
    name = os.path.basename(unquote(parsed.path))
    if not name or '.' not in name:
        # 从 query 参数中提取文件名（如 ?path=xxx.txt）
        qs = parse_qs(parsed.query)
        if 'path' in qs:
            name = qs['path'][0]
        else:
            name = parsed.netloc.replace(':', '_')
    return name


def encode_url(url: str) -> str:
    """对 URL 中的非 ASCII 字符进行 percent-encoding，保留已编码的部分"""
    parsed = urlparse(url)
    # 只对 path 和 query 中的非 ASCII 字符编码，safe 参数保留已编码的 %XX
    encoded_path = quote(parsed.path, safe='/:@!$&\'()*+,;=')
    encoded_query = quote(parsed.query, safe='/:@!$&\'()*+,;=') if parsed.query else ''
    encoded = parsed._replace(path=encoded_path, query=encoded_query).geturl()
    return encoded


def download_one(url: str, index: int) -> tuple[str, bool, str]:
    """
    下载单个文件。
    返回: (url, 是否成功, 消息)
    """
    filename = get_filename(url)
    filepath = os.path.join(SAVE_DIR, filename)

    # 同名文件加序号
    if os.path.exists(filepath):
        base, ext = os.path.splitext(filename)
        i = 1
        while os.path.exists(filepath):
            filepath = os.path.join(SAVE_DIR, f"{base}_{i}{ext}")
            i += 1

    try:
        # 对 URL 中的中文等非 ASCII 字符进行编码
        encoded_url = encode_url(url)
        req = Request(encoded_url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=TIMEOUT) as resp:
            # 检查状态码
            if resp.status != 200:
                return url, False, f"HTTP 状态码: {resp.status}"

            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            with open(filepath, 'wb') as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

            size_mb = downloaded / (1024 * 1024)
            if total:
                print(f"[✓] #{index} {filename}  ({size_mb:.2f} MB)")
            else:
                print(f"[✓] #{index} {filename}  ({size_mb:.2f} MB, 大小未知)")
            return url, True, ""

    except Exception as e:
        return url, False, str(e)


def main():
    # 检查 URL 文件
    if not os.path.exists(URL_FILE):
        print(f"错误: 找不到文件 '{URL_FILE}'")
        print(f"请创建 {URL_FILE}，每行放一个下载链接")
        sys.exit(1)

    # 读取 URL 列表
    with open(URL_FILE, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    if not urls:
        print(f"错误: '{URL_FILE}' 中没有有效的链接")
        sys.exit(1)

    # 创建保存目录
    os.makedirs(SAVE_DIR, exist_ok=True)

    print(f"共 {len(urls)} 个链接, {MAX_WORKERS} 线程并发下载")
    print(f"保存目录: {os.path.abspath(SAVE_DIR)}")
    print("-" * 60)

    success_count = 0
    fail_count = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(download_one, url, i + 1): url
            for i, url in enumerate(urls)
        }
        for future in as_completed(futures):
            url, ok, msg = future.result()
            if ok:
                success_count += 1
            else:
                fail_count += 1
                print(f"[✗] 下载失败: {url}")
                print(f"    原因: {msg}")

    print("-" * 60)
    print(f"完成! 成功: {success_count}, 失败: {fail_count}, 总计: {len(urls)}")


if __name__ == "__main__":
    main()