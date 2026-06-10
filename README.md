# 🎬 视频内容提取工具集

两个可移植的 Claude Code Skills，用于视频内容提取和笔记生成。

## 📦 包含的 Skills

| Skill | 功能 | 适用场景 |
|-------|------|----------|
| **bilinote** | 视频笔记生成器 | 将视频转为结构化笔记，支持 9 种风格 |
| **douyin-content-capture** | 抖音内容提取 | 下载抖音视频/图文，提取文案 |

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/YOUR_USERNAME/douyin-capture.git
cd douyin-capture
```

### 2. 配置环境

**重要：这两个 Skills 不提供默认输出目录，必须手动配置。**

#### bilinote 配置

```bash
cp bilinote/.env.example bilinote/.env
# 编辑 .env 文件，设置输出目录
```

```env
BILINOTE_OUTPUT_DIR=~/Documents/视频笔记
```

#### douyin-content-capture 配置

```bash
# 运行依赖检查（会自动创建 .env 并提示配置）
bash douyin-content-capture/scripts/check-deps.sh
```

```env
DOUYIN_OUTPUT_DIR=~/Downloads/douyin-captures
DOUYIN_WHISPER_MODEL=small
DOUYIN_WHISPER_DEVICE=auto
```

### 3. 开始使用

```bash
# 生成视频笔记
python3 bilinote/main.py "视频.mp4" --style detailed

# 提取抖音内容
bash douyin-content-capture/scripts/run.sh "https://v.douyin.com/xxxxx/"
```

---

## 📖 详细文档

### bilinote - 视频笔记生成器

将视频自动转写后，由 Claude 直接生成专业结构化笔记。

**功能特性：**
- 🎯 9 种笔记风格（精简、详细、学术、教程、小红书等）
- 📑 4 种输出格式（目录、原片跳转、截图标记、AI 总结）
- ⏱️ 时间戳精确定位
- 📸 智能截图标记
- 🧹 轻度校对（错别字修正、标点补全）

**使用示例：**

```bash
# 默认配置（详细风格 + 原片跳转 + 截图 + AI总结）
python3 bilinote/main.py "课程.mp4"

# 指定风格和格式
python3 bilinote/main.py "教程.mp4" --style tutorial --format link screenshot

# 小红书风格
python3 bilinote/main.py "vlog.mp4" --style xiaohongshu
```

**风格列表：**

| 风格 | 说明 |
|------|------|
| `minimal` | 精简，仅保留核心观点 |
| `detailed` | 详细，完整记录所有内容（默认） |
| `academic` | 学术风格，正式结构化 |
| `tutorial` | 教程风格，步骤清晰 |
| `xiaohongshu` | 小红书爆款风格 |
| `life_journal` | 生活向，情感化表达 |
| `task_oriented` | 任务导向，行动项清晰 |
| `business` | 商业风格，正式精准 |
| `meeting_minutes` | 会议纪要 |

---

### douyin-content-capture - 抖音内容提取

从抖音分享链接下载无水印视频、提取图文、语音转写文案。

**功能特性：**
- 🔗 支持多种链接格式（短链、长链、整段分享文案）
- 🎥 无水印视频下载
- 🎙️ 本地 Whisper 语音转写
- 📝 自动繁简转换
- 🖼️ 图文笔记提取

**使用示例：**

```bash
# 下载并转写视频
bash douyin-content-capture/scripts/run.sh "https://v.douyin.com/xxxxx/"

# 下载图文笔记
bash douyin-content-capture/scripts/run.sh "https://www.douyin.com/note/123456"

# 使用整段分享文案
bash douyin-content-capture/scripts/run.sh "7.48 复制打开抖音... https://v.douyin.com/xxxxx/"

# 指定 Whisper 模型
bash douyin-content-capture/scripts/run.sh --model base "https://v.douyin.com/xxxxx/"
```

**输出结构：**

```
输出目录/
└── 作品ID_标题/
    ├── video.mp4              # 无水印视频
    ├── audio.wav              # 提取的音频
    ├── transcript.txt         # 简体文案
    ├── transcript_segments.json  # 带时间戳的分段文案
    └── meta.json              # 作品元数据
```

---

## ⚙️ 环境变量

### bilinote

| 变量 | 说明 | 必填 |
|------|------|------|
| `BILINOTE_OUTPUT_DIR` | 笔记输出目录 | ✅ |

### douyin-content-capture

| 变量 | 说明 | 必填 |
|------|------|------|
| `DOUYIN_OUTPUT_DIR` | 下载输出目录 | ✅ |
| `DOUYIN_WHISPER_MODEL` | Whisper 模型大小 | 可选 |
| `DOUYIN_WHISPER_DEVICE` | 推理设备 | 可选 |
| `DOUYIN_REPO_URL` | 源码仓库地址 | 可选 |

---

## 🛠️ 环境要求

- Python 3.10+
- FFmpeg
- Git

**macOS 安装：**
```bash
brew install python ffmpeg git
```

**Ubuntu/Debian 安装：**
```bash
sudo apt update
sudo apt install python3 ffmpeg git
```

---

## 📁 项目结构

```
douyin-capture/
├── README.md                          # 本文件
├── .gitignore                         # Git 忽略文件
│
├── bilinote/                          # 视频笔记生成器
│   ├── SKILL.md                       # Skill 说明文档
│   ├── main.py                        # 入口脚本
│   ├── generate.py                    # 核心生成逻辑
│   ├── prompt_builder.py              # 提示词构建器
│   ├── prompt.py                      # 提示词模板
│   ├── proofreader.py                 # 轻度校对模块
│   └── .env.example                   # 环境配置示例
│
└── douyin-content-capture/            # 抖音内容提取
    ├── SKILL.md                       # Skill 说明文档
    ├── .env.example                   # 环境配置示例
    ├── scripts/
    │   ├── run.sh                     # 主运行脚本
    │   └── check-deps.sh              # 依赖检查脚本
    └── obsidian-content-capture-backend/  # 核心源码
        ├── script/
        │   ├── pipeline.py            # 主流水线
        │   ├── douyin_resolver.py     # 链接解析
        │   ├── transcriber.py         # 语音转写
        │   └── ...
        └── requirements.txt           # Python 依赖
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

## 🔗 相关项目

- [BiliNote](https://github.com/JefferyHcool/BiliNote) - bilinote 的灵感来源
- [obsidian-content-capture-backend](https://github.com/zhaoyaoyuan/obsidian-content-capture-backend) - douyin-content-capture 的核心源码
