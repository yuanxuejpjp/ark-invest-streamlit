# 🚀 Streamlit Cloud 部署指南

## 方式一：通过 GitHub 部署（推荐）

### 步骤 1：创建 GitHub 仓库

1. 访问 https://github.com/new
2. 仓库名称填写：`ark-invest-streamlit-cn`
3. 选择 "Public"（公开）
4. 点击 "Create repository"

### 步骤 2：上传代码

在 `D:\vibe-coding\stock_advice\ark-invest-streamlit` 目录下执行：

```bash
# 添加远程仓库（将 YOUR_USERNAME 替换为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/ark-invest-streamlit-cn.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

或者使用 GitHub Desktop 上传。

### 步骤 3：部署到 Streamlit Cloud

1. 访问 https://share.streamlit.io
2. 使用 GitHub 账号登录
3. 点击 "New app"
4. 选择仓库：`YOUR_USERNAME/ark-invest-streamlit-cn`
5. 分支选择：`main`
6. 主文件路径：`app.py`
7. 点击 "Deploy"

等待几分钟，应用将自动部署完成！

---

## 方式二：手动 ZIP 上传（无需 Git）

如果无法使用 Git，可以使用以下方法：

### 步骤 1：打包文件

将以下文件打包为 `ark-invest-streamlit.zip`：
- `app.py`
- `requirements.txt`
- `.streamlit/config.toml`
- `README.md`

### 步骤 2：上传到 Streamlit Cloud

1. 访问 https://share.streamlit.io
2. 注册/登录账号
3. 点击 "New app" → "Deploy from existing repo"
4. 按照提示操作

---

## 📋 文件清单

项目包含以下文件：

```
ark-invest-streamlit/
├── app.py                 # 主应用代码（汉化版）
├── requirements.txt       # Python 依赖
├── README.md             # 项目说明
├── .gitignore            # Git 忽略文件
└── .streamlit/
    └── config.toml       # Streamlit 配置
```

---

## 🔧 依赖说明

应用依赖以下 Python 包（已在 requirements.txt 中列出）：

- `streamlit>=1.28.0` - Web 应用框架
- `pandas>=2.0.0` - 数据处理
- `requests>=2.31.0` - HTTP 请求
- `plotly>=5.18.0` - 数据可视化

---

## ⚠️ 部署后注意事项

1. **首次部署可能需要 2-3 分钟**
2. **应用 URL 格式**：`https://your-app-name.streamlit.app`
3. **免费版限制**：
   - 1 GB 内存
   - 资源会在不使用时休眠
   - 每月有一定计算时长限制

---

## 🐛 常见问题

### 问题 1：部署失败，提示依赖错误
**解决**：检查 requirements.txt 格式是否正确

### 问题 2：应用运行缓慢
**解决**：这是正常现象，免费版资源有限，首次访问可能需要唤醒服务

### 问题 3：数据显示为空
**解决**：API 服务可能暂时不可用，稍后重试即可

---

## 📞 需要帮助？

- Streamlit 文档：https://docs.streamlit.io
- 社区论坛：https://discuss.streamlit.io
