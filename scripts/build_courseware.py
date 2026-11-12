#!/usr/bin/env python3
"""把试卷讲评数据 (exam.json) 打包成单文件网页课件。

用法:
    python3 build_courseware.py exam.json -o 课件.html
    python3 build_courseware.py exam.json --check      # 只校验，不生成

校验分两级：
  ERROR  数据结构有硬伤，课件会出错或显示空白 -> 退出码 1
  WARN   课件能生成，但某个功能会静默失效（例如原文依据句在原文里找不到） -> 退出码 0
"""
import argparse
import json
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "template.html"
PLACEHOLDER = "/*__EXAM_DATA__*/null"
PUNCT = re.compile(r"[\s，。、；：！？“”‘’《》（）()\[\]【】,.;:!?\"'—…·\-_]")
PALETTES = ("ink", "snow", "bamboo", "indigo", "ochre", "night")


def norm(s):
    return PUNCT.sub("", str(s or ""))


def validate(exam):
    errors, warns = [], []
    if not isinstance(exam, dict) or not exam.get("sections"):
        return ["顶层必须是对象，且 sections 不能为空"], warns
    pal = (exam.get("meta") or {}).get("palette")
    if pal and pal not in PALETTES:
        warns.append(f"meta.palette「{pal}」不是内置配色（{'/'.join(PALETTES)}），课件会回退到 ink")
    seen_ids = set()
    for si, s in enumerate(exam["sections"]):
        where = f"sections[{si}]《{s.get('title', '?')}》"
        if not s.get("title"):
            errors.append(f"{where}: 缺少 title")
        passages = {}
        for pi, p in enumerate(s.get("passages", [])):
            pid = p.get("id") or f"{s.get('id', 's%d' % (si + 1))}-t{pi + 1}"
            paras = p.get("paragraphs", [])
            if not paras:
                errors.append(f"{where}.passages[{pi}]: paragraphs 为空，原文无法显示")
            para_ids = set()
            for k, pp in enumerate(paras):
                if not pp.get("text"):
                    errors.append(f"{where}.passages[{pi}].paragraphs[{k}]: 缺少 text")
                para_ids.add(pp.get("id") or f"p{k + 1}")
            for g in p.get("glosses", []):
                if not any(g.get("term", "\0") in pp.get("text", "") for pp in paras):
                    warns.append(f"{where}.passages[{pi}]: 释义词「{g.get('term')}」在原文里找不到，点词释义不会出现")
            if any(pp.get("trans") for pp in paras) and not all(pp.get("trans") for pp in paras):
                warns.append(f"{where}.passages[{pi}]: 有的段落有译文、有的没有，对照译文页会缺行")
            passages[pid] = (p, paras, para_ids)
        for qi, q in enumerate(s.get("questions", [])):
            qw = f"{where} 第{q.get('no', qi + 1)}题"
            qid = q.get("id") or f"{s.get('id', 's%d' % (si + 1))}-q{q.get('no', qi + 1)}"
            if qid in seen_ids:
                errors.append(f"{qw}: 题目 id 重复 ({qid})")
            seen_ids.add(qid)
            qtype = q.get("type") or ("choice" if q.get("options") else "dictation" if q.get("subs") else "writing" if q.get("writing") else "subjective")
            if not q.get("stem") and qtype != "writing":
                errors.append(f"{qw}: 缺少 stem")
            if not q.get("score"):
                warns.append(f"{qw}: 没写 score，分值统计会按 0 算")
            if qtype == "choice":
                keys = [o.get("key") for o in q.get("options", [])]
                ans = re.sub(r"[^A-Za-z]", "", str(q.get("answer", ""))).upper()
                if not ans:
                    errors.append(f"{qw}: 选择题缺少 answer")
                elif not set(ans) <= set(keys):
                    errors.append(f"{qw}: answer={ans} 不在选项 {keys} 里")
                if not q.get("analysis") and not any(o.get("analysis") for o in q.get("options", [])):
                    warns.append(f"{qw}: 没有解析（analysis 或每个选项的 analysis）")
            if qtype == "subjective" and not (q.get("answer_text") or q.get("points")):
                warns.append(f"{qw}: 主观题没有 answer_text / points")
            if qtype == "dictation":
                for k, sub in enumerate(q.get("subs", [])):
                    if not sub.get("blanks"):
                        errors.append(f"{qw} 第{k + 1}小问: blanks 为空")
                    for b in sub.get("blanks", []):
                        if not b.get("answer"):
                            errors.append(f"{qw} 第{k + 1}小问: 有空缺 answer")
                        for h in b.get("hot", []):
                            c = h if isinstance(h, str) else h.get("c", "")
                            if c and c not in b.get("answer", ""):
                                warns.append(f"{qw} 第{k + 1}小问: 易错字「{c}」不在答案「{b.get('answer')}」里")
            if qtype == "writing" and not q.get("writing"):
                errors.append(f"{qw}: 写作题缺少 writing 对象")
            # 原文依据句必须真的出现在原文里，否则「定位」会静默失效
            if q.get("evidence"):
                p_key = q.get("passage") or (next(iter(passages)) if passages else None)
                if p_key not in passages:
                    warns.append(f"{qw}: 有 evidence 但找不到对应的 passage ({p_key})")
                else:
                    _, paras, _ = passages[p_key]
                    for ev in q["evidence"]:
                        quote = ev.get("quote", "")
                        pool = [pp for k, pp in enumerate(paras) if not ev.get("para") or (pp.get("id") or f"p{k + 1}") == ev["para"]]
                        if not quote or not any(quote in pp.get("text", "") for pp in pool):
                            warns.append(f"{qw}: 依据句「{quote[:14]}…」在原文{'段落 ' + ev['para'] if ev.get('para') else ''}里找不到（必须逐字一致，包括标点）")
    return errors, warns


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("exam", help="试卷讲评数据 JSON")
    ap.add_argument("-o", "--out", help="输出的 HTML 路径（默认与 JSON 同名 .html）")
    ap.add_argument("--check", action="store_true", help="只校验，不生成")
    ap.add_argument("--palette", choices=PALETTES, help="强制指定默认配色，覆盖 meta.palette")
    args = ap.parse_args()

    src = Path(args.exam)
    try:
        exam = json.loads(src.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR  JSON 解析失败：第 {e.lineno} 行第 {e.colno} 列 — {e.msg}", file=sys.stderr)
        return 1

    errors, warns = validate(exam)
    for w in warns:
        print("WARN  ", w)
    for e in errors:
        print("ERROR ", e, file=sys.stderr)
    if errors:
        print(f"\n{len(errors)} 个错误，未生成课件。", file=sys.stderr)
        return 1
    if args.check:
        print(f"校验通过（{len(warns)} 条提醒）。")
        return 0

    if args.palette:
        exam.setdefault("meta", {})["palette"] = args.palette

    tpl = TEMPLATE.read_text(encoding="utf-8")
    if PLACEHOLDER not in tpl:
        print("ERROR  模板里找不到数据占位符", file=sys.stderr)
        return 1
    # </ 与 U+2028/2029 会破坏 <script> 内的 JS 字面量，统一转义
    blob = json.dumps(exam, ensure_ascii=False).replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    html = tpl.replace(PLACEHOLDER, blob, 1)
    out = Path(args.out) if args.out else src.with_suffix(".html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    n_q = sum(len(s.get("questions", [])) for s in exam["sections"])
    pal = (exam.get("meta") or {}).get("palette", "ink")
    print(f"已生成 {out}（{len(exam['sections'])} 个板块，{n_q} 道题，配色 {pal}，{out.stat().st_size // 1024} KB）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
