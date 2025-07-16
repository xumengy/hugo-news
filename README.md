# 葡萄之家（my-news）

本项目是基于 [Hugo](https://gohugo.io/) 和 dream 主题的个人博客/资讯网站，支持自动化内容采集与发布，适合技术分享、生活记录、资讯聚合等多种用途。

## 主要特性
- 使用 Hugo 静态网站生成器，构建速度快，易于维护
- dream 主题，界面美观，支持暗色/亮色切换
- 支持 GitHub Actions 自动部署到 GitHub Pages
- 支持 n8n 工作流自动抓取内容并上传 Markdown 文件
- 响应式设计，适配 PC 和移动端

## 快速开始
1. **安装 Hugo**
   ```bash
   brew install hugo # Mac
   # 或参考 https://gohugo.io/getting-started/installing/
   ```
2. **克隆本仓库**
   ```bash
   git clone https://github.com/xumengy/hugo-news.git
   cd hugo-news
   ```
3. **本地预览**
   ```bash
   hugo server -D
   # 访问 http://localhost:1313
   ```
4. **添加/编辑内容**
   - 所有文章位于 `content/posts/` 目录，支持 Markdown 格式。
   - 可通过 n8n 自动推送内容，或手动添加。

## 自动部署到 GitHub Pages
- 本项目已配置 `.github/workflows/hugo.yml`，推送到 main 分支后会自动构建并部署到 GitHub Pages。
- 访问地址见 hugo.toml 中 `baseurl` 设置。

## n8n 自动化内容采集
- 支持通过 n8n 工作流自动抓取内容并上传到 GitHub 仓库。
- 相关脚本见 `scripts/` 目录。

## 主题与自定义
- 主题目录：`themes/dream/`
- 可在 `hugo.toml` 中自定义站点参数、主题配色、作者信息等。

## 参考
- [Hugo 官方文档](https://gohugo.io/documentation/)
- [dream 主题文档](https://github.com/g1eny0ung/hugo-theme-dream)

---
如有问题欢迎提 issue 或联系作者。 