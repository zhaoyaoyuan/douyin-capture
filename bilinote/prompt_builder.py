"""
BiliNote 动态提示词构建器
基于 BiliNote 开源项目 v2.3.0
"""

from prompt import BASE_PROMPT, LINK_PROMPT, AI_SUM_PROMPT, SCREENSHOT_PROMPT, TOC_PROMPT


# 笔记风格映射
STYLE_FORMATS = {
    'minimal': '''
1. **精简信息**: 仅记录最重要的核心观点和结论，简洁明了，去掉所有冗余。
只保留最关键的 3-5 个要点。
''',

    'detailed': '''
2. **详细记录**: 包含完整的内容和每个部分的详细讨论。需要尽可能多的记录视频内容，最好详细的笔记，不要遗漏任何重要信息。
''',

    'academic': '''
3. **学术风格**: 适合学术报告，正式且结构化。
- 使用严谨的学术用语
- 分章节清晰论述
- 逻辑层次分明
- 引用准确规范
''',

    'tutorial': '''
4. **教程笔记**: 尽可能详细的记录教程，特别是关键点和重要的结论步骤。
- 分步骤清晰说明
- 突出重点注意事项
- 标记易错点
- 保留所有代码和命令
- 记录操作的先后顺序
''',

    'xiaohongshu': '''
5. **小红书风格**:

### 擅长使用下面的爆款关键词：
好用到哭，大数据，教科书般，小白必看，宝藏，绝绝子神器，都给我冲，划重点，笑不活了，YYDS，秘方，我不允许，压箱底，建议收藏，停止摆烂，上天在提醒你，挑战全网，手把手，揭秘，普通女生，沉浸式，有手就能做，吹爆，好用哭了，搞钱必看，狠狠搞钱，打工人，吐血整理，家人们，隐藏，高级感，治愈，破防了，万万没想到，爆款，永远可以相信，被夸爆，手残党必备，正确姿势

### 采用二极管标题法创作标题：
- 正面刺激法: 产品或方法 + 只需1秒（短期） + 便可开挂（逆天效果）
- 负面刺激法: 你不XXX + 绝对会后悔（天大损失） +（紧迫感）
利用人们厌恶损失和负面偏误的心理

### 写作技巧
1. 使用惊叹号、省略号等标点符号增强表达力，营造紧迫感和惊喜感。
2. **使用emoji表情符号，来增加文字的活力**
3. 采用具有挑战性和悬念的表述，引发好奇心
4. 融入热点话题和实用工具，提高文章的实用性和时效性
5. 描述具体的成果和效果，强调标题中的关键词，使其更具吸引力
6. 使用吸引人的标题
''',

    'life_journal': '''
6. **生活向**: 记录个人生活感悟，情感化表达。
- 温暖真诚的语气
- 记录真实感受
- 适当抒情
- 保持亲切感
''',

    'task_oriented': '''
7. **任务导向**: 强调任务、目标，适合工作和待办事项。
- 清晰列出待办事项
- 标注优先级
- 记录截止时间
- 明确责任人和行动项
- 使用 ✅ ⏰ 🔴 🟡 🟢 等标记状态
''',

    'business': '''
8. **商业风格**: 适合商业报告，正式且精准。
- 数据驱动表述
- 专业商务用语
- 结构化呈现
- 重点突出 ROI 和收益
''',

    'meeting_minutes': '''
9. **会议纪要**: 适合商业报告、会议纪要，正式且精准。
- 会议基本信息（时间、地点、参会人）
- 会议议题
- 讨论要点
- 决议事项
- 行动项（责任人 + 截止时间）
- 待跟进事项
'''
}


# 格式映射
FORMAT_MAP = {
    'toc': TOC_PROMPT,
    'link': LINK_PROMPT,
    'screenshot': SCREENSHOT_PROMPT,
    'summary': AI_SUM_PROMPT,
}


def build_prompt(
    video_title: str,
    segment_text: str,
    tags: str = '',
    style: str = None,
    formats: list = None,
    extras: str = None
) -> str:
    """
    构建完整的 BiliNote 风格提示词

    Args:
        video_title: 视频标题
        segment_text: 分段转录文本（带时间戳）
        tags: 视频标签
        style: 笔记风格（minimal, detailed, academic, tutorial, xiaohongshu, life_journal, task_oriented, business, meeting_minutes）
        formats: 输出格式列表（toc, link, screenshot, summary）
        extras: 额外的自定义提示词

    Returns:
        完整的提示词字符串
    """
    # 基础提示词
    prompt = BASE_PROMPT.format(
        video_title=video_title,
        segment_text=segment_text,
        tags=tags or '无'
    )

    # 添加格式选项
    if formats:
        for fmt in formats:
            if fmt in FORMAT_MAP:
                prompt += '\n' + FORMAT_MAP[fmt]

    # 添加风格选项
    if style and style in STYLE_FORMATS:
        prompt += '\n' + STYLE_FORMATS[style]

    # 添加额外提示词
    if extras:
        prompt += f'\n\n额外要求：\n{extras}\n'

    return prompt


def get_available_styles() -> list:
    """获取所有可用的笔记风格"""
    return list(STYLE_FORMATS.keys())


def get_available_formats() -> list:
    """获取所有可用的输出格式"""
    return list(FORMAT_MAP.keys())


def get_style_info(style: str) -> dict:
    """获取指定风格的详细信息"""
    style_names = {
        'minimal': '精简',
        'detailed': '详细',
        'academic': '学术',
        'tutorial': '教程',
        'xiaohongshu': '小红书',
        'life_journal': '生活向',
        'task_oriented': '任务导向',
        'business': '商业',
        'meeting_minutes': '会议纪要',
    }
    return {
        'key': style,
        'name': style_names.get(style, style),
        'description': STYLE_FORMATS.get(style, '')
    }
