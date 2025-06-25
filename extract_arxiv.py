import os
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
from datetime import datetime

def extract_info_from_html(html_content):
    """从HTML内容中提取论文信息"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 查找所有arxiv结果
    arxiv_results = soup.find_all('li', class_='arxiv-result')
    
    entries = []

    for result in tqdm(arxiv_results, desc="提取论文记录", leave=False):
        entry = {}
        
        # 提取arxiv ID
        list_title = result.find('p', class_='list-title')
        if list_title and list_title.a:
            identifier = list_title.a.text
            entry['identifier'] = identifier
        
        # 提取标题
        title_elem = result.find('p', class_='title')
        if title_elem:
            entry['title'] = title_elem.text.strip()
        
        # 提取作者
        authors_elem = result.find('p', class_='authors')
        if authors_elem:
            # 只获取作者链接中的文本，不包括"Authors:"文本
            authors = [a.text for a in authors_elem.find_all('a')]
            entry['authors'] = ', '.join(authors)
        
        # 提取提交日期和公告月份
        submission_info = result.find('p', class_='is-size-7')
        if submission_info:
            submission_text = submission_info.text
            
            # 提取提交日期
            submitted_match = re.search(r'Submitted\s+(\d+\s+\w+),\s+(\d{4})', submission_text)
            if submitted_match:
                day_month = submitted_match.group(1)
                year = submitted_match.group(2)
                submission_date = f"{day_month}, {year}"
                # 转换日期格式为YYYY-MM-DD
                try:
                    date_obj = datetime.strptime(submission_date, '%d %B, %Y')
                    entry['first_submission'] = date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    entry['first_submission'] = submission_date
            
            # 提取公告月份
            announced_match = re.search(r'originally announced\s+(\w+\s+\d{4})', submission_text)
            if announced_match:
                announcement = announced_match.group(1)
                try:
                    date_obj = datetime.strptime(announcement, '%B %Y')
                    entry['first_announcement'] = date_obj.strftime('%Y-%m')
                except ValueError:
                    entry['first_announcement'] = announcement
        
        tags_div = result.find('div', class_='tags is-inline-block')
        if tags_div:
            all_tags = []
            for tag in tags_div.find_all('span', class_=['tag is-small is-link tooltip is-tooltip-top', 'tag is-small is-grey tooltip is-tooltip-top']):
                # 确保提取的是标签内部的文本而不是tooltip文本
                if tag.get_text().strip():
                    all_tags.append(tag.get_text().strip())
            entry['categories'] = ', '.join(all_tags)
        
        # 提取摘要 - 优先使用完整摘要
        abstract_full = result.find('span', id=lambda x: x and x.endswith('-abstract-full'))
        if abstract_full:
            # 移除"More/Less"按钮
            for a in abstract_full.find_all('a', class_='is-size-7'):
                a.extract()
            entry['abstract'] = abstract_full.text.strip()
        else:
            # 如果没有找到完整摘要，尝试获取短摘要
            abstract_short = result.find('span', id=lambda x: x and x.endswith('-abstract-short'))
            if abstract_short:
                # 移除"More"按钮
                for a in abstract_short.find_all('a', class_='is-size-7'):
                    a.extract()
                entry['abstract'] = abstract_short.text.strip()
        
        entries.append(entry)
    
    return entries

def format_to_markdown(entries):
    """将提取的信息格式化为Markdown"""
    md_content = ""
    
    for entry in tqdm(entries, desc="格式化为Markdown", leave=False):
        md_content += f"### 标题: {entry.get('title', '')}\n"
        md_content += f"> **arxiv**: {entry.get('identifier', '')}\n"
        md_content += f"> **Authors**: {entry.get('authors', '')}\n"
        md_content += f"> **First submission**: {entry.get('first_submission', '')}\n"
        md_content += f"> **First announcement**: {entry.get('first_announcement', '')}\n"
        md_content += f"> **领域**: {entry.get('categories', '')}\n"
        md_content += f"> **摘要**: {entry.get('abstract', '')}\n\n"
    
    return md_content

def process_html_files(input_folder, output_file):
    """处理文件夹中的所有HTML文件并输出到Markdown文件"""
    # 获取所有HTML文件
    html_files = [f for f in os.listdir(input_folder) if f.endswith('.html')]
    
    all_entries = []

    for html_file in tqdm(html_files, desc="处理HTML文件"):
        file_path = os.path.join(input_folder, html_file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        entries = extract_info_from_html(html_content)
        all_entries.extend(entries)
    
    # 格式化为Markdown并写入文件
    md_content = format_to_markdown(all_entries)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"处理完成! 共处理了 {len(html_files)} 个HTML文件，提取了 {len(all_entries)} 条记录")
    print(f"结果已保存到: {output_file}")

def main():
    input_folder = "q-bio_data\\page_html"
    output_file = "q-bio_data\\q-bio.md"
    
    process_html_files(input_folder, output_file)

if __name__ == "__main__":
    main()
