# Markdown内容优化指南

## 概述

本指南将帮助您优化从其他网站抓取的markdown内容，使其在您的Hugo网站中显示更加优美和专业。

## 优化步骤

### 1. 添加Front Matter

每篇文章都需要添加Hugo的front matter，包含以下信息：

```yaml
---
title: "文章标题"
date: 2025-01-27
description: "文章描述 - 简短的中文描述"
tags: ["tag1", "tag2", "tag3"]
categories: ["category1", "category2"]
author: "原作者姓名"
draft: false
---
```

### 2. 内容清理

#### 删除不需要的元素：
- 原网站的导航链接（如"Skip to main content"）
- 评论部分
- 原网站的标签链接
- "Add new comment"等交互元素
- 多余的HTML标签

#### 优化格式：
- 统一引用格式
- 清理多余的空白行
- 确保图片链接正常显示
- 优化标题层级

### 3. 翻译和本地化

#### 可选步骤：
- 将英文内容翻译为中文
- 调整文化相关的引用和例子
- 本地化链接和资源

### 4. 添加元信息

在文章末尾添加：
```
---

*原文作者：[原作者] | 翻译和重新排版*
```

## 使用自动化脚本

### 使用Python清理脚本

1. 将抓取的原始内容保存为文件
2. 运行清理脚本：

```bash
python scripts/clean-markdown.py raw-content.md cleaned-content.md "文章标题" "文章描述"
```

### 使用Hugo模板

1. 使用提供的模板创建新文章：

```bash
hugo new posts/your-article.md
```

2. 将清理后的内容粘贴到模板中

## 最佳实践

### 1. 图片处理
- 确保图片链接可以正常访问
- 考虑下载图片到本地`static/images/`目录
- 添加适当的alt文本

### 2. 链接处理
- 保留原文链接作为参考
- 检查链接是否仍然有效
- 考虑添加本地化链接

### 3. 格式统一
- 使用一致的标题层级
- 统一引用和代码块格式
- 保持段落间距一致

### 4. SEO优化
- 添加有意义的描述
- 使用相关的标签和分类
- 确保标题具有描述性

## 示例

### 原始内容（抓取）
```markdown
[Skip to main content](https://example.com)

# Article Title

Some content here...

[Add new comment](https://example.com/comment)

## Comments

User comment here...
```

### 优化后内容
```markdown
---
title: "文章标题"
date: 2025-01-27
description: "关于某个主题的深入分析"
tags: ["technology", "analysis"]
categories: ["tech"]
author: "原作者"
draft: false
---

# 文章标题

一些内容在这里...

## 延伸阅读

- [相关链接1](https://example.com)
- [相关链接2](https://example.com)

---

*原文作者：原作者 | 翻译和重新排版*
```

## 常见问题

### Q: 如何处理复杂的HTML内容？
A: 使用脚本清理HTML标签，保留必要的markdown格式。

### Q: 图片链接失效怎么办？
A: 下载图片到本地，或寻找替代图片源。

### Q: 如何保持原文的引用格式？
A: 使用markdown的引用语法（>）重新格式化。

### Q: 是否需要翻译所有内容？
A: 根据您的网站定位决定，可以保留原文并提供翻译。

## 工具推荐

1. **在线Markdown编辑器**：Typora, Obsidian
2. **文本处理工具**：VS Code with Markdown extensions
3. **图片处理**：ImageOptim, TinyPNG
4. **翻译工具**：DeepL, Google Translate

## 总结

通过遵循这些步骤，您可以将抓取的markdown内容转换为适合您Hugo网站的高质量文章。记住，质量比数量更重要，花时间优化每篇文章将带来更好的用户体验。 