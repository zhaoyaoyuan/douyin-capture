---
name: douyin-content-capture
description: >-
  抖音内容提取工具 - 从抖音分享链接下载无水印视频、提取图文、语音转写文案。
  支持 v.douyin.com 短链、www.douyin.com/note|video 页面、整段分享文案。
  使用本地 faster-whisper 转写，无需登录 Cookie 或云端 API。
  当用户提到"下载抖音视频"、"抖音提取"、"抖音文案"、"抖音转写"、"抖音无水印"、
  "douyin download"、"抖音分享链接"、"提取抖音"等时使用。
---

# 抖音内容提取（本地流水线）

从抖音分享链接或整段分享文案，在本地完成解析、下载与文案提取。**无需登录 Cookie，无需云端语音 API。**

## 功能概述

| 能力 | 说明 |
|------|------|
| 链接支持 | `v.douyin.com` 短链、`www.douyin.com/note\|video`、`iesdouyin.com/share/...`、整段分享文案 |
| 视频处理 | 无水印下载 → FFmpeg 抽音频 → faster-whisper 转写 → zhconv 简体 |
| 图文处理 | 提取 `desc` 配文 + 下载配图（不跑 Whisper，不做图片 OCR） |
| 输出 | 每作品一个文件夹 `{输出目录}/{作品ID}_{标题}/` |

## 环境配置

### 下载目录

下载目录通过 `.env` 文件配置。首次使用时会自动创建。

**配置文件位置**: `${SKILL_DIR}/.env`

```bash
# 抖音内容下载目录（绝对路径）
DOUYIN_OUTPUT_DIR=~/Downloads/douyin-captures

# Whisper 模型: tiny / base / small / medium / large-v2 / large-v3
DOUYIN_WHISPER_MODEL=small

# 推理设备: auto / cpu / cuda
DOUYIN_WHISPER_DEVICE=auto
```

> `${SKILL_DIR}` 指本 skill 目录：`~/.agents/skills/douyin-content-capture`

### 系统依赖

| 依赖 | 用途 | 安装方式 |
|------|------|----------|
| **Python 3.10+** | 运行环境 | 系统自带或 `brew install python3` |
| **FFmpeg** | 视频抽音频 | macOS: `brew install ffmpeg` / Ubuntu: `sudo apt install ffmpeg` |

### Python 依赖

| 包 | 用途 |
|----|------|
| `requests` | 分享页请求、文件下载 |
| `faster-whisper` | 视频语音转写（首次需联网下载模型） |
| `zhconv` | 转写结果繁体→简体 |

## 使用流程

### Step 1: 检查依赖（首次使用或环境变更时）

运行依赖检查脚本，自动检测并安装缺失依赖：

```bash
bash ${SKILL_DIR}/scripts/check-deps.sh
```

该脚本会：
1. 检查 Python 3.10+ 是否可用
2. 检查 FFmpeg 是否已安装
3. 检查项目源码是否存在，不存在则自动 clone
4. 创建 venv 并安装 Python 依赖
5. 检查/创建 `.env` 配置文件

### Step 2: 执行下载/提取

```bash
bash ${SKILL_DIR}/scripts/run.sh "抖音分享链接"
```

#### 命令行参数

```bash
# 基本用法：下载并转写
bash ${SKILL_DIR}/scripts/run.sh "https://v.douyin.com/xxxxx/"

# 图文笔记
bash ${SKILL_DIR}/scripts/run.sh "https://www.douyin.com/note/7640701464617132402"

# 整段分享文案
bash ${SKILL_DIR}/scripts/run.sh "7.48 复制打开抖音… https://v.douyin.com/xxxxx/ …"

# 指定 Whisper 模型
bash ${SKILL_DIR}/scripts/run.sh --model base "https://v.douyin.com/xxxxx/"

# 指定输出目录（覆盖 .env 配置）
bash ${SKILL_DIR}/scripts/run.sh -o /path/to/output "分享链接"
```

#### 交互模式

```bash
# 无参数时从 stdin 读取链接
bash ${SKILL_DIR}/scripts/run.sh
# 粘贴链接后按 Ctrl+D 结束输入
```

### Step 3: 查看结果

输出目录结构：

**视频作品：**
```
{输出目录}/{作品ID}_{标题}/
├── video.mp4              # 无水印视频
├── audio.wav              # 提取的音频
├── download_url.txt       # 原始下载链接
├── transcript.txt         # 简体文案（含元数据头）
├── transcript_segments.json  # 带时间戳的分段文案
└── meta.json              # 作品元数据
```

**图文作品：**
```
{输出目录}/{作品ID}_{标题}/
├── images/01.jpg …        # 配图
├── image_urls.txt         # 图片链接列表
├── transcript.txt         # 简体文案
└── meta.json              # 作品元数据
```

`transcript.txt` 格式：
```
类型: 视频
标题: xxx
作者: xxx
作品ID: xxx
来源: https://v.douyin.com/xxxxx/
处理时间: 2024-01-01T00:00:00+08:00

--- 文案 ---

这里是转写后的简体文案内容...
```

## 在 Python 中调用

```python
import sys
sys.path.insert(0, "${SKILL_DIR}/obsidian-content-capture-backend")

from script.config import Settings
from script.douyin_resolver import resolve_douyin_share
from script.pipeline import process_douyin_share

# 仅解析元数据（不下载不转写）
meta = resolve_douyin_share("https://v.douyin.com/xxxxx/")
print(meta.title, meta.content_type, meta.download_url)

# 完整流水线
out_dir = process_douyin_share(
    "https://v.douyin.com/xxxxx/",
    settings=Settings(whisper_model="small"),
)
```

## 故障排查

| 现象 | 解决方案 |
|------|----------|
| 解析失败 | 检查链接有效性；`note`/`video` 页需能转到 `iesdouyin.com/share/...` |
| 视频转写很慢 | CPU + `small` 模型下长视频数分钟正常，可试 `tiny`/`base` 加速 |
| `float16 → float32` 警告 | CPU 上 ctranslate2 自动降级，可忽略 |
| 缺少 FFmpeg | `brew install ffmpeg` 或 `sudo apt install ffmpeg` |
| 缺少 Python 依赖 | 重新运行 `bash ${SKILL_DIR}/scripts/check-deps.sh` |
| Conda 环境冲突 | 确保使用 venv: `source ${SKILL_DIR}/obsidian-content-capture-backend/.venv/bin/activate` |

## 注意事项

- 仅供学习与研究，请遵守相关法律法规与平台规则
- 图文题本在图片中的文字不会自动识别（无 OCR）
- 首次视频转写会从 Hugging Face 下载 Whisper 模型（需联网，约 500MB）
- 项目源码位于 `${SKILL_DIR}/obsidian-content-capture-backend/`

## 源码参考

核心代码位于 `${SKILL_DIR}/obsidian-content-capture-backend/script/` 目录：

| 文件 | 功能 |
|------|------|
| `douyin_resolver.py` | 分享页解析、链接转换、SSR 数据提取 |
| `pipeline.py` | 主流水线（下载→抽音频→转写→保存） |
| `transcriber.py` | Whisper 语音转写 + 繁简转换 |
| `downloader.py` | 文件下载 |
| `audio_extractor.py` | FFmpeg 音频提取 |
| `config.py` | 配置数据类 |
| `main.py` | CLI 入口 |

完整项目文档见 `${SKILL_DIR}/obsidian-content-capture-backend/README.md`
