#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown内容清理脚本
用于优化从其他网站抓取的markdown内容
"""

import re
import sys
import os
from datetime import datetime

def clean_markdown_content(content):
    """清理markdown内容"""
    
    # 1. 删除原网站的导航链接
    content = re.sub(r'\[Skip to main content\].*?\n', '', content)
    
    # 2. 删除评论部分
    content = re.sub(r'## Comments.*', '', content, flags=re.DOTALL)
    
    # 3. 删除原网站的标签链接
    content = re.sub(r'\[.*?\]\(https://.*?\.com/tags/.*?\)\n', '', content)
    
    # 4. 删除"Add new comment"链接
    content = re.sub(r'- \[Add new comment\].*?\n', '', content)
    
    # 5. 清理多余的空白行
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # 6. 优化图片链接（确保可以正常显示）
    content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'![\1](\2)', content)
    
    # 7. 统一引用格式
    content = re.sub(r'^> \*\*([^*]+)\*\*:', r'> **\1**:', content, flags=re.MULTILINE)
    
    # 8. 清理HTML标签（保留必要的）
    content = re.sub(r'<[^>]*>', '', content)
    
    return content.strip()

def generate_front_matter(title, description="", tags=None, categories=None, author="", draft=False):
    """生成front matter"""
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
---

"""
    return front_matter

def process_file(input_file, output_file, title, description="", tags=None, categories=None, author="", draft=False):
    """处理单个文件"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 清理内容
        cleaned_content = clean_markdown_content(content)
        
        # 生成front matter
        front_matter = generate_front_matter(title, description, tags, categories, author, draft)
        
        # 组合最终内容
        final_content = front_matter + cleaned_content + "\n\n---\n\n*原文作者：" + author + " | 翻译和重新排版*"
        
        # 写入输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"✅ 成功处理文件: {output_file}")
        
    except Exception as e:
        print(f"❌ 处理文件时出错: {e}")

def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("使用方法: python clean-markdown.py <输入文件> <输出文件> [标题] [描述]")
        print("示例: python clean-markdown.py raw-content.md cleaned-content.md '文章标题' '文章描述'")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else "未命名文章"
    description = sys.argv[4] if len(sys.argv) > 4 else ""
    
    # 默认标签和分类
    tags = ["technology", "web"]
    categories = ["general"]
    author = "原作者"
    
    process_file(input_file, output_file, title, description, tags, categories, author)

if __name__ == "__main__":
    main() 