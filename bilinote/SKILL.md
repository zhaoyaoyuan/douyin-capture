---
name: bilinote
description: "BiliNote 风格 AI 视频笔记生成器 - 基于 BiliNote 开源项目 v2.3.0 提示词工程。将视频自动转写后，由 Claude 直接生成专业结构化笔记。支持 9 种风格、4 种输出格式、原片时间戳跳转、智能截图标记。当用户说'生成视频笔记'、'把视频转成笔记'、'BiliNote 笔记'、'视频转文字带时间戳'时立即使用。"
version: "2.3.0"
author: "知识库系统 (基于 BiliNote 开源项目)"
tags: ["视频笔记", "多风格模板", "时间戳跳转", "关键帧提取", "轻度校对", "AI总结"]
---

# BiliNote 视频笔记生成 Skill v2.3.0

## 核心特性

| 功能 | 说明 |
|-----|------|
| 🎯 **9种笔记风格** | 精简、详细、学术、教程、小红书、生活向、任务导向、商业、会议纪要 |
| 📑 **4种输出格式** | 目录(TOC)、原片跳转、截图标记、AI总结 |
| ⏱️ **时间戳精确定位** | `*Content-[mm:ss]` 章节跳转标记 |
| 📸 **智能截图标记** | `*Screenshot-[mm:ss]` 在关键内容处自动标注 |
| 🧹 **轻度校对** | 30+错别字修正、标点补全、口头禅去除 |
| 🤖 **Claude 原生 AI** | 直接由 Claude 生成，无需外部 OpenAI API |

---

## 工作流程

```
用户输入视频路径
    ↓
【脚本预处理】
    ├─ 提取音频 (ffmpeg)
    ├─ Whisper 语音转文字
    ├─ 轻度校对（错别字/标点/口头禅）
    ├─ 按时间戳分段 (60秒/段)
    └─ 提取关键帧截图 (30秒/张)
    ↓
【Claude AI 生成】
    ├─ 读取 BiliNote 专业提示词模板
    ├─ 结合用户选择的风格和格式
    ├─ 智能分段并添加时间戳标记
    ├─ 推理截图插入位置
    └─ 生成结构化 Markdown 笔记
    ↓
保存到「笔记同步助手」目录
```

---

## 笔记风格说明

| 风格 | 说明 | 适用场景 |
|-----|------|---------|
| `minimal` | 精简，仅保留核心观点 | 快速浏览 |
| `detailed` | 详细，完整记录所有内容 | 学习、课程（默认） |
| `academic` | 学术风格，正式结构化 | 学术报告、论文 |
| `tutorial` | 教程风格，步骤清晰 | 技术教程、操作演示 |
| `xiaohongshu` | 小红书爆款风格 | 生活分享、种草 |
| `life_journal` | 生活向，情感化表达 | 生活记录、Vlog |
| `task_oriented` | 任务导向，行动项清晰 | 工作安排、待办 |
| `business` | 商业风格，正式精准 | 商业报告、分析 |
| `meeting_minutes` | 会议纪要 | 会议记录 |

---

## 输出格式说明

| 格式 | 说明 |
|-----|------|
| `toc` | 自动生成目录 |
| `link` | 每个章节标题后添加时间戳标记 `*Content-[mm:ss]` |
| `screenshot` | 在需要视觉辅助的位置插入截图标记 `*Screenshot-[mm:ss]` |
| `summary` | 在笔记末尾添加专业 AI 总结 |

---

## 使用方法

### Skill 调用方式

在 Claude Code 中直接使用 `/bilinote` 命令：

```
# 默认配置（详细风格 + 原片跳转 + 截图 + AI总结）
/bilinote "视频文件.mp4"

# 指定风格和格式
/bilinote "视频文件.mp4" --style tutorial --format link screenshot summary

# 启用多模态（提取更多关键帧）
/bilinote "视频文件.mp4" --multimodal
```

### 常用组合

```
# 学习课程 - 详细记录 + 原片跳转 + 截图 + 总结
/bilinote "课程.mp4" --style detailed --format link screenshot summary

# 会议记录 - 会议纪要风格
/bilinote "会议.mp4" --style meeting_minutes --format toc summary

# 教程视频 - 教程风格 + 原片跳转 + 截图
/bilinote "教程.mp4" --style tutorial --format link screenshot

# 生活 Vlog - 小红书风格
/bilinote "vlog.mp4" --style xiaohongshu

# 工作任务拆解
/bilinote "工作会议.mp4" --style task_oriented --format summary
```

### 可用参数

| 参数 | 说明 | 默认值 |
|-----|------|--------|
| `video_path` | 视频文件路径（必填） | - |
| `--style` | 笔记风格：minimal, detailed, academic, tutorial, xiaohongshu, life_journal, task_oriented, business, meeting_minutes | `detailed` |
| `--format / -f` | 输出格式（可多选）：toc, link, screenshot, summary | `link screenshot summary` |
| `--multimodal` | 启用多模态（提取更多关键帧） | 不启用 |
| `--model` | Whisper 模型大小：tiny, base, small, medium, large | `base` |
| `--tags` | 自定义标签（多个用空格分隔） | 无 |
| `--extras` | 额外的自定义提示词 | 无 |

---

## 输出目录结构

```
笔记同步助手/
└── 2026-05-19/
    ├── 视频名称.md               # 最终结构化笔记（Claude生成）
    ├── 视频名称_transcribe.txt   # 原始转写文本（带时间戳）
    ├── 视频名称_prompt.txt       # AI 提示词模板
    ├── 视频名称_metadata.json    # 元数据配置
    ├── audio/
    │   └── 视频名称.mp3          # 提取的音频文件
    └── images/
        ├── 视频名称_frame_000.jpg  # 关键帧截图
        ├── 视频名称_frame_001.jpg
        └── ...
```

---

## 环境依赖

- Python 3.13+
- ffmpeg (`brew install ffmpeg`)
- openai-whisper（自动安装）

---

## 与 parse-video Skill 的区别

| 特性 | parse-video | **bilinote** |
|-----|-------------|--------------|
| **目标定位** | 快速转写工具 | **专业 AI 笔记生成** |
| **风格模板** | 1种默认 | **9种专业风格** |
| **格式选项** | 无 | **4种可选格式组合** |
| **AI引擎** | 基础要点提取 | **Claude 原生智能** |
| **时间戳** | 分段显示 | **`*Content-[mm:ss]` 跳转标记** |
| **截图处理** | 全部提取 | **智能位置推理 + `*Screenshot-[mm:ss]`** |
| **输出结构** | 固定 5 部分 | **灵活 Markdown 章节结构** |

**使用建议**：
- 快速转写用 `parse-video`
- 需要高质量专业结构化笔记用 `bilinote`

---

## 核心提示词系统

基于 BiliNote 开源项目 v2.3.0 专业提示词工程：

### 基础提示词结构

```
【角色设定】专业笔记助手，擅长结构化整理
【语言要求】中文 + 专有名词保留英文
【视频信息】标题 + 标签
【输出规范】纯 Markdown + 不包裹代码块
【分段内容】带时间戳的完整转写
【生成原则】完整信息 + 去除无关 + 保留关键 + 可读布局
```

### 格式增强提示词

- **原片跳转**：每个主标题后添加 `*Content-[mm:ss]`
- **截图标记**：视觉演示/代码展示处插入 `*Screenshot-[mm:ss]`
- **AI 总结**：末尾添加专业精炼总结

---

## 项目来源

基于 BiliNote 开源项目 v2.3.0 重构：

- GitHub: https://github.com/JefferyHcool/BiliNote
- 官方网站: https://www.bilinote.app

**重构说明**：移除外部 OpenAI API 依赖，改为 Claude Code 原生 AI 处理，保持原有的提示词工程和专业输出质量。
