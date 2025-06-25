import os
import time
import requests
from bs4 import BeautifulSoup

def create_directory(directory):
    """创建目录，如果不存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def extract_next_page_link(html_content):
    """从HTML内容中提取下一页链接"""
    soup = BeautifulSoup(html_content, 'html.parser')
    next_link = soup.find('a', class_='pagination-next')
    
    if next_link and next_link.get('href'):
        href = next_link.get('href')
        # 删除所有的amp;
        clean_href = href.replace('amp;', '')
        # 添加域名
        full_url = 'https://arxiv.org' + clean_href
        return full_url
    return None

def crawl_arxiv_pages():
    """从1.html开始爬取所有下一页内容"""
    # 创建保存HTML文件的目录
    output_dir = 'page_html(20250101-20250516)'
    create_directory(output_dir)
    
    # 初始页面是本地的1.html
    with open('1.html', 'r', encoding='utf-8') as file:
        current_html = file.read()
    
    # 保存1.html到输出目录
    with open(os.path.join(output_dir, '1.html'), 'w', encoding='utf-8') as file:
        file.write(current_html)
    
    # 用于保存所有链接的文件
    pagelinks = []
    
    # 从第1页开始，获取下一页链接并爬取
    page_num = 1
    next_link = extract_next_page_link(current_html)
    
    # 当存在下一页链接时继续爬取
    while next_link:
        print(f"正在爬取第 {page_num + 1} 页: {next_link}")
        pagelinks.append(next_link)
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(next_link, headers=headers)
            
            # 检查请求是否成功
            if response.status_code == 200:
                page_num += 1
                page_html = response.text
                with open(os.path.join(output_dir, f'G_{page_num}.html'), 'w', encoding='utf-8') as file:
                    file.write(page_html)
                
                # 从新页面提取下一个链接
                next_link = extract_next_page_link(page_html)
                
                time.sleep(2)
            else:
                print(f"请求失败，状态码: {response.status_code}")
                break
        except Exception as e:
            print(f"爬取过程中出错: {e}")
            break
    
    with open('page_link(20250101-20250516).txt', 'w', encoding='utf-8') as file:
        for link in pagelinks:
            file.write(f"{link}\n")
    
    print(f"爬取完成! 共爬取 {page_num} 页，链接已保存到 pagelink.txt")

if __name__ == "__main__":
    crawl_arxiv_pages()
