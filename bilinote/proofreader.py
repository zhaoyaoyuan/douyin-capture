"""
BiliNote 轻度校对模块
- 错别字修正
- 标点补全
- 口头禅去除
"""

import re


# 常见同音错别字映射（30+条）
TYPO_CORRECTIONS = {
    # 股票领域
    '涨厅版': '涨停板',
    '装家': '庄家',
    '标地': '标的',
    '行秦': '行情',
    '女士不爽': '屡试不爽',
    '手序': '手续',
    '平苔': '平台',
    '做手': '做庄',
    '做T': '做T',
    '打板': '打板',
    '翘板': '撬板',
    '拉生': '拉升',
    '砸盘': '砸盘',
    '洗盘': '洗盘',
    '出货': '出货',

    # 通用领域
    '水到去成': '水到渠成',
    '言归正在': '言归正传',
    '知根之': '殊不知',
    '必进': '毕竟',
    '精典': '经典',
    '精点': '经典',
    '即然': '既然',
    '既使': '即使',
    '在说': '再说',
    '在次': '再次',
    '作做': '做作',
    '坐位': '座位',
    '坐位': '座位',
    '坐位': '座位',

    # 常见错误
    '的话': '的话',  # 正确，但可能冗余
}


# 口头禅和填充词
FILLER_WORDS = [
    '嗯', '哦', '啊', '呃', '哎', '唉',
    '那个', '这个', '然后', '那么', '就是',
    '就是说', '对吧', '知道吧', '怎么说呢',
    '对吧', '是吧', '嗯啊', '那个那个',
    '反正', '其实', '基本上', '大概',
    '差不多', '可能', '也许', '应该',
    '我觉得', '我认为', '我想',
    '呢', '嘛', '呀', '哟',
]


def fix_typos(text: str) -> str:
    """修正常见错别字"""
    result = text
    for typo, correct in TYPO_CORRECTIONS.items():
        # 使用词边界匹配，避免替换包含关系
        pattern = r'(?<!\w)' + re.escape(typo) + r'(?!\w)'
        result = re.sub(pattern, correct, result)
    return result


def remove_fillers(text: str) -> str:
    """去除口头禅和填充词"""
    result = text

    # 优先处理长词
    sorted_fillers = sorted(FILLER_WORDS, key=len, reverse=True)

    for filler in sorted_fillers:
        # 替换填充词为空格（使用单词边界）
        result = re.sub(r'\b' + re.escape(filler) + r'\b', ' ', result)
        # 也处理连续的独立填充词
        result = re.sub(r'^' + re.escape(filler) + r'\b', ' ', result)
        result = re.sub(r'\b' + re.escape(filler) + r'$', ' ', result)

    # 清理多余空格
    result = re.sub(r'\s+', ' ', result).strip()
    return result


def add_punctuation(text: str) -> str:
    """智能补全标点符号"""
    result = text.strip()

    # 如果是空字符串，直接返回
    if not result:
        return result

    # 确保结尾有标点
    if result[-1] not in '。！？.?!':
        # 疑问句判断
        question_words = ['什么', '为什么', '怎么', '如何', '哪里', '谁', '吗', '呢', '?']
        is_question = any(w in result[-10:] for w in question_words)

        if is_question:
            result += '？'
        else:
            result += '。'

    # 连续标点去重
    result = re.sub(r'([。！？])\1+', r'\1', result)

    return result


def light_proofread(text: str) -> str:
    """
    轻度校对主函数

    执行顺序：
    1. 去除口头禅和填充词
    2. 修正常见错别字
    3. 智能补全标点
    4. 清理多余空格

    Args:
        text: 原始文本

    Returns:
        校对后的文本
    """
    if not text or not text.strip():
        return text

    result = text

    # 1. 去除填充词
    result = remove_fillers(result)

    # 2. 修正错别字
    result = fix_typos(result)

    # 3. 补全标点
    result = add_punctuation(result)

    # 4. 清理多余空格
    result = re.sub(r'\s+', ' ', result).strip()

    return result


def split_sentences(text: str) -> list:
    """
    智能分句

    将长文本按语义拆分成短句
    按句号、问号、感叹号、逗号（作为分句标记
    """
    # 先标准化标点
    text = text.replace('？', '。').replace('！', '。').replace('!', '.').replace('?', '.')

    # 按句号拆分
    sentences = re.split(r'[。.]', text)

    # 过滤空句
    sentences = [s.strip() for s in sentences if s.strip()]

    return sentences
