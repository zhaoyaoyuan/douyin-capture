# BiliNote 视频笔记生成器 v2.3.0

基于 BiliNote 开源项目的提示词工程和工作流构建，支持 9 种笔记风格和 4 种输出格式。

## 功能特性

- 🎯 **9种笔记风格**：精简、详细、学术、教程、小红书、生活向、任务导向、商业、会议纪要
- 📑 **4种输出格式**：目录(TOC)、原片跳转、截图标记、AI总结
- 🖼️ **多模态理解**：关键帧提取 + 智能位置推理
- ⏱️ **时间戳精确定位**：`*Content-[mm:ss]` 章节跳转
- 🧹 **轻度校对**：错别字修正、标点补全、口头禅去除

## 快速开始

### Skill 调用方式（推荐）

在 Claude Code 中直接使用 `/bilinote` 命令：

```
# 生成默认风格（详细 + 原片跳转 + AI总结）
/bilinote "视频文件.mp4"

# 指定风格和格式
/bilinote "视频文件.mp4" --style detailed --format link screenshot summary

# 多模态理解（提取画面）
/bilinote "视频文件.mp4" --multimodal
```

### 直接调用 Python

```bash
python3.13 ~/.claude/skills/bilinote/generate.py "视频文件.mp4"
```

## 笔记风格说明

| 风格 | 说明 | 适用场景 |
|-----|------|---------|
| `minimal` | 精简，仅保留核心观点 | 快速浏览 |
| `detailed` | 详细，完整记录所有内容 | 学习、课程 |
| `academic` | 学术风格，正式结构化 | 学术报告、论文 |
| `tutorial` | 教程风格，步骤清晰 | 技术教程、操作演示 |
| `xiaohongshu` | 小红书爆款风格 | 生活分享、种草 |
| `life_journal` | 生活向，情感化表达 | 生活记录、Vlog |
| `task_oriented` | 任务导向，行动项清晰 | 工作安排、待办 |
| `business` | 商业风格，正式精准 | 商业报告、分析 |
| `meeting_minutes` | 会议纪要 | 会议记录 |

## 输出格式说明

| 格式 | 说明 |
|-----|------|
| `toc` | 自动生成目录 |
| `link` | 每个章节标题后添加时间戳标记 `*Content-[mm:ss]` |
| `screenshot` | 在需要视觉辅助的位置插入截图标记 `*Screenshot-[mm:ss]` |
| `summary` | 在笔记末尾添加 AI 总结 |

## 常用组合

```
# 学习课程 - 详细记录 + 原片跳转 + 截图 + 总结
/bilinote "课程.mp4" --style detailed --format link screenshot summary

# 会议记录 - 会议纪要风格
/bilinote "会议.mp4" --style meeting_minutes --format toc summary

# 教程视频 - 教程风格 + 原片跳转 + 截图
/bilinote "教程.mp4" --style tutorial --format link screenshot

# 生活 Vlog - 小红书风格
/bilinote "vlog.mp4" --style xiaohongshu
```

## 环境要求

- Python 3.13+
- ffmpeg (`brew install ffmpeg`)
- openai-whisper（自动安装）

## OpenAI API 配置（可选）

配置后可使用 GPT 进行智能整理：

```bash
export OPENAI_API_KEY="your-api-key"
```

未配置时自动降级为本地生成模式。

## 输出目录

```
笔记同步助手/
└── 2026-05-19/
    ├── 视频名称.md           # 结构化笔记
    ├── audio/
    │   └── 视频名称.mp3      # 提取的音频文件
    └── images/
        ├── 视频名称_frame_000.jpg  # 关键帧截图
        └── ...
```

## 与 parse-video Skill 的区别

| 特性 | parse-video | bilinote |
|-----|-------------|----------|
| 目标 | 通用转写 + 基础整理 | **专业 AI 笔记生成** |
| 风格支持 | 1种 | **9种专业风格** |
| 格式选项 | 无 | **4种可选格式** |
| 多模态 | 基础截图 | **智能截图标记 + 位置推理** |
| 提示词工程 | 基础 | **BiliNote 专业级系统** |
| 输出结构 | 固定 5 部分 | **灵活 Markdown 结构** |

**使用建议**：
- 快速转写用 `parse-video`
- 需要高质量专业笔记用 `bilinote`

## 项目来源

基于 BiliNote 开源项目 v2.3.0 的提示词工程和工作流重构：

- GitHub: https://github.com/JefferyHcool/BiliNote
- 官方网站: https://www.bilinote.app
