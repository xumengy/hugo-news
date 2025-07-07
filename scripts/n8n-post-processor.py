#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
n8n内容后处理器
专门用于处理n8n工作流抓取并上传到GitHub的markdown内容
"""

import re
import sys
import os
import json
import requests
from datetime import datetime
from pathlib import Path
import subprocess

class N8nPostProcessor:
    def __init__(self, content_dir="content/posts", static_dir="static/images"):
        self.content_dir = Path(content_dir)
        self.static_dir = Path(static_dir)
        self.content_dir.mkdir(parents=True, exist_ok=True)
        self.static_dir.mkdir(parents=True, exist_ok=True)
    
    def clean_n8n_content(self, content):
        """清理n8n抓取的内容"""
        
        # 1. 删除n8n特有的元数据
        content = re.sub(r'<!-- n8n.*?-->', '', content, flags=re.DOTALL)
        content = re.sub(r'\[Skip to main content\].*?\n', '', content)
        
        # 2. 删除原网站元素
        content = re.sub(r'## Comments.*', '', content, flags=re.DOTALL)
        content = re.sub(r'\[Add new comment\].*?\n', '', content)
        content = re.sub(r'\[.*?\]\(https://.*?\.com/tags/.*?\)\n', '', content)
        
        # 3. 清理HTML标签
        content = re.sub(r'<[^>]*>', '', content)
        
        # 4. 优化markdown格式
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r'^> \*\*([^*]+)\*\*:', r'> **\1**:', content, flags=re.MULTILINE)
        
        # 5. 修复图片链接
        content = self.fix_image_links(content)
        
        return content.strip()
    
    def fix_image_links(self, content):
        """修复图片链接，下载到本地"""
        def replace_image(match):
            alt_text = match.group(1)
            image_url = match.group(2)
            
            try:
                # 生成本地文件名
                filename = self.download_image(image_url)
                if filename:
                    return f'![{alt_text}](/images/{filename})'
                else:
                    return f'![{alt_text}]({image_url})'
            except:
                return f'![{alt_text}]({image_url})'
        
        return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, content)
    
    def download_image(self, url):
        """下载图片到本地"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # 从URL提取文件名
                filename = url.split('/')[-1]
                if '?' in filename:
                    filename = filename.split('?')[0]
                
                # 确保文件名唯一
                counter = 1
                original_filename = filename
                while (self.static_dir / filename).exists():
                    name, ext = os.path.splitext(original_filename)
                    filename = f"{name}_{counter}{ext}"
                    counter += 1
                
                # 保存图片
                with open(self.static_dir / filename, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ 下载图片: {filename}")
                return filename
        except Exception as e:
            print(f"⚠️ 下载图片失败 {url}: {e}")
        
        return None
    
    def generate_front_matter(self, title, description="", tags=None, categories=None, author="", draft=False, source_url=""):
        """生成Hugo front matter"""
        if tags is None:
            tags = []
        if categories is None:
            categories = []
        
        front_matter = f"""---
title: "{title}"
date: {datetime.now().strftime('%Y-%m-%d')}
description: "{description}"
tags: {tags}
categories: {categories}
author: "{author}"
draft: {str(draft).lower()}
source_url: "{source_url}"
---

"""
        return front_matter
    
    def extract_metadata(self, content):
        """从内容中提取元数据"""
        metadata = {
            'title': '未命名文章',
            'description': '',
            'tags': ['technology'],
            'categories': ['general'],
            'author': '原作者',
            'source_url': ''
        }
        
        # 提取标题
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
        
        # 提取链接作为来源
        url_match = re.search(r'https?://[^\s\)]+', content)
        if url_match:
            metadata['source_url'] = url_match.group(0)
        
        return metadata
    
    def auto_translate(self, content):
        """自动翻译内容（使用免费API）"""
        # 这里可以集成翻译API，如Google Translate或DeepL
        # 为了演示，我们返回原文
        return content
    
    def process_n8n_content(self, raw_content, output_filename=None):
        """处理n8n抓取的内容"""
        
        # 清理内容
        cleaned_content = self.clean_n8n_content(raw_content)
        
        # 提取元数据
        metadata = self.extract_metadata(cleaned_content)
        
        # 生成文件名
        if not output_filename:
            safe_title = re.sub(r'[^\w\s-]', '', metadata['title'])
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            output_filename = f"{datetime.now().strftime('%Y-%m-%d')}-{safe_title[:50]}.md"
        
        # 生成front matter
        front_matter = self.generate_front_matter(
            title=metadata['title'],
            description=metadata['description'],
            tags=metadata['tags'],
            categories=metadata['categories'],
            author=metadata['author'],
            source_url=metadata['source_url']
        )
        
        # 组合最终内容
        final_content = front_matter + cleaned_content + f"\n\n---\n\n*原文作者：{metadata['author']} | 通过n8n抓取并优化*"
        
        # 保存文件
        output_path = self.content_dir / output_filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"✅ 成功处理文章: {output_path}")
        return str(output_path)
    
    def git_commit_and_push(self, file_path, commit_message=None):
        """提交到Git并推送到GitHub"""
        try:
            if not commit_message:
                commit_message = f"添加新文章: {Path(file_path).stem}"
            
            # 添加文件
            subprocess.run(['git', 'add', file_path], check=True)
            
            # 提交
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            # 推送
            subprocess.run(['git', 'push'], check=True)
            
            print(f"✅ 成功提交并推送到GitHub: {commit_message}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git操作失败: {e}")
            return False

def main():
    """主函数"""
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h']:
        print("使用方法: python n8n-post-processor.py <输入文件> [输出文件名]")
        print("示例: python n8n-post-processor.py raw-content.md")
        print("选项:")
        print("  --help, -h    显示此帮助信息")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    processor = N8nPostProcessor()
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        
        # 处理内容
        output_path = processor.process_n8n_content(raw_content, output_file)
        
        # 询问是否提交到Git
        response = input("是否提交到GitHub? (y/n): ")
        if response.lower() == 'y':
            processor.git_commit_and_push(output_path)
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")

if __name__ == "__main__":
    main() 