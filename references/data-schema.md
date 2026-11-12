# 数据格式（exam.json）

整卷是一个 JSON 对象。**完整可运行的例子见 `examples/sample_exam.json`**，建议复制它再改。

字符串里的 `\n` 会换行；`**加粗**` 会渲染成粗体；其余都按纯文本处理（不要写 HTML）。中文引号用 “ ” 或「 」，不要用英文双引号，否则要转义。

## 顶层

```json
{
  "meta": {
    "tag": "新课标Ⅰ卷 · 真题",
    "title": "2024 年高考语文 · 新课标Ⅰ卷",
    "subtitle": "真题讲解 · 原文溯源 · 解题思路",
    "klass": "高三（2）班",
    "date": "2026-03-18",
    "palette": "ink",
    "reviewed": false,
    "cover": false
  },
  "sections": [ ... ]
}
```

| 字段 | 说明 |
|---|---|
| `meta.reviewed` | `false`（默认）时课件顶部显示「请核对」提示。教师核对完设为 `true` |
| `meta.cover` | `true` 时打开课件先显示封面 |
| `meta.palette` | 默认配色：`ink` 墨池（默认）/ `snow` 素笺 / `bamboo` 青瓷 / `indigo` 靛青 / `ochre` 牛皮 / `night` 夜课。老师用控制栏换过配色后以本机选择为准 |
| `meta.klass` / `meta.date` | 可选，显示在标题栏小字里（班级、日期），不写则不显示 |

## 板块 section

```json
{
  "id": "modern",
  "title": "现代文阅读",
  "passages": [ ... ],
  "questions": [ ... ]
}
```

默写、语用、写作等没有阅读材料的板块，`passages` 写 `[]`。导航上的「N 题 · X 分」由题目自动统计，不用写。

## 材料 passage

```json
{
  "id": "t1",
  "title": "梧桐",
  "genre": "文学类文本",
  "tag": "散文",
  "byline": "作者或出处",
  "kind": "poem",
  "numbered": true,
  "reading_tip": "**读法**：……",
  "paragraphs": [ { "id": "p1", "text": "……", "trans": "……", "label": "首联" } ],
  "glosses": [ { "term": "已", "gloss": "停止", "kind": "char" } ],
  "notes": ["注释一", "注释二"],
  "thread": "情感线或主线一句话",
  "structure": [ { "label": "起", "paras": "第 1 段", "text": "……" } ],
  "approach": {
    "title": "现代文阅读 · 做题思路",
    "chips": ["读情感线", "找关键词"],
    "items": [ { "label": "文学类题只有三问", "text": "……" } ],
    "pitfalls": ["常见误区一", "常见误区二"]
  }
}
```

| 字段 | 说明 |
|---|---|
| `paragraphs[].text` | 原文。**依据句和释义词都在这里面逐字匹配**，所以录入时不要改标点 |
| `paragraphs[].trans` | 该段译文。有了它，段尾出现「译」按钮，同时多出「对照译文」标签页。**要么每段都写，要么都不写** |
| `paragraphs[].label` | 段落标签。古诗用「首联」「颔联」；文言多材料用「材料一」。不写则用序号 |
| `kind: "poem"` | 古诗。对照译文页会写成「原句 · 第 N 句」 |
| `numbered: false` | 不显示段落序号块（古诗建议关掉） |
| `glosses` | 点词释义。`term` 必须在原文里出现，所有出现处都会加下划线。`kind`：`char` 单字词（虚线），`word` 双音词（点线） |
| `structure` / `approach` | 有则出现对应标签页；学生模式下题目揭晓前隐藏，避免提前看到答案思路 |

一篇文章有多个材料（例如文言文「材料一、材料二」）：写成 `passages` 里的多个元素，题目用 `"passage": "t2"` 指定对应哪个；不指定则用第一个。

## 题目 question

通用字段：

| 字段 | 说明 |
|---|---|
| `no` | 题号（数字） |
| `type` | `choice` / `subjective` / `dictation` / `writing`；可省略，会按内容推断 |
| `kind` | 题目类型标签，如「文学类·内容鉴赏」「文言·断句」 |
| `score` | 分值（数字） |
| `tag` | 角标，如「选讲」「重点」 |
| `difficulty` | 「易」「中」「难」 |
| `star` | `true` 时默认标为重点题（标题右侧 ☆ 亮起）。也可以不写，让老师上课时自己点星，星标按人保存在浏览器里 |
| `stem` | 题干 |
| `passage` | 对应的材料 id |
| `analysis` | 解析（整体） |
| `approach` | 字符串数组：做题思路，按步骤编号显示。有它就出现「技巧·模板」标记 |
| `approach_title` | 思路框标题，默认「答题思路」，可写「答题建模（四步法）」 |
| `pitfalls` | 字符串数组：常见误区 |
| `evidence` | 原文依据，见下 |

### 选择题 choice

```json
{
  "no": 6, "kind": "文学类·内容鉴赏", "score": 3,
  "stem": "下列对文本相关内容和艺术特色的分析鉴赏，正确的一项是（3分）",
  "options": [
    { "key": "A", "text": "……", "right": true,
      "basis": "对应第⑥段：「……」", "analysis": "……" }
  ],
  "answer": "A",
  "analysis": "……",
  "evidence": [ { "para": "p3", "quote": "原文逐字复制的句子", "note": "第③段：这里" } ]
}
```

- `answer`：单选写 `"A"`，多选写 `"BD"`。
- `options[].right`：**该选项的陈述是否正确**，和「它是不是答案」是两回事。题干问「不正确的一项」时，答案选项的 `right` 是 `false`。揭晓时选项会显示「表述正确／表述错误」，这样不会被「不正确」的题干搞混。
- `options[].basis`：这一项对应原文哪里，短短一句，显示在选项里。
- `options[].analysis`：为什么对／错。**每个选项都写**，讲评时逐项点才有东西可点。

### 主观题 subjective

```json
{
  "no": 8, "score": 4, "stem": "……",
  "answer_text": "①……；②……；③……",
  "points": ["内容：……（1分）", "手法：……（2分）"],
  "approach": [ "**写了什么**：……", "**怎么写的**：……" ]
}
```

`answer_text` 是参考答案全文，`points` 是分条得分点。至少写一个。

### 依据 evidence

```json
"evidence": [
  { "para": "p3", "quote": "忽然很想像从前一样，伸手去接那只杯盖", "note": "第③段：结尾句" }
]
```

- `quote` **必须是 `paragraphs[].text` 里连续的一段原文，逐字一致**。构建脚本会检查，找不到就 WARN。
- `para` 指定在哪个段落里找；不写则在整个材料里找。
- `note` 点「定位原文」时显示在题目下方，说明这一句为什么是依据。
- 一题可以有多条依据。

### 默写题 dictation

默写一问一屏：

```json
{
  "no": 17, "type": "dictation", "kind": "情景式默写", "score": 6,
  "stem": "补写出下列句子中的空缺部分。（6分）",
  "subs": [
    {
      "stem": "(1)……：“________，无以至千里。”",
      "blanks": [
        { "label": "空1", "prompt": "默写第 1 句", "answer": "不积跬步",
          "hot": ["跬"], "alt": ["可接受的另一种写法"] }
      ]
    }
  ]
}
```

- `answer`：标准答案。核对时忽略标点和空白。
- `hot`：易错字，在标准答案里**标红**。写字符串，或写 `{ "c": "蜉", "wrong": "浮" }` 附带「易误写为」提示。**`c` 必须在 `answer` 里**，否则构建脚本警告。
- `alt`：同样算对的别的写法（通假、异体等）。
- 学生模式点「核对作答」：学生写错的字会标红并划线，漏写会提示漏几个字，并自动判分（每空平分题目分值）。

### 写作题 writing

```json
{
  "no": 23, "type": "writing", "score": 60,
  "stem": "阅读下面的材料，根据要求写作。（60分）",
  "material": "作文材料全文",
  "requirements": "要求：……",
  "writing": {
    "analysis": { "summary": "……", "angles": [ { "label": "", "text": "", "level": "稳妥" } ], "traps": ["……"] },
    "structure": [ { "part": "开头", "words": "约 120 字", "text": "……" } ],
    "materials": [ { "title": "", "text": "", "use": "可用于……" } ],
    "openings": [ { "type": "亮观点式", "text": "……" } ],
    "endings":  [ { "type": "回扣式", "text": "……" } ],
    "model": { "title": "", "score": "54 分", "excerpt": false,
               "paragraphs": [ { "text": "范文段落", "comment": "批注：这段好在哪／可以讨论什么" } ] },
    "rubric": [ { "dim": "立意", "max": 20, "desc": "……" } ]
  }
}
```

六个键各自可选，写了几个就出现几个标签页（审题立意 / 结构框架 / 素材库 / 开头结尾 / 范文对照 / 评分量表）。`model`（范文）受「答案隐藏」控制，教师点揭晓前不显示。范文的批注 `comment` 与段落并排显示，用来「对照着讲」。
