# n8n工作流优化指南

## 概述

本指南将帮助您优化n8n工作流，使其抓取的内容能够更好地集成到您的Hugo网站中。

## n8n工作流优化建议

### 1. 内容抓取节点优化

#### HTTP Request节点配置
```json
{
  "method": "GET",
  "url": "{{ $json.target_url }}",
  "headers": {
    "User-Agent": "Mozilla/5.0 (compatible; n8n-bot/1.0)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
  },
  "timeout": 30000
}
```

#### HTML Extract节点配置
```json
{
  "extractionValues": {
    "title": {
      "selector": "h1, .post-title, .entry-title",
      "returnArray": false
    },
    "content": {
      "selector": ".post-content, .entry-content, article",
      "returnArray": false
    },
    "author": {
      "selector": ".author, .byline, [rel='author']",
      "returnArray": false
    },
    "date": {
      "selector": ".date, .published, time",
      "returnArray": false
    },
    "tags": {
      "selector": ".tags a, .tag",
      "returnArray": true
    }
  }
}
```

### 2. 内容处理节点

#### Function节点 - 内容清理
```javascript
// 清理HTML标签，转换为Markdown
function cleanContent(html) {
  // 移除脚本和样式
  html = html.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '');
  html = html.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '');
  
  // 转换标题
  html = html.replace(/<h1[^>]*>(.*?)<\/h1>/gi, '# $1\n\n');
  html = html.replace(/<h2[^>]*>(.*?)<\/h2>/gi, '## $1\n\n');
  html = html.replace(/<h3[^>]*>(.*?)<\/h3>/gi, '### $1\n\n');
  
  // 转换段落
  html = html.replace(/<p[^>]*>(.*?)<\/p>/gi, '$1\n\n');
  
  // 转换链接
  html = html.replace(/<a[^>]*href="([^"]*)"[^>]*>(.*?)<\/a>/gi, '[$2]($1)');
  
  // 转换图片
  html = html.replace(/<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*>/gi, '![$2]($1)');
  
  // 转换粗体和斜体
  html = html.replace(/<strong[^>]*>(.*?)<\/strong>/gi, '**$1**');
  html = html.replace(/<em[^>]*>(.*?)<\/em>/gi, '*$1*');
  
  // 转换列表
  html = html.replace(/<ul[^>]*>([\s\S]*?)<\/ul>/gi, function(match, content) {
    return content.replace(/<li[^>]*>(.*?)<\/li>/gi, '- $1\n') + '\n';
  });
  
  // 清理多余空白
  html = html.replace(/\n\s*\n\s*\n/g, '\n\n');
  
  return html.trim();
}

// 处理输入数据
const items = $input.all();
const processedItems = [];

for (const item of items) {
  const cleanedContent = cleanContent(item.json.content || '');
  
  processedItems.push({
    json: {
      ...item.json,
      cleaned_content: cleanedContent,
      processed_at: new Date().toISOString()
    }
  });
}

return processedItems;
```

### 3. 元数据提取节点

#### Function节点 - 元数据提取
```javascript
// 提取和标准化元数据
function extractMetadata(content, title, author, date) {
  // 生成描述
  const description = content.substring(0, 200).replace(/[#*`]/g, '') + '...';
  
  // 提取标签
  const tagPatterns = [
    /#(\w+)/g,
    /标签[：:]\s*([^，,。\n]+)/g,
    /Tags[：:]\s*([^，,。\n]+)/g
  ];
  
  const tags = new Set();
  tagPatterns.forEach(pattern => {
    const matches = content.match(pattern);
    if (matches) {
      matches.forEach(match => {
        const tag = match.replace(/[#：:]/g, '').trim();
        if (tag.length > 0 && tag.length < 20) {
          tags.add(tag);
        }
      });
    }
  });
  
  // 分类标签
  const categories = [];
  if (content.includes('技术') || content.includes('tech')) categories.push('technology');
  if (content.includes('编程') || content.includes('programming')) categories.push('programming');
  if (content.includes('设计') || content.includes('design')) categories.push('design');
  
  return {
    title: title || '未命名文章',
    description: description,
    author: author || '原作者',
    date: date || new Date().toISOString().split('T')[0],
    tags: Array.from(tags).slice(0, 5),
    categories: categories.length > 0 ? categories : ['general']
  };
}

const items = $input.all();
const processedItems = [];

for (const item of items) {
  const metadata = extractMetadata(
    item.json.cleaned_content,
    item.json.title,
    item.json.author,
    item.json.date
  );
  
  processedItems.push({
    json: {
      ...item.json,
      ...metadata
    }
  });
}

return processedItems;
```

### 4. GitHub集成节点

#### GitHub节点配置
```json
{
  "operation": "create",
  "owner": "{{ $json.github_owner }}",
  "repository": "{{ $json.github_repo }}",
  "path": "content/posts/{{ $json.filename }}",
  "message": "添加新文章: {{ $json.title }}",
  "content": "{{ $json.markdown_content }}",
  "branch": "main"
}
```

### 5. 完整工作流示例

#### 工作流结构
```
1. HTTP Request (抓取网页)
2. HTML Extract (提取内容)
3. Function (清理HTML)
4. Function (提取元数据)
5. Function (生成Markdown)
6. GitHub (上传文件)
7. Slack/Email (通知)
```

#### 生成Markdown的Function节点
```javascript
function generateMarkdown(item) {
  const { title, description, author, date, tags, categories, cleaned_content, source_url } = item.json;
  
  const frontMatter = `---
title: "${title}"
date: ${date}
description: "${description}"
tags: ${JSON.stringify(tags)}
categories: ${JSON.stringify(categories)}
author: "${author}"
draft: false
source_url: "${source_url || ''}"
---

`;

  const content = cleaned_content;
  const footer = `

---

*原文作者：${author} | 通过n8n抓取并优化*`;

  return frontMatter + content + footer;
}

const items = $input.all();
const processedItems = [];

for (const item of items) {
  const markdown = generateMarkdown(item);
  const filename = `${item.json.date}-${item.json.title.replace(/[^\w\s-]/g, '').replace(/\s+/g, '-').substring(0, 50)}.md`;
  
  processedItems.push({
    json: {
      ...item.json,
      markdown_content: markdown,
      filename: filename
    }
  });
}

return processedItems;
```

## 最佳实践

### 1. 错误处理
- 添加Try-Catch节点处理网络错误
- 设置重试机制
- 记录错误日志

### 2. 内容去重
```javascript
// 检查是否已存在相同标题的文章
const existingTitles = ['已存在的标题1', '已存在的标题2'];
const isDuplicate = existingTitles.includes(item.json.title);

if (isDuplicate) {
  return []; // 跳过重复内容
}
```

### 3. 内容质量检查
```javascript
// 检查内容长度和质量
const content = item.json.cleaned_content;
const minLength = 100;
const maxLength = 50000;

if (content.length < minLength || content.length > maxLength) {
  return []; // 跳过质量不合格的内容
}
```

### 4. 定时执行
- 设置合理的时间间隔（如每小时或每天）
- 避免过于频繁的请求
- 考虑目标网站的robots.txt

## 监控和通知

### 1. 成功通知
```javascript
// 发送成功通知到Slack
const message = `✅ 成功抓取新文章: ${item.json.title}\n链接: ${item.json.source_url}`;
```

### 2. 错误通知
```javascript
// 发送错误通知
const errorMessage = `❌ 抓取失败: ${item.json.url}\n错误: ${item.json.error}`;
```

## 性能优化

### 1. 并发控制
- 限制同时进行的请求数量
- 使用队列处理大量URL

### 2. 缓存机制
- 缓存已处理的内容
- 避免重复处理相同URL

### 3. 资源管理
- 定期清理临时文件
- 监控内存使用情况

## 总结

通过以上优化，您的n8n工作流将能够：
- 更准确地抓取内容
- 自动清理和格式化
- 提取有用的元数据
- 无缝集成到GitHub
- 提供监控和通知

这将大大减少手动处理的工作量，提高内容更新的效率。 