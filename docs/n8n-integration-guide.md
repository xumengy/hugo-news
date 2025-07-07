# n8n集成优化指南

## 概述

本指南将帮助您优化n8n工作流抓取的内容，使其能够自动处理并完美集成到您的Hugo网站中。

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装Python依赖
pip install requests beautifulsoup4 markdown

# 或者使用requirements.txt
pip install -r requirements.txt
```

### 2. 测试处理器

```bash
# 运行测试脚本
python scripts/test-n8n-processor.py
```

### 3. 处理单个文件

```bash
# 处理原始内容
python scripts/n8n-post-processor.py raw-content/your-article.md
```

## 📋 完整工作流程

### 步骤1: n8n工作流配置

#### 1.1 HTTP Request节点
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

#### 1.2 HTML Extract节点
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
    }
  }
}
```

#### 1.3 Function节点 - 内容清理
```javascript
// 清理HTML并转换为Markdown
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

#### 1.4 GitHub节点 - 上传原始内容
```json
{
  "operation": "create",
  "owner": "{{ $json.github_owner }}",
  "repository": "{{ $json.github_repo }}",
  "path": "raw-content/{{ $json.filename }}",
  "message": "添加原始内容: {{ $json.title }}",
  "content": "{{ $json.cleaned_content }}",
  "branch": "main"
}
```

### 步骤2: GitHub Actions自动处理

当n8n上传原始内容到`raw-content/`目录时，GitHub Actions会自动触发处理流程：

1. **内容清理**: 删除原网站元素
2. **元数据提取**: 自动提取标题、描述、标签
3. **图片下载**: 下载图片到本地
4. **格式优化**: 生成标准的Hugo front matter
5. **自动部署**: 构建并部署网站

### 步骤3: 手动处理（可选）

如果需要手动处理内容：

```bash
# 处理单个文件
python scripts/n8n-post-processor.py raw-content/article.md

# 批量处理
for file in raw-content/*.md; do
  python scripts/n8n-post-processor.py "$file"
done
```

## 🔧 配置选项

### 1. 自定义处理器配置

编辑`scripts/n8n-post-processor.py`中的配置：

```python
class N8nPostProcessor:
    def __init__(self, content_dir="content/posts", static_dir="static/images"):
        # 自定义目录路径
        self.content_dir = Path(content_dir)
        self.static_dir = Path(static_dir)
```

### 2. 自定义清理规则

在`clean_n8n_content`方法中添加自定义清理规则：

```python
def clean_n8n_content(self, content):
    # 添加自定义清理规则
    content = re.sub(r'你的自定义模式', '替换内容', content)
    return content
```

### 3. 自定义元数据提取

在`extract_metadata`方法中自定义元数据提取逻辑：

```python
def extract_metadata(self, content):
    # 自定义标签提取
    custom_tags = ['你的标签1', '你的标签2']
    # 自定义分类逻辑
    # ...
```

## 📊 监控和日志

### 1. 处理日志

处理器会输出详细的处理日志：

```
✅ 成功处理文章: content/posts/2025-01-27-文章标题.md
✅ 下载图片: image1.jpg
⚠️ 下载图片失败 https://example.com/image2.jpg: 连接超时
```

### 2. 错误处理

- 网络错误会自动重试
- 图片下载失败会保留原链接
- 格式错误会记录到日志

### 3. 成功通知

可以配置Slack或邮件通知：

```javascript
// n8n中的通知节点
const message = `✅ 成功处理新文章: ${item.json.title}\n链接: ${item.json.source_url}`;
```

## 🎯 最佳实践

### 1. 内容质量检查

```javascript
// 在n8n中添加质量检查
const content = item.json.cleaned_content;
const minLength = 100;
const maxLength = 50000;

if (content.length < minLength || content.length > maxLength) {
  return []; // 跳过质量不合格的内容
}
```

### 2. 去重机制

```javascript
// 检查是否已存在相同标题的文章
const existingTitles = ['已存在的标题1', '已存在的标题2'];
const isDuplicate = existingTitles.includes(item.json.title);

if (isDuplicate) {
  return []; // 跳过重复内容
}
```

### 3. 定时执行

- 设置合理的时间间隔（每小时或每天）
- 避免过于频繁的请求
- 考虑目标网站的robots.txt

### 4. 错误恢复

- 添加重试机制
- 记录错误日志
- 发送错误通知

## 🔍 故障排除

### 常见问题

1. **图片下载失败**
   - 检查网络连接
   - 验证图片URL是否有效
   - 检查目标网站的反爬虫设置

2. **内容格式错误**
   - 检查HTML结构
   - 调整选择器
   - 查看处理日志

3. **GitHub Actions失败**
   - 检查权限设置
   - 验证文件路径
   - 查看Actions日志

### 调试技巧

1. **启用详细日志**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **测试单个功能**
   ```bash
   python scripts/test-n8n-processor.py
   ```

3. **检查中间文件**
   - 查看`raw-content/`目录
   - 检查`processed-content/`目录
   - 验证生成的markdown文件

## 📈 性能优化

### 1. 并发处理

```python
# 使用多线程处理多个文件
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(process_file, file) for file in files]
```

### 2. 缓存机制

```python
# 缓存已处理的内容
import hashlib

def get_content_hash(content):
    return hashlib.md5(content.encode()).hexdigest()
```

### 3. 资源管理

- 定期清理临时文件
- 监控内存使用
- 优化图片大小

## 🎉 总结

通过这个完整的n8n集成方案，您可以：

- ✅ 自动化内容抓取和处理
- ✅ 保持内容质量和一致性
- ✅ 减少手动工作量
- ✅ 提高更新效率
- ✅ 获得详细的监控和日志

这将大大提升您的内容管理效率，让您的Hugo网站保持活跃和高质量的内容更新。 