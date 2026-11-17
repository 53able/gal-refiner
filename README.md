# gal-refiner

日本語の文章を「ギャル目線」にリファインするエージェントスキルです。語尾をギャル語にするだけでなく、自分の「好き」で言い切る、読み手を仲間として具体的に褒める、否定で終わらせない、という視点へ書き換えます。数値、日付、URL、出典、結論、注意書きは変えません。

## インストール

[skills](https://github.com/vercel-labs/skills) CLI で入れます。Node.js 22.20 以降が必要です。

```bash
npx skills add 53able/gal-refiner
```

エージェントを指定する場合:

```bash
npx skills add 53able/gal-refiner --skill gal-refiner -a claude-code
```

`-g` を付けると、すべてのプロジェクトで使えるようになります。

## 使い方

「ギャルっぽくして」「ギャル目線で書き直して」「ギャルマインドで」「アゲな感じに」といった依頼で起動します。強度は 3 段階です。

| 強度 | 語り口 | 向いている場面 |
|---|---|---|
| `light` | です・ます調のまま、硬い敬語を崩す。絵文字なし | 社内文書、顧客向けの柔らかい案内 |
| `medium` (既定) | 「〜じゃん」「めっちゃ」を要所に | ブログ、社内チャット、SNS |
| `full` | ギャル語・感嘆を積極的に。絵文字は媒体が許す場合だけ | 企画ネタ、キャラ台詞、遊びの投稿 |

法律、医療、メンタルヘルスの危機対応、謝罪、弔意の文書と、実在人物の口調の模倣には使いません。

同梱の `scripts/check_preservation.py` は、元文と書き換え後を照合し、数値・URL・出典番号の欠落を報告して、元文の留保文を一覧にします。Python 3 の標準ライブラリだけで動きます。

```bash
python3 skills/gal-refiner/scripts/check_preservation.py original.md refined.md
```

## 構成

```
skills/gal-refiner/
├── SKILL.md                  手順の本体
├── references/
│   └── gal-viewpoint.md      目線の変換パターン、強度別の語彙、避ける表現、書き換え例
└── scripts/
    └── check_preservation.py 元文と書き換え後の照合
evals/gal-refiner/            評価ケース (インストールされない)
```

## 評価ケース

`evals/gal-refiner/` に 3 件の評価ケースがあります。

- `research-summary-keeps-caveats`: 調査メモを書き換えても、数値・出典・留保が残るか
- `retro-slack-message-full`: `full` の Slack 投稿で、数値を保ち、元文にない評価を足さないか
- `light-notice-for-customers`: 顧客向けの告知を `light` で柔らかくし、絵文字や元文にない案内を足さないか

各ケースは `case.yaml` (期待する結果)、`prompt.md` (依頼文)、`graders/` (判定の観点) からなります。スキルの本体とは別のディレクトリに置いてあり、`npx skills add` ではインストールされません。

## 背景

ペルソナ指定が変えるのは主に話し方で、事実の正確さは上がりません。そのため、このスキルは事実を先に固定し、目線と語り口を変えたあとで元文と照合する手順を取ります。ギャル目線の定義は、ギャルマインドに関する調査メモ (2026-11-18、本リポジトリには含みません) から、文章の書き換えに使える部分だけを抜き出したものです。

## ライセンス

[MIT](LICENSE)
