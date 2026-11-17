#!/usr/bin/env python3
"""元文と書き換え後の文章を照合し、事実系トークンの欠落を報告し、元文の留保文を一覧にする。

使い方:
    python3 check_preservation.py <元文ファイル> <書き換え後ファイル> [--json]

終了コード: 0 = 欠落なし / 1 = 欠落あり（要確認） / 2 = 入力エラー
留保文の一覧は欠落判定に使わない。書き換え後に同じ意味が残っているかを目で確かめるためのもの。
"""
import argparse
import json
import re
import sys
import unicodedata

URL_RE = re.compile(r"https?://[^\s)\]>」』]+")
CODE_RE = re.compile(r"`([^`\n]+)`")
CITE_RE = re.compile(r"\[(\d+(?:\s*,\s*[^\]]+)?)\]")
# 数値: 1,234 / 3.5 / 2026 / 4名 など。単位は付けずに数字部分だけ比較する
NUM_RE = re.compile(r"\d+(?:[.,]\d+)*")
HEDGE_WORDS = [
    "ただし", "未検証", "確認できない", "確認できなかった", "とは限らない", "言えない",
    "できない", "可能性", "限定的", "探索的", "断定", "注意", "区別", "保証",
    "わからない", "分からない", "かもしれない", "ではない", "とは別", "違う",
]
SENT_RE = re.compile(r"[^。！？!?\n]+[。！？!?]?")
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def hedge_sentences(text: str) -> list:
    t = MD_LINK_RE.sub(r"[\1]", normalize(text))
    out = []
    for s in SENT_RE.findall(t):
        s = s.strip(" -*#|>")
        if s and any(w in s for w in HEDGE_WORDS) and s not in out:
            out.append(s)
    return out


def normalize(text: str) -> str:
    # 全角数字などを半角へ寄せる
    return unicodedata.normalize("NFKC", text)


def extract(text: str) -> dict:
    t = normalize(text)
    urls = URL_RE.findall(t)
    t_no_url = URL_RE.sub(" ", t)
    codes = CODE_RE.findall(t_no_url)
    cites = [c.split(",")[0].strip() for c in CITE_RE.findall(t_no_url)]
    nums = [n.replace(",", "") for n in NUM_RE.findall(t_no_url)]
    return {"urls": urls, "codes": codes, "cites": cites, "nums": nums}


def missing(before: list, after: list) -> list:
    """before にあって after にない要素（重複を考慮しない集合差）。"""
    return sorted(set(before) - set(after), key=lambda x: (len(x), x))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("original")
    p.add_argument("refined")
    p.add_argument("--json", action="store_true", help="JSONで出力する")
    a = p.parse_args()
    try:
        with open(a.original, encoding="utf-8") as f:
            src = f.read()
        with open(a.refined, encoding="utf-8") as f:
            dst = f.read()
    except OSError as e:
        print(f"入力エラー: {e}", file=sys.stderr)
        return 2

    s, d = extract(src), extract(dst)
    report = {
        "missing_numbers": missing(s["nums"], d["nums"]),
        "added_numbers": missing(d["nums"], s["nums"]),
        "missing_urls": missing(s["urls"], d["urls"]),
        "missing_citations": missing(s["cites"], d["cites"]),
        "missing_inline_code": missing(s["codes"], d["codes"]),
        "hedge_sentences_to_check": hedge_sentences(src),
    }
    problems = any(report[k] for k in ("missing_numbers", "added_numbers", "missing_urls",
                                        "missing_citations", "missing_inline_code"))

    if a.json:
        report["ok"] = not problems
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1 if problems else 0

    labels = {
        "missing_numbers": "消えた数値",
        "added_numbers": "増えた数値（元文にない）",
        "missing_urls": "消えたURL",
        "missing_citations": "消えた出典番号",
        "missing_inline_code": "消えたインラインコード",
    }
    for k, label in labels.items():
        if report[k]:
            print(f"[要確認] {label}: {', '.join(report[k])}")
    hs = report["hedge_sentences_to_check"]
    if hs:
        print(f"[目視] 元文の留保・注意書き {len(hs)} 文。書き換え後に同じ意味が残っているか確かめる（言い回しは変えてよい）:")
        for i, h in enumerate(hs, 1):
            print(f"  {i}. {h}")
    print("結果: " + ("要確認あり" if problems else "欠落なし"))
    print("※ 数値の表記替え（4名→4人、5人中4人→4/5）は機械照合で欠落に見えることがある。目視で判断する。")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
