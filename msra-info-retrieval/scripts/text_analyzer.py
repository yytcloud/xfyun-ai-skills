# -*- coding: utf-8 -*-
"""
text_analyzer.py - 轻量级文本分析工具

功能：
  1. 关键句提取（基于句子重要性启发式算法）
  2. 实体识别（基于常见模式匹配：人名/地名/机构名/日期/数字）
  3. 关键词提取（基于词频统计）

仅使用 Python 标准库：re, json, sys, collections, math
不依赖任何第三方 NLP 库
"""

import re
import json
import sys
import collections
import math


# ============================================================
# 工具函数
# ============================================================

def split_sentences(text):
    """将文本拆分为句子列表，支持中英文标点。"""
    # 按中英文句号、问号、感叹号、分号分割
    sentences = re.split(r'(?<=[。！？；.!?;])\s*', text)
    # 过滤空句和过短的句子
    return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 2]


def is_chinese_char(char):
    """判断一个字符是否为中文字符。"""
    cp = ord(char)
    if (0x4E00 <= cp <= 0x9FFF or
        0x3400 <= cp <= 0x4DBF or
        0x20000 <= cp <= 0x2A6DF or
        0x2A700 <= cp <= 0x2B73F or
        0x2B740 <= cp <= 0x2B81F or
        0x2B820 <= cp <= 0x2CEAF or
        0xF900 <= cp <= 0xFAFF or
        0x2F800 <= cp <= 0x2FA1F):
        return True
    return False


def tokenize(text):
    """
    简单分词：对中文按字/词切分（基于常见双字词模式），
    对英文按空格和标点切分。
    返回词/词组列表。
    """
    tokens = []

    # 提取中文片段并做简单分词
    chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf]+')
    for match in chinese_pattern.finditer(text):
        segment = match.group()
        # 简单的双字词切分 + 单字回退
        i = 0
        while i < len(segment):
            if i + 2 <= len(segment):
                tokens.append(segment[i:i + 2])
                i += 2
            else:
                tokens.append(segment[i])
                i += 1

    # 提取英文单词
    english_words = re.findall(r'[a-zA-Z]{2,}', text)
    tokens.extend([w.lower() for w in english_words])

    return tokens


def remove_stopwords(tokens):
    """移除常见停用词，包括单字停用词和双字停用词组。"""
    stopwords = set([
        # 中文单字停用词
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都',
        '一', '上', '也', '很', '到', '说', '要', '去', '你', '会',
        '着', '看', '好', '这', '他', '她', '它', '们',
        '那', '被', '从', '把', '对', '与', '及', '等', '中', '或', '但',
        '而', '且', '所', '以', '为', '之', '其', '还', '又', '地', '得',
        '更', '让', '比', '向', '给', '做', '能', '来', '去', '过', '里',
        '后', '前', '下', '多', '少', '大', '小', '新', '老', '长',
        # 中文双字停用词/常见虚词组合
        '一个', '没有', '自己', '这个', '那个', '什么', '怎么', '如何',
        '可以', '因为', '所以', '如果', '虽然', '但是', '然后', '通过',
        '进行', '以及', '已经', '对于', '关于', '其中', '之间', '以上',
        '以下', '目前', '以来', '从而', '即使', '尽管', '不仅', '而且',
        '或者', '还是', '只是', '只有', '由于', '因此', '于是', '此外',
        '同时', '之后', '之前', '其他', '另外', '其中', '某些', '某个',
        '一种', '一些', '这些', '那些', '这样', '那样', '怎样', '如此',
        '方面', '问题', '情况', '时候', '地方', '工作', '需要', '可能',
        '应该', '能够', '开始', '出现', '具有', '存在', '属于', '包括',
        '涉及', '相关', '主要', '重要', '不同', '相同', '根据', '按照',
        '通过', '使用', '采用', '利用', '基于', '针对', '提出', '实现',
        '达到', '获得', '提高', '促进', '推动', '支持', '提供', '带来',
        # 常见双字虚词/介词/连词/副词（避免双字分词产生的噪音）
        '于2', '了由', '在医', '疗领', '域的', '率达', '到了', '为的',
        '月在', '年在', '是中', '是目', '的前', '的中', '的人', '的了',
        '一个', '我们', '他们', '她们', '你们', '这个', '那个', '什么',
        # 英文停用词
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'shall', 'to', 'of', 'in', 'for',
        'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'between', 'and', 'but', 'or',
        'not', 'no', 'nor', 'so', 'yet', 'both', 'either', 'neither', 'each',
        'every', 'all', 'any', 'few', 'more', 'most', 'other', 'some', 'such',
        'than', 'too', 'very', 'just', 'about', 'it', 'its', 'this', 'that',
        'these', 'those', 'i', 'me', 'my', 'we', 'our', 'you', 'your', 'he',
        'him', 'his', 'she', 'her', 'they', 'them', 'their', 'what', 'which',
        'who', 'whom', 'when', 'where', 'why', 'how',
    ])
    return [t for t in tokens if t not in stopwords and len(t) > 1]


# ============================================================
# 1. 关键句提取
# ============================================================

def extract_key_sentences(text, top_n=5):
    """
    基于句子重要性启发式算法提取关键句。

    评分维度：
    - 位置加分：段首/段尾的句子得分更高
    - 长度加分：句子长度适中（15-80字）得分更高
    - 关键词密度：包含更多高频关键词的句子得分更高
    - 指示词加分：包含"结论""因此""关键""重要""发现"等词的句子得分更高
    """
    sentences = split_sentences(text)
    if not sentences:
        return []

    total = len(sentences)

    # 计算全局词频
    all_tokens = tokenize(text)
    all_tokens = remove_stopwords(all_tokens)
    freq = collections.Counter(all_tokens)

    # 取高频词作为关键词
    top_keywords = set([w for w, _ in freq.most_common(30)])

    # 指示词列表
    indicator_words = [
        '结论', '因此', '关键', '重要', '发现', '表明', '结果显示',
        '研究发现', '证明了', '说明', '意味着', '核心', '主要',
        'significant', 'conclusion', 'result', 'finding', 'key', 'important',
        'demonstrate', 'show', 'evidence', 'critical', 'crucial',
    ]

    scored_sentences = []
    for idx, sent in enumerate(sentences):
        score = 0.0

        # 1. 位置加分（段首前20%和段尾后10%）
        pos_ratio = idx / max(total - 1, 1)
        if pos_ratio <= 0.2:
            score += 2.0 * (1 - pos_ratio / 0.2)
        elif pos_ratio >= 0.9:
            score += 1.5 * ((pos_ratio - 0.9) / 0.1)

        # 2. 长度加分（适中长度得分最高）
        sent_len = len(sent)
        if 15 <= sent_len <= 80:
            score += 2.0
        elif 5 <= sent_len < 15:
            score += 1.0
        elif 80 < sent_len <= 150:
            score += 1.0

        # 3. 关键词密度
        sent_tokens = tokenize(sent)
        sent_tokens = remove_stopwords(sent_tokens)
        if sent_tokens:
            keyword_count = sum(1 for t in sent_tokens if t in top_keywords)
            score += keyword_count * 0.5

        # 4. 指示词加分
        for iw in indicator_words:
            if iw in sent:
                score += 2.0
                break  # 每句最多加一次

        # 5. 包含数字的句子略加分（通常包含数据）
        if re.search(r'\d+\.?\d*', sent):
            score += 0.5

        scored_sentences.append({
            'sentence': sent,
            'score': round(score, 3),
            'index': idx
        })

    # 按得分降序排序，取 top_n
    scored_sentences.sort(key=lambda x: x['score'], reverse=True)
    result = scored_sentences[:top_n]

    # 按原文顺序返回
    result.sort(key=lambda x: x['index'])

    return result


# ============================================================
# 2. 实体识别（基于模式匹配）
# ============================================================

# 常见中国地名后缀
LOCATION_SUFFIXES = (
    '省', '市', '区', '县', '镇', '乡', '村', '岛', '山', '河', '湖', '海',
    '省', '自治区', '直辖市', '特别行政区', '州', '路', '街', '道',
    '广场', '公园', '机场', '港口', '高原', '盆地', '平原', '沙漠',
)

# 常见机构名后缀
ORG_SUFFIXES = (
    '大学', '学院', '研究院', '研究所', '研究中心', '实验室', '公司', '集团',
    '有限公司', '股份有限公司', '银行', '医院', '诊所', '部门', '委员会',
    '协会', '基金会', '组织', '机构', '政府', '部', '局', '署', '厅',
    '办公室', '处', '科', '馆', '院', '社', '台', '网', '报', '刊',
    'Inc', 'Corp', 'Ltd', 'LLC', 'Co.', 'Corporation', 'Company',
    'University', 'Institute', 'Laboratory', 'Hospital', 'Academy',
    'Association', 'Foundation', 'Committee', 'Ministry', 'Department',
    'Agency', 'Bureau', 'Organization',
)

# 常见中国人名姓氏（高频前100）
COMMON_SURNAMES = (
    '赵', '钱', '孙', '李', '周', '吴', '郑', '王', '冯', '陈',
    '褚', '卫', '蒋', '沈', '韩', '杨', '朱', '秦', '尤', '许',
    '何', '吕', '施', '张', '孔', '曹', '严', '华', '金', '魏',
    '陶', '姜', '戚', '谢', '邹', '喻', '柏', '水', '窦', '章',
    '云', '苏', '潘', '葛', '奚', '范', '彭', '郎', '鲁', '韦',
    '昌', '马', '苗', '凤', '花', '方', '俞', '任', '袁', '柳',
    '丰', '鲍', '史', '唐', '费', '廉', '岑', '薛', '雷', '贺',
    '倪', '汤', '滕', '殷', '罗', '毕', '郝', '邬', '安', '常',
    '乐', '于', '时', '傅', '皮', '齐', '康', '伍', '余', '元',
    '卜', '顾', '孟', '平', '黄', '和', '穆', '萧', '尹', '姚',
)


def recognize_entities(text):
    """
    基于常见模式匹配识别文本中的实体。

    识别类型：
    - PERSON: 人名（中文：姓氏+1-2字名；英文：首字母大写连续词）
    - LOCATION: 地名（中文：含地名后缀的词组）
    - ORGANIZATION: 机构名（含机构后缀的词组）
    - DATE: 日期（多种日期格式）
    - NUMBER: 数字（含百分号、货币等）
    - TERM: 领域术语（被引号或书名号包裹的内容）
    """
    entities = []

    # --- 日期识别 ---
    # 年月日格式：2024年3月15日 / 2024-03-15 / 2024/03/15
    date_patterns = [
        r'\d{4}年\d{1,2}月\d{1,2}日?',
        r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',
        r'\d{4}年',
        r'\d{1,2}月\d{1,2}日',
        r'(?:20|19)\d{2}[年\s]',
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
        r'[a-z]*\.?\s+\d{1,2},?\s+(?:20|19)\d{2}',
        r'(?:Q[1-4]\s*(?:20|19)\d{2})',
    ]
    for pattern in date_patterns:
        for match in re.finditer(pattern, text):
            entities.append({
                'text': match.group(),
                'type': 'DATE',
                'start': match.start(),
                'end': match.end()
            })

    # --- 数字识别 ---
    number_patterns = [
        r'\d+\.?\d*%',             # 百分比
        r'\d+\.?\d*(?:万|亿|千|百|十|元|美元|欧元|日元|英镑)',
        r'[$￥€£]\s*\d+\.?\d*',   # 货币
        r'\b\d+\.?\d*\b',          # 普通数字
    ]
    for pattern in number_patterns:
        for match in re.finditer(pattern, text):
            num_text = match.group()
            # 排除已经被识别为日期的数字
            is_date = any(
                e['type'] == 'DATE' and match.start() >= e['start'] and match.end() <= e['end']
                for e in entities
            )
            if not is_date and len(num_text) > 0:
                entities.append({
                    'text': num_text,
                    'type': 'NUMBER',
                    'start': match.start(),
                    'end': match.end()
                })

    # --- 机构名识别 ---
    for suffix in ORG_SUFFIXES:
        # 机构名：通常为 2-6 个中文字符 + 后缀（限制前缀长度避免过度匹配）
        org_pattern = re.compile(
            r'[\u4e00-\u9fff]{2,6}' + re.escape(suffix)
        )
        for match in org_pattern.finditer(text):
            entities.append({
                'text': match.group(),
                'type': 'ORGANIZATION',
                'start': match.start(),
                'end': match.end()
            })

    # --- 地名识别 ---
    for suffix in LOCATION_SUFFIXES:
        loc_pattern = re.compile(
            r'[\u4e00-\u9fff]{1,6}' + re.escape(suffix)
        )
        for match in loc_pattern.finditer(text):
            loc_text = match.group()
            # 排除已经被识别为机构名的
            is_org = any(
                e['type'] == 'ORGANIZATION' and match.start() >= e['start'] and match.end() <= e['end']
                for e in entities
            )
            if not is_org:
                entities.append({
                    'text': loc_text,
                    'type': 'LOCATION',
                    'start': match.start(),
                    'end': match.end()
                })

    # --- 中文人名识别 ---
    # 姓氏（1字）+ 名（1-2字），总长度 2-3 字
    # 常见虚词/介词/动词（不会出现在人名末尾）
    _NON_NAME_TAILS = set(
        '的在了有和就不人都一上也很到说要去你会着看好这他她它们'
        '那被从把对与及等中或但而且所以为之其还又地得更让比向'
        '给做能来过去里后前下多认为于由参加举办使将已将'
    )
    name_pattern = re.compile(
        r'(?:' + '|'.join(COMMON_SURNAMES) + r')[\u4e00-\u9fff]{1,2}'
    )
    for match in name_pattern.finditer(text):
        name_text = match.group()
        # 修正：如果末尾字符是虚词/动词，截掉最后一个字
        while len(name_text) > 2 and name_text[-1] in _NON_NAME_TAILS:
            name_text = name_text[:-1]
        if len(name_text) < 2:
            continue
        # 排除地名和机构名
        is_other = any(
            e['type'] in ('LOCATION', 'ORGANIZATION') and match.start() >= e['start'] and match.end() <= e['end']
            for e in entities
        )
        if not is_other:
            entities.append({
                'text': name_text,
                'type': 'PERSON',
                'start': match.start(),
                'end': match.start() + len(name_text)
            })

    # --- 英文人名识别（简单模式：两个以上首字母大写的连续词） ---
    eng_name_pattern = re.compile(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b')
    for match in eng_name_pattern.finditer(text):
        entities.append({
            'text': match.group(),
            'type': 'PERSON',
            'start': match.start(),
            'end': match.end()
        })

    # --- 领域术语识别（被引号、书名号包裹的内容） ---
    # 严格匹配：必须有成对的引号/书名号/尖括号/方括号包裹
    term_patterns = [
        r'["""]([^"""]{2,40})["""]',     # 双引号
        r"[''']([^''']{2,40})[''']",     # 单引号
        r'《([^《》]{2,40})》',           # 书名号
        r'〈([^〈〉]{2,40})〉',           # 单书名号
        r'\[([^\[\]]{2,40})\]',           # 方括号（英文）
        r'【([^【】]{2,40})】',           # 方括号（中文）
    ]
    for pattern in term_patterns:
        for match in re.finditer(pattern, text):
            entities.append({
                'text': match.group(),
                'type': 'TERM',
                'start': match.start(),
                'end': match.end()
            })

    # 按出现位置排序并去重（重叠实体保留较长的）
    entities.sort(key=lambda e: e['start'])
    deduped = []
    for ent in entities:
        # 检查是否与已保留的实体重叠
        overlap = False
        for prev in deduped:
            if ent['start'] < prev['end'] and ent['end'] > prev['start']:
                # 保留较长的实体
                if len(ent['text']) > len(prev['text']):
                    deduped.remove(prev)
                    deduped.append(ent)
                overlap = True
                break
        if not overlap:
            deduped.append(ent)

    return deduped


# ============================================================
# 3. 关键词提取
# ============================================================

def extract_keywords(text, top_n=15):
    """
    基于词频统计（TF）提取关键词。

    步骤：
    1. 分词
    2. 去停用词
    3. 统计词频
    4. 按词频降序返回 top_n 个关键词
    """
    tokens = tokenize(text)
    tokens = remove_stopwords(tokens)

    freq = collections.Counter(tokens)

    # 过滤单字符（中文单字通常信息量低）
    filtered = {k: v for k, v in freq.items() if len(k) >= 2 or (len(k) == 1 and is_chinese_char(k) and v >= 3)}

    # 排序取 top_n
    sorted_keywords = sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:top_n]

    total_words = sum(freq.values())
    result = []
    for word, count in sorted_keywords:
        result.append({
            'keyword': word,
            'count': count,
            'frequency': round(count / max(total_words, 1), 4)
        })

    return result


# ============================================================
# 主函数
# ============================================================

def analyze_text(text):
    """
    对输入文本进行综合分析，返回 JSON 格式结果。
    """
    result = {
        'key_sentences': extract_key_sentences(text),
        'entities': recognize_entities(text),
        'keywords': extract_keywords(text)
    }
    return result


def main():
    """命令行入口：从文件或标准输入读取文本，输出分析结果。"""
    if len(sys.argv) > 1:
        # 从文件读取
        filepath = sys.argv[1]
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            print(json.dumps({'error': 'File not found: ' + filepath}, ensure_ascii=False, indent=2))
            sys.exit(1)
        except Exception as e:
            print(json.dumps({'error': str(e)}, ensure_ascii=False, indent=2))
            sys.exit(1)
    else:
        # 从标准输入读取
        text = sys.stdin.read()

    if not text.strip():
        print(json.dumps({'error': 'Input text is empty'}, ensure_ascii=False, indent=2))
        sys.exit(1)

    result = analyze_text(text)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()