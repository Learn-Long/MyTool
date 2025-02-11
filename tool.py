import requests
from bs4 import BeautifulSoup
import os

def parse_html(html_content):
    """解析HTML内容并提取所需资料"""
    result = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    for item in soup.find_all('div', class_='thread-item'):
        # 提取标题
        title_span = item.find('span', class_='thread-title')
        title = title_span.get_text(strip=True) if title_span else ''
        
        # 提取链接并添加.html后缀
        a_tag = item.find('a', href=True)
        if a_tag:
            href = a_tag['href']
            # 移除可能存在的多余斜杠并添加.html
            href = href.rstrip('/') + '.html'
            full_url = f"https://www.ptt.cc{href}"
        else:
            full_url = ''
        
        # 初始化条目资料
        entry = [title, full_url]
        
        # 提取评论
        for comment in item.find_all('div', class_='e7-top'):
            parts = []
            
            # 楼层
            floor_span = comment.find('span', class_='e7-floor')
            if floor_span: parts.append(floor_span.get_text(strip=True))
            
            # 箭头符号
            arrow_span = comment.find('span', class_='f11')
            if arrow_span: parts.append(arrow_span.get_text(strip=True))
            
            # 作者和内容
            author_span = comment.find('span', class_='e7-author')
            if author_span:
                parts.append(author_span.get_text(strip=True) + ":")
                # 提取作者后面的内容
                content_span = author_span.find_next_sibling('span', class_='yellow--text')
                if content_span:
                    content = content_span.get_text(strip=True).lstrip(':').strip()
                    parts.append(content)
            
            # IP和时间
            ip_time_span = comment.find('span', class_='grey--text')
            if ip_time_span: parts.append(ip_time_span.get_text(strip=True))
            
            entry.append(' '.join(parts))
        
        result.append(entry)
    return result

def process_files(user_id, page_count):
    """处理所有已下载文件并整合到主文件"""
    main_filename = f"{user_id}.txt"
    
    with open(main_filename, 'w', encoding='utf-8') as main_file:
        for page in range(page_count):
            filename = f"{user_id}{page}.txt"
            if not os.path.exists(filename):
                continue
            
            with open(filename, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            for entry in parse_html(html_content):
                # 写入标题和URL
                main_file.write(entry[0] + '\n')       # 标题
                main_file.write(entry[1] + '\n')       # URL
                
                # 写入所有评论
                for comment in entry[2:]:
                    main_file.write(comment + '\n')
                
                main_file.write('\n')  # 条目间空行分隔

def cleanup_temp_files(user_id, page_count):
    """清理临时文件"""
    print("\n正在清理临时文件...")
    for page in range(page_count):
        filename = f"{user_id}{page}.txt"
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print(f"已删除：{filename}")
            except Exception as e:
                print(f"删除{filename}失败：{str(e)}")
    print("清理完成！")

def main():
    # 初始设置
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # 获取用户输入
    user_id = input("请输入要查询的ID：").strip()
    page_count = input("请输入要查询的页数：").strip()

    # 验证输入
    try:
        page_count = int(page_count)
        if page_count <= 0:
            print("错误：页数必须大于0")
            return
    except ValueError:
        print("错误：请输入有效的整数页数")
        return

    # 下载页面
    for page in range(page_count):
        url = f"https://www.pttweb.cc/user/{user_id}/hatepolitics?t=message&page={page}"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            filename = f"{user_id}{page}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"已下载：{filename}")
            
        except Exception as e:
            print(f"下载页面 {page} 失败：{str(e)}")

    # 处理文件
    process_files(user_id, page_count)
    
    # 清理临时文件
    cleanup_temp_files(user_id, page_count)
    
    # 最终提示
    print(f"\n最终文件已保存至：{os.path.abspath(user_id)}.txt")

if __name__ == "__main__":
    main()