#!/usr/bin/env python3
"""
BiliNote 风格 AI 视频笔记生成器 v2.3.0
基于 BiliNote 开源项目的提示词工程和工作流构建

【架构说明】
本脚本仅负责视频预处理（音频提取、Whisper转写、轻度校对、关键帧提取），
AI 智能笔记生成由 Claude Code 直接完成，不依赖外部 OpenAI API。

功能：
- 视频音频提取
- OpenAI Whisper 语音转文字
- 轻度校对（错别字、标点、口头禅去除）
- 按时间戳分段输出
- 关键帧截图提取
- 自动保存到「笔记同步助手」目录
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 导入本地模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prompt_builder import build_prompt, get_available_styles, get_available_formats
from proofreader import light_proofread

# Skill 目录
SKILL_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = SKILL_DIR / ".env"
ENV_EXAMPLE = SKILL_DIR / ".env.example"


def load_env():
    """加载 .env 配置文件"""
    if ENV_FILE.exists():
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.split('#')[0].strip()  # 去除行内注释
                    if key and value:
                        os.environ.setdefault(key, value)


def check_output_dir():
    """检查并配置输出目录"""
    # 先加载 .env
    load_env()
    
    # 检查环境变量
    output_dir = os.environ.get("BILINOTE_OUTPUT_DIR")
    
    if not output_dir:
        print("\n" + "=" * 60)
        print("❌ 错误: 未配置输出目录")
        print("=" * 60)
        print()
        print("BiliNote 需要指定笔记输出目录才能正常运行。")
        print()
        
        # 尝试创建 .env 文件
        if ENV_EXAMPLE.exists():
            print("检测到 .env.example 模板，正在创建 .env 配置文件...")
            import shutil
            shutil.copy(ENV_EXAMPLE, ENV_FILE)
            print(f"✅ 已创建: {ENV_FILE}")
        else:
            print("正在创建 .env 配置文件...")
            with open(ENV_FILE, 'w', encoding='utf-8') as f:
                f.write("# BiliNote 视频笔记生成器 - 环境配置\n")
                f.write("# 请修改下面的路径为你想要的笔记输出目录\n\n")
                f.write("BILINOTE_OUTPUT_DIR=~/Documents/笔记\n")
            print(f"✅ 已创建: {ENV_FILE}")
        
        print()
        print("📝 请按以下步骤配置:")
        print("-" * 40)
        print(f"1. 编辑配置文件: {ENV_FILE}")
        print("2. 修改 BILINOTE_OUTPUT_DIR 为你的笔记输出目录")
        print("3. 重新运行此命令")
        print("-" * 40)
        print()
        print("示例配置:")
        print("  BILINOTE_OUTPUT_DIR=~/Documents/我的笔记")
        print()
        sys.exit(1)
    
    # 展开 ~ 并返回 Path
    output_dir = os.path.expanduser(output_dir)
    return Path(output_dir)


# 初始化目录配置
BASE_DIR = check_output_dir()
NOTE_DIR = BASE_DIR / "笔记同步助手"


def get_video_duration(video_path: str) -> float:
    """获取视频时长（秒）"""
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())
    except:
        return 0


def format_time(seconds: float) -> str:
    """格式化时间 mm:ss"""
    mm = int(seconds // 60)
    ss = int(seconds % 60)
    return f"{mm:02d}:{ss:02d}"


def extract_audio(video_path: str, output_path: str) -> str:
    """使用 ffmpeg 提取音频"""
    print(f"正在提取音频...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = [
        'ffmpeg', '-i', video_path,
        '-vn', '-acodec', 'libmp3lame',
        '-q:a', '2', '-y',
        '-hide_banner', '-loglevel', 'error',
        output_path
    ]
    subprocess.run(cmd, check=True)
    return output_path


def transcribe_audio(audio_path: str, model_size: str = "base") -> dict:
    """使用 OpenAI Whisper 转写音频"""
    print(f"正在语音转写 (模型: {model_size})...")

    try:
        import whisper
    except ImportError:
        print("⚠️  未安装 whisper，尝试通过 pip 安装...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'openai-whisper'], check=True)
        import whisper

    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path, language="zh", verbose=False)

    return result


def build_segments_with_timestamps(transcribe_result: dict, chunk_seconds: int = 60) -> str:
    """构建带时间戳的分段文本"""
    segments = []
    current_segment = []
    current_start = 0

    for seg in transcribe_result['segments']:
        seg_start = seg['start']
        seg_text = seg['text'].strip()

        if not seg_text:
            continue

        # 轻度校对
        seg_text = light_proofread(seg_text)

        if seg_start - current_start >= chunk_seconds:
            # 保存当前分段
            if current_segment:
                text = ' '.join(current_segment)
                time_str = format_time(current_start)
                segments.append(f"{time_str} - {text}")

            current_segment = [seg_text]
            current_start = seg_start
        else:
            current_segment.append(seg_text)

    # 最后一段
    if current_segment:
        text = ' '.join(current_segment)
        time_str = format_time(current_start)
        segments.append(f"{time_str} - {text}")

    return '\n'.join(segments)


def extract_keyframes(video_path: str, output_dir: str, interval: int = 30) -> list:
    """按时间间隔提取关键帧截图"""
    print(f"正在提取关键帧截图 (间隔: {interval}秒)...")

    os.makedirs(output_dir, exist_ok=True)
    duration = get_video_duration(video_path)

    image_paths = []
    ts = 0
    idx = 0

    while ts < duration:
        output_path = os.path.join(output_dir, f"frame_{idx:03d}_{format_time(ts).replace(':', '_')}.jpg")

        cmd = [
            'ffmpeg', '-ss', str(ts), '-i', video_path,
            '-frames:v', '1', '-q:v', '2', '-y',
            '-hide_banner', '-loglevel', 'error',
            output_path
        ]

        try:
            subprocess.run(cmd, check=True)
            if os.path.exists(output_path):
                image_paths.append(output_path)
        except:
            pass

        ts += interval
        idx += 1

    print(f"已提取 {len(image_paths)} 张截图")
    return image_paths


def save_transcription_result(
    video_path: str,
    segment_text: str,
    audio_path: str = None,
    image_paths: list = None,
    style: str = None,
    formats: list = None
) -> tuple:
    """
    保存转写结果，仅保留最终产物（无中间文件）

    返回：(提示词文本, 笔记目录, 元数据)
    """
    today = datetime.now().strftime('%Y-%m-%d')
    video_name = Path(video_path).stem
    clean_name = video_name.replace('/', '_').replace('\\', '_').replace(' ', '_')

    # 日期目录
    date_dir = NOTE_DIR / today
    os.makedirs(date_dir, exist_ok=True)

    # 子目录
    audio_dir = date_dir / 'audio'
    images_dir = date_dir / 'images'
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    # 移动音频文件
    if audio_path and os.path.exists(audio_path):
        dest_audio = audio_dir / f"{clean_name}.mp3"
        os.rename(audio_path, dest_audio)
        audio_ref = f"audio/{clean_name}.mp3"
    else:
        audio_ref = None

    # 移动截图文件
    image_refs = []
    if image_paths:
        for idx, src_img in enumerate(image_paths):
            if os.path.exists(src_img):
                dest_img = images_dir / f"{clean_name}_frame_{idx:03d}.jpg"
                os.rename(src_img, dest_img)
                image_refs.append(f"images/{clean_name}_frame_{idx:03d}.jpg")

    # 元数据（仅内存使用，不保存文件）
    metadata = {
        'video_title': video_name,
        'style': style,
        'formats': formats,
        'tags': ['视频笔记', 'BiliNote'],
        'audio_path': audio_ref,
        'image_paths': image_refs,
        'output_dir': str(date_dir),
        'output_md': str(date_dir / f"{clean_name}.md")
    }

    # 构建提示词（仅内存使用，不保存文件）
    tags_str = ', '.join(metadata['tags'])
    prompt = build_prompt(
        video_title=video_name,
        segment_text=segment_text,
        tags=tags_str,
        style=style,
        formats=formats
    )

    print(f"\n✅ 预处理完成！")
    print(f"📁 输出目录: {date_dir}")
    print(f"🎯 风格: {style} | 格式: {', '.join(formats) if formats else '默认'}")

    return prompt, str(date_dir), metadata


def main():
    parser = argparse.ArgumentParser(description='BiliNote 风格 AI 视频笔记生成器')
    parser.add_argument('video_path', help='视频文件路径')
    parser.add_argument('--style', default='detailed',
                        choices=get_available_styles(),
                        help='笔记风格')
    parser.add_argument('--format', '-f', nargs='+', default=['link', 'screenshot', 'summary'],
                        choices=get_available_formats(),
                        help='输出格式（可多选：toc, link, screenshot, summary）')
    parser.add_argument('--multimodal', action='store_true', help='启用多模态（提取画面）')
    parser.add_argument('--model', default='base', help='Whisper 模型大小：tiny, base, small, medium, large')
    parser.add_argument('--tags', nargs='+', help='自定义标签')
    parser.add_argument('--extras', help='额外的自定义提示词')
    parser.add_argument('--json', action='store_true', help='仅输出 JSON 结果（供调用方使用）')

    args = parser.parse_args()

    # 检查视频文件
    if not os.path.exists(args.video_path):
        print(f"❌ 视频文件不存在: {args.video_path}")
        sys.exit(1)

    video_name = Path(args.video_path).stem

    if not args.json:
        print(f"\n🎬 BiliNote 视频笔记生成器 v2.3.0")
        print(f"{'=' * 50}")
        print(f"视频: {video_name}")
        print(f"风格: {args.style}")
        print(f"格式: {', '.join(args.format)}")
        print(f"多模态: {'是' if args.multimodal else '否'}")
        print(f"{'=' * 50}\n")

    # 创建临时目录
    import tempfile
    temp_dir = tempfile.mkdtemp(prefix='bilinote_')
    audio_path = os.path.join(temp_dir, 'audio.mp3')

    try:
        # 1. 提取音频
        extract_audio(args.video_path, audio_path)

        # 2. 语音转写
        transcribe_result = transcribe_audio(audio_path, args.model)

        # 3. 构建带时间戳的分段文本
        segment_text = build_segments_with_timestamps(transcribe_result, chunk_seconds=60)

        # 4. 提取关键帧（如果启用多模态或需要截图格式）
        image_paths = []
        if args.multimodal or 'screenshot' in args.format:
            image_paths = extract_keyframes(args.video_path, os.path.join(temp_dir, 'frames'), interval=30)

        # 5. 保存结果，输出提示词
        prompt, output_dir, metadata = save_transcription_result(
            video_path=args.video_path,
            segment_text=segment_text,
            audio_path=audio_path,
            image_paths=image_paths,
            style=args.style,
            formats=args.format
        )

        if args.json:
            # 机器可读格式输出
            result = {
                'success': True,
                'prompt': prompt,
                'output_dir': output_dir,
                'metadata': metadata
            }
            print(json.dumps(result, ensure_ascii=False))
        else:
            # 人类可读格式
            print(f"\n📋 下一步：Claude AI 将生成专业笔记...")
            print(f"\n{'=' * 50}")
            print("【提示词已准备就绪，Claude 将生成最终笔记】")
            print(f"{'=' * 50}\n")
            print("请稍候，AI 正在生成结构化笔记...")

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # 清理临时目录
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


if __name__ == '__main__':
    main()
