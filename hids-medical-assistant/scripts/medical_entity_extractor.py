# -*- coding: utf-8 -*-
"""
医疗实体提取工具 - 纯 Python 正则实现
用于从医疗文本中提取症状、诊断、药物、检查项目和数值指标。
仅依赖 Python 标准库（re, json, sys），无第三方依赖。

适用场景：HIDS 医疗健康智能理解与辅助决策 Skill
"""

import re
import json
import sys


# ============================================================
# 1. 医疗实体词典
# ============================================================

# 常见症状关键词
SYMPTOM_KEYWORDS = [
    "头晕", "头痛", "头痛", "胸闷", "胸痛", "心悸", "气短", "呼吸困难",
    "恶心", "呕吐", "腹痛", "腹泻", "便秘", "腹胀", "食欲不振",
    "乏力", "疲劳", "发热", "畏寒", "盗汗",
    "咳嗽", "咳痰", "喘息", "鼻塞", "流涕",
    "失眠", "嗜睡", "多梦", "焦虑", "抑郁",
    "关节疼痛", "腰痛", "背痛", "颈痛", "肢体麻木",
    "视物模糊", "耳鸣", "听力下降", "口干", "多饮", "多尿",
    "体重下降", "体重增加", "浮肿", "皮疹", "瘙痒",
    "尿频", "尿急", "尿痛", "血尿",
    "反酸", "烧心", "吞咽困难",
    "情绪低落", "注意力不集中", "记忆力减退",
]

# 常见诊断关键词（含疾病名称）
DIAGNOSIS_KEYWORDS = [
    "高血压", "高血压病", "糖尿病", "2型糖尿病", "1型糖尿病", "妊娠期糖尿病",
    "冠心病", "心绞痛", "心肌梗死", "心律失常", "房颤", "心衰", "心力衰竭",
    "脑卒中", "脑梗死", "脑出血", "短暂性脑缺血发作",
    "高脂血症", "高胆固醇血症", "高甘油三酯血症", "混合型高脂血症",
    "高尿酸血症", "痛风",
    "脂肪肝", "肝硬化", "肝炎", "乙型肝炎", "丙型肝炎",
    "慢性肾病", "肾功能不全", "肾衰竭", "尿毒症",
    "慢性阻塞性肺疾病", "COPD", "哮喘", "支气管炎", "肺炎",
    "甲状腺功能亢进", "甲亢", "甲状腺功能减退", "甲减", "甲状腺结节",
    "贫血", "缺铁性贫血",
    "骨质疏松", "骨关节炎", "类风湿关节炎",
    "消化性溃疡", "胃炎", "胃食管反流病",
    "焦虑症", "抑郁症", "睡眠障碍",
    "肿瘤", "恶性肿瘤", "肺癌", "胃癌", "肝癌", "结直肠癌", "乳腺癌",
    "前列腺增生", "前列腺炎",
    "代谢综合征", "肥胖症",
    "左心室肥厚", "心肌缺血", "心脏瓣膜病",
    "感染", "上呼吸道感染", "尿路感染",
]

# 常见药物关键词
MEDICATION_KEYWORDS = [
    "阿司匹林", "氯吡格雷", "替格瑞洛", "华法林", "利伐沙班", "达比加群",
    "氨氯地平", "硝苯地平", "非洛地平", "贝尼地平", "左氨氯地平",
    "缬沙坦", "氯沙坦", "厄贝沙坦", "替米沙坦", "坎地沙坦", "奥美沙坦",
    "依那普利", "贝那普利", "培哚普利", "雷米普利", "福辛普利",
    "美托洛尔", "比索洛尔", "阿替洛尔", "卡维地洛", "普萘洛尔",
    "氢氯噻嗪", "呋塞米", "螺内酯", "吲达帕胺",
    "二甲双胍", "格列美脲", "格列齐特", "阿卡波糖", "西格列汀",
    "达格列净", "恩格列净", "利拉鲁肽", "艾塞那肽", "胰岛素",
    "阿托伐他汀", "瑞舒伐他汀", "辛伐他汀", "普伐他汀", "匹伐他汀",
    "依折麦布", "非诺贝特", "吉非罗齐", "苯扎贝特",
    "奥美拉唑", "埃索美拉唑", "泮托拉唑", "雷贝拉唑",
    "别嘌醇", "非布司他", "苯溴马隆",
    "布洛芬", "对乙酰氨基酚", "塞来昔布", "双氯芬酸",
    "氨溴索", "右美沙芬", "沙丁胺醇", "布地奈德", "孟鲁司特",
    "头孢", "阿莫西林", "左氧氟沙星", "阿奇霉素", "莫西沙星",
    "甲硝唑", "氟康唑", "阿昔洛韦",
    "氯雷他定", "西替利嗪", "扑尔敏",
    "地西泮", "艾司唑仑", "唑吡坦", "佐匹克隆",
    "硝苯地平", "氨氯地平", "地高辛",
]

# 常见检查项目关键词
EXAM_KEYWORDS = [
    "血常规", "尿常规", "大便常规", "便隐血",
    "肝功能", "肾功能", "血脂", "血糖",
    "空腹血糖", "餐后血糖", "糖化血红蛋白", "HbA1c",
    "甲状腺功能", "甲功", "甲功五项", "甲功三项",
    "凝血功能", "D-二聚体",
    "肿瘤标志物", "CEA", "AFP", "CA125", "CA199", "PSA",
    "心电图", "ECG", "动态心电图", "Holter",
    "心脏超声", "超声心动图", " echocardiography",
    "胸部CT", "腹部CT", "头颅CT", "冠脉CTA",
    "胸部X光", "胸片",
    "腹部超声", "肝胆脾超声", "泌尿系超声", "甲状腺超声", "颈动脉超声",
    "胃镜", "肠镜", "支气管镜",
    "肝纤维化扫描",
    "24小时动态血压", "动态血压",
    "运动平板", "肺功能",
    "眼底检查", "骨密度",
    "血气分析", "血培养", "病原学检查",
    "脑电图", "肌电图",
    "冠脉造影",
    "MRI", "核磁共振", "头颅MRI", "腹部MRI",
    "PET-CT",
]

# 常见检验指标（用于数值指标提取）
LAB_INDICATORS = [
    # 血常规
    {"name": "白细胞", "name_en": "WBC", "unit": "x10^9/L", "ref_low": 3.5, "ref_high": 9.5},
    {"name": "红细胞", "name_en": "RBC", "unit": "x10^12/L", "ref_low": 4.3, "ref_high": 5.8},
    {"name": "血红蛋白", "name_en": "Hb", "unit": "g/L", "ref_low": 130, "ref_high": 175},
    {"name": "血小板", "name_en": "PLT", "unit": "x10^9/L", "ref_low": 125, "ref_high": 350},
    {"name": "红细胞压积", "name_en": "HCT", "unit": "%", "ref_low": 40.0, "ref_high": 50.0},
    {"name": "平均红细胞体积", "name_en": "MCV", "unit": "fL", "ref_low": 82, "ref_high": 100},
    {"name": "中性粒细胞比率", "name_en": "NEUT%", "unit": "%", "ref_low": 40.0, "ref_high": 75.0},
    {"name": "淋巴细胞比率", "name_en": "LYMPH%", "unit": "%", "ref_low": 20.0, "ref_high": 50.0},
    # 生化
    {"name": "谷丙转氨酶", "name_en": "ALT", "unit": "U/L", "ref_low": 9, "ref_high": 50},
    {"name": "谷草转氨酶", "name_en": "AST", "unit": "U/L", "ref_low": 15, "ref_high": 40},
    {"name": "总胆红素", "name_en": "TBIL", "unit": "μmol/L", "ref_low": 3.4, "ref_high": 17.1},
    {"name": "直接胆红素", "name_en": "DBIL", "unit": "μmol/L", "ref_low": 0, "ref_high": 6.8},
    {"name": "白蛋白", "name_en": "ALB", "unit": "g/L", "ref_low": 40, "ref_high": 55},
    {"name": "总蛋白", "name_en": "TP", "unit": "g/L", "ref_low": 65, "ref_high": 85},
    {"name": "尿素氮", "name_en": "BUN", "unit": "mmol/L", "ref_low": 2.6, "ref_high": 7.5},
    {"name": "肌酐", "name_en": "Cr", "unit": "μmol/L", "ref_low": 57, "ref_high": 111},
    {"name": "尿酸", "name_en": "UA", "unit": "μmol/L", "ref_low": 208, "ref_high": 428},
    {"name": "空腹血糖", "name_en": "FPG", "unit": "mmol/L", "ref_low": 3.9, "ref_high": 6.1},
    {"name": "糖化血红蛋白", "name_en": "HbA1c", "unit": "%", "ref_low": 4.0, "ref_high": 6.0},
    {"name": "总胆固醇", "name_en": "TC", "unit": "mmol/L", "ref_low": 2.8, "ref_high": 5.2},
    {"name": "甘油三酯", "name_en": "TG", "unit": "mmol/L", "ref_low": 0.3, "ref_high": 1.7},
    {"name": "高密度脂蛋白胆固醇", "name_en": "HDL-C", "unit": "mmol/L", "ref_low": 1.0, "ref_high": 1.9},
    {"name": "低密度脂蛋白胆固醇", "name_en": "LDL-C", "unit": "mmol/L", "ref_low": 0, "ref_high": 3.4},
    {"name": "肌钙蛋白I", "name_en": "cTnI", "unit": "ng/mL", "ref_low": 0, "ref_high": 0.04},
    {"name": "B型钠尿肽", "name_en": "BNP", "unit": "pg/mL", "ref_low": 0, "ref_high": 100},
    {"name": "钾", "name_en": "K", "unit": "mmol/L", "ref_low": 3.5, "ref_high": 5.3},
    {"name": "钠", "name_en": "Na", "unit": "mmol/L", "ref_low": 137, "ref_high": 147},
    {"name": "氯", "name_en": "Cl", "unit": "mmol/L", "ref_low": 99, "ref_high": 110},
    {"name": "钙", "name_en": "Ca", "unit": "mmol/L", "ref_low": 2.11, "ref_high": 2.52},
    {"name": "磷", "name_en": "P", "unit": "mmol/L", "ref_low": 0.81, "ref_high": 1.45},
    # 甲状腺
    {"name": "促甲状腺激素", "name_en": "TSH", "unit": "mIU/L", "ref_low": 0.27, "ref_high": 4.2},
    {"name": "游离T3", "name_en": "FT3", "unit": "pmol/L", "ref_low": 3.1, "ref_high": 6.8},
    {"name": "游离T4", "name_en": "FT4", "unit": "pmol/L", "ref_low": 12.0, "ref_high": 22.0},
    # 肿瘤标志物
    {"name": "癌胚抗原", "name_en": "CEA", "unit": "ng/mL", "ref_low": 0, "ref_high": 5.0},
    {"name": "甲胎蛋白", "name_en": "AFP", "unit": "ng/mL", "ref_low": 0, "ref_high": 7.0},
    {"name": "糖类抗原125", "name_en": "CA125", "unit": "U/mL", "ref_low": 0, "ref_high": 35.0},
    {"name": "糖类抗原199", "name_en": "CA199", "unit": "U/mL", "ref_low": 0, "ref_high": 37.0},
    # 凝血
    {"name": "凝血酶原时间", "name_en": "PT", "unit": "秒", "ref_low": 11.0, "ref_high": 14.5},
    {"name": "活化部分凝血活酶时间", "name_en": "APTT", "unit": "秒", "ref_low": 25.0, "ref_high": 35.0},
    {"name": "国际标准化比值", "name_en": "INR", "unit": "", "ref_low": 0.8, "ref_high": 1.2},
    # 血脂附加
    {"name": "载脂蛋白A1", "name_en": "ApoA1", "unit": "g/L", "ref_low": 1.0, "ref_high": 1.6},
    {"name": "载脂蛋白B", "name_en": "ApoB", "unit": "g/L", "ref_low": 0.6, "ref_high": 1.1},
    {"name": "脂蛋白a", "name_en": "Lp(a)", "unit": "mg/L", "ref_low": 0, "ref_high": 300},
]


# ============================================================
# 2. 实体提取函数
# ============================================================

def extract_symptoms(text):
    """
    从文本中提取症状实体。
    返回去重后的症状列表。
    """
    found = []
    for symptom in SYMPTOM_KEYWORDS:
        if symptom in text:
            found.append(symptom)
    # 去重并保持顺序
    seen = set()
    unique = []
    for s in found:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return unique


def extract_diagnoses(text):
    """
    从文本中提取诊断实体。
    返回去重后的诊断列表。
    """
    found = []
    for diag in DIAGNOSIS_KEYWORDS:
        if diag in text:
            found.append(diag)
    seen = set()
    unique = []
    for d in found:
        if d not in seen:
            seen.add(d)
            unique.append(d)
    return unique


def extract_medications(text):
    """
    从文本中提取药物实体。
    返回包含药物名称和剂量信息的列表。
    """
    results = []
    seen = set()

    for med in MEDICATION_KEYWORDS:
        if med in text and med not in seen:
            seen.add(med)

            # 尝试提取剂量信息：数字 + 单位(mg/g/ml/U/片/粒/支)
            # 在药物名称附近搜索
            pattern = re.compile(
                r'(?:' + re.escape(med) + r')'        # 药物名
                r'(?:\S*\s*){0,3}'                     # 允许中间有几个字符
                r'(\d+(?:\.\d+)?)'                     # 数字
                r'\s*(mg|g|ml|mL|U|片|粒|支|万单位)?',  # 单位
                re.IGNORECASE
            )
            dose_match = pattern.search(text)

            # 尝试提取用法：qd/tid/bid/qn 等
            usage_pattern = re.compile(
                r'(?:' + re.escape(med) + r')'
                r'(?:\S*\s*){0,6}'
                r'\b(qd|bid|tid|qid|qn|q8h|q12h|qod|prn|po|iv|im|ih|皮下|口服|静脉|肌肉)\b',
                re.IGNORECASE
            )
            usage_match = usage_pattern.search(text)

            entry = {"name": med}
            if dose_match:
                entry["dose"] = dose_match.group(1)
                if dose_match.group(2):
                    entry["unit"] = dose_match.group(2)
            if usage_match:
                entry["usage"] = usage_match.group(1).lower()

            results.append(entry)

    return results


def extract_exams(text):
    """
    从文本中提取检查项目实体。
    返回去重后的检查项目列表。
    """
    found = []
    for exam in EXAM_KEYWORDS:
        if exam.lower() in text.lower():
            found.append(exam)
    seen = set()
    unique = []
    for e in found:
        if e not in seen:
            seen.add(e)
            unique.append(e)
    return unique


def extract_lab_values(text):
    """
    从文本中提取检验数值指标。
    通过指标名称匹配 + 附近数值提取。
    返回包含指标名、实测值、单位、参考范围和异常程度的列表。
    """
    results = []

    for indicator in LAB_INDICATORS:
        names_to_match = [indicator["name"]]
        if indicator["name_en"]:
            names_to_match.append(indicator["name_en"])

        for name in names_to_match:
            if name in text:
                # 在指标名称附近搜索数值
                # 匹配模式：指标名 + 可选字符 + 数值 + 可选单位
                search_range_start = text.find(name)
                search_range_end = min(search_range_start + 80, len(text))
                search_segment = text[search_range_start:search_range_end]

                # 提取实测值：找到第一个合理的数字
                value_pattern = re.compile(
                    r'[:：\s]([\d]+(?:\.[\d]+)?)'
                )
                value_match = value_pattern.search(search_segment)

                if value_match:
                    try:
                        value = float(value_match.group(1))
                    except ValueError:
                        continue

                    entry = {
                        "indicator": indicator["name"],
                        "indicator_en": indicator.get("name_en", ""),
                        "value": value,
                        "unit": indicator["unit"],
                        "ref_low": indicator["ref_low"],
                        "ref_high": indicator["ref_high"],
                    }

                    # 计算异常程度
                    entry["is_abnormal"] = (
                        value < indicator["ref_low"] or
                        value > indicator["ref_high"]
                    )

                    if entry["is_abnormal"]:
                        if value < indicator["ref_low"]:
                            ref_mid = (indicator["ref_low"] + indicator["ref_high"]) / 2
                            deviation = abs(indicator["ref_low"] - value) / max(ref_mid, 0.01) * 100
                        else:
                            ref_mid = (indicator["ref_low"] + indicator["ref_high"]) / 2
                            deviation = abs(value - indicator["ref_high"]) / max(ref_mid, 0.01) * 100

                        if deviation < 15:
                            entry["severity"] = "轻度偏离"
                        elif deviation < 50:
                            entry["severity"] = "中度偏离"
                        else:
                            entry["severity"] = "重度偏离"
                    else:
                        entry["severity"] = "正常"

                    results.append(entry)
                break  # 找到第一个匹配的名称即可

    return results


def extract_vital_signs(text):
    """
    从文本中提取生命体征数值（血压、心率、体温、呼吸等）。
    """
    results = []

    # 血压：如 150/95 mmHg 或 150/95mmHg
    bp_pattern = re.compile(
        r'血压[:：]?\s*(\d{2,3})\s*/\s*(\d{2,3})\s*(?:mmHg)?'
    )
    bp_match = bp_pattern.search(text)
    if bp_match:
        sbp = int(bp_match.group(1))
        dbp = int(bp_match.group(2))
        sbp_abnormal = sbp >= 140
        dbp_abnormal = dbp >= 90
        if sbp >= 180 or dbp >= 110:
            severity = "重度偏离"
        elif sbp >= 160 or dbp >= 100:
            severity = "中度偏离"
        elif sbp_abnormal or dbp_abnormal:
            severity = "轻度偏离"
        else:
            severity = "正常"
        results.append({
            "indicator": "血压",
            "value": "{}/{} mmHg".format(sbp, dbp),
            "systolic": sbp,
            "diastolic": dbp,
            "ref": "< 140/90 mmHg",
            "is_abnormal": sbp_abnormal or dbp_abnormal,
            "severity": severity,
        })

    # 心率
    hr_pattern = re.compile(
        r'(?:心率|脉搏)[:：]?\s*(\d{2,3})\s*次/?分'
    )
    hr_match = hr_pattern.search(text)
    if hr_match:
        hr = int(hr_match.group(1))
        results.append({
            "indicator": "心率",
            "value": "{} 次/分".format(hr),
            "ref": "60-100 次/分",
            "is_abnormal": hr < 60 or hr > 100,
            "severity": "轻度偏离" if (hr < 60 or hr > 100) else "正常",
        })

    # 体温
    temp_pattern = re.compile(
        r'(?:体温|温度)[:：]?\s*(\d{2}(?:\.\d+)?)\s*°?C'
    )
    temp_match = temp_pattern.search(text)
    if temp_match:
        temp = float(temp_match.group(1))
        results.append({
            "indicator": "体温",
            "value": "{} °C".format(temp),
            "ref": "36.0-37.3 °C",
            "is_abnormal": temp > 37.3 or temp < 36.0,
            "severity": "轻度偏离" if (temp > 37.3 or temp < 36.0) else "正常",
        })

    # 呼吸
    rr_pattern = re.compile(
        r'呼吸[:：]?\s*(\d{2,3})\s*次/?分'
    )
    rr_match = rr_pattern.search(text)
    if rr_match:
        rr = int(rr_match.group(1))
        results.append({
            "indicator": "呼吸频率",
            "value": "{} 次/分".format(rr),
            "ref": "12-20 次/分",
            "is_abnormal": rr < 12 or rr > 20,
            "severity": "轻度偏离" if (rr < 12 or rr > 20) else "正常",
        })

    # BMI
    bmi_pattern = re.compile(
        r'BMI[:：]?\s*(\d{1,2}(?:\.\d+)?)\s*kg/m'
    )
    bmi_match = bmi_pattern.search(text)
    if bmi_match:
        bmi = float(bmi_match.group(1))
        if bmi >= 28:
            severity = "中度偏离"
            category = "肥胖"
        elif bmi >= 24:
            severity = "轻度偏离"
            category = "超重"
        elif bmi < 18.5:
            severity = "轻度偏离"
            category = "偏瘦"
        else:
            severity = "正常"
            category = "正常"
        results.append({
            "indicator": "BMI",
            "value": "{} kg/m^2".format(bmi),
            "ref": "18.5-23.9 kg/m^2",
            "is_abnormal": bmi < 18.5 or bmi >= 24,
            "severity": severity,
            "category": category if severity != "正常" else "",
        })

    return results


# ============================================================
# 3. 综合提取
# ============================================================

def extract_all(text):
    """
    对输入文本执行全量医疗实体提取。
    返回结构化字典。
    """
    return {
        "symptoms": extract_symptoms(text),
        "diagnoses": extract_diagnoses(text),
        "medications": extract_medications(text),
        "examinations": extract_exams(text),
        "lab_values": extract_lab_values(text),
        "vital_signs": extract_vital_signs(text),
    }


# ============================================================
# 4. 主程序入口
# ============================================================

def main():
    """
    命令行入口。
    用法：
        python medical_entity_extractor.py <输入文本文件路径>
        python medical_entity_extractor.py                    # 从 stdin 读取
    """
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print("[ERROR] 文件不存在: {}".format(filepath), file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print("[ERROR] 读取文件失败: {}".format(e), file=sys.stderr)
            sys.exit(1)
    else:
        # 从 stdin 读取
        text = sys.stdin.read()

    if not text.strip():
        print("[WARN] 输入文本为空。", file=sys.stderr)
        sys.exit(0)

    result = extract_all(text)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()