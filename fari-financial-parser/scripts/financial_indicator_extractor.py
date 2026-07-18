#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
financial_indicator_extractor.py - 从中文金融文档文本中提取关键财务指标
仅使用 re、json、sys，无第三方依赖。
"""
import re
import json
import sys

INDICATORS = [
    {"name": "营业收入", "key": "revenue", "unit": "亿元",
     "patterns": [r'(?:实现)?营业收入[约为约][\s]*([0-9]+\.?[0-9]*)\s*(?:亿元|万元|元)']},
    {"name": "净利润", "key": "net_profit", "unit": "亿元",
     "patterns": [r'(?:归属于母公司股东的)?净利润[约为约][\s]*([0-9]+\.?[0-9]*)\s*(?:亿元|万元|元)']},
    {"name": "毛利率", "key": "gross_margin", "unit": "%",
     "patterns": [r'(?:综合)?毛利率[约为约][\s]*([0-9]+\.?[0-9]*)\s*[%％]']},
    {"name": "资产负债率", "key": "debt_to_asset_ratio", "unit": "%",
     "patterns": [r'资产负债率[约为约][\s]*([0-9]+\.?[0-9]*)\s*[%％]']},
    {"name": "经营现金流净额", "key": "operating_cash_flow", "unit": "亿元",
     "patterns": [r'经营活动(?:产生)?的?现金(?:流(?:量)?)?净额[约为约][\s]*([0-9]+\.?[0-9]*)\s*(?:亿元|万元|元)']},
]

def extract_all(text):
    indicators = []
    for ind_def in INDICATORS:
        for pattern in ind_def["patterns"]:
            match = re.search(pattern, text)
            if match:
                indicators.append({"name": ind_def["name"], "key": ind_def["key"], "value": float(match.group(1)), "unit": ind_def["unit"]})
                break
    return {"indicators": indicators, "total": len(indicators)}

def main():
    text = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    if text.strip():
        print(json.dumps(extract_all(text), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()