#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试n8n内容处理器
演示如何使用n8n-post-processor.py处理抓取的内容
"""

import os
import sys
from pathlib import Path

# 添加scripts目录到Python路径
sys.path.append(str(Path(__file__).parent))

try:
    from n8n_post_processor import N8nPostProcessor
except ImportError:
    print("⚠️ 无法导入n8n_post_processor模块，请确保文件存在")
    sys.exit(1)

def create_test_content():
    """创建测试内容"""
    test_content = """[Skip to main content](https://example.com)

# 测试文章标题

这是一篇测试文章，用于演示n8n内容处理器的功能。

## 主要内容

这篇文章包含以下内容：

- 列表项目1
- 列表项目2
- 列表项目3

### 子标题

这里是一些**粗体文本**和*斜体文本*。

![测试图片](https://example.com/test-image.jpg)

> 这是一个引用块，包含重要信息。

## 延伸阅读

- [相关链接1](https://example.com/link1)
- [相关链接2](https://example.com/link2)

[Add new comment](https://example.com/comment)

## Comments

用户评论内容...

[technology](https://example.com/tags/technology)
[programming](https://example.com/tags/programming)
"""
    return test_content

def test_processor():
    """测试处理器功能"""
    print("🧪 开始测试n8n内容处理器...")
    
    # 创建处理器实例
    processor = N8nPostProcessor()
    
    # 创建测试内容
    test_content = create_test_content()
    
    # 保存测试内容到文件
    test_file = "raw-content/test-article.md"
    os.makedirs("raw-content", exist_ok=True)
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"📝 创建测试文件: {test_file}")
    
    # 处理内容
    try:
        output_path = processor.process_n8n_content(test_content, "test-output.md")
        print(f"✅ 处理成功: {output_path}")
        
        # 显示处理后的内容
        with open(output_path, 'r', encoding='utf-8') as f:
            processed_content = f.read()
        
        print("\n📄 处理后的内容预览:")
        print("=" * 50)
        print(processed_content[:500] + "...")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        return False

def test_image_download():
    """测试图片下载功能"""
    print("\n🖼️ 测试图片下载功能...")
    
    processor = N8nPostProcessor()
    
    # 测试图片URL（使用一个公开的测试图片）
    test_image_url = "https://via.placeholder.com/300x200/0066cc/ffffff?text=Test+Image"
    
    try:
        filename = processor.download_image(test_image_url)
        if filename:
            print(f"✅ 图片下载成功: {filename}")
            return True
        else:
            print("❌ 图片下载失败")
            return False
    except Exception as e:
        print(f"❌ 图片下载出错: {e}")
        return False

def test_metadata_extraction():
    """测试元数据提取功能"""
    print("\n📊 测试元数据提取功能...")
    
    processor = N8nPostProcessor()
    test_content = create_test_content()
    
    try:
        metadata = processor.extract_metadata(test_content)
        print("✅ 元数据提取成功:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")
        return True
    except Exception as e:
        print(f"❌ 元数据提取失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 n8n内容处理器测试套件")
    print("=" * 50)
    
    tests = [
        ("内容处理", test_processor),
        ("图片下载", test_image_download),
        ("元数据提取", test_metadata_extraction)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 运行测试: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append((test_name, False))
    
    # 显示测试结果
    print("\n📋 测试结果汇总:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！处理器工作正常。")
    else:
        print("⚠️ 部分测试失败，请检查配置。")

if __name__ == "__main__":
    main() 