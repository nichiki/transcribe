# 音声書き起こし & テキスト処理ツール (Gemini API)

Gemini APIを使用して音声ファイルの書き起こしとテキスト処理（要約・見出し付けなど）を行うPythonツールセットです。

## 機能

### 音声書き起こし (`transcribe.py`)
- MP3、WAV、AIFF、AAC、OGG、FLACフォーマットに対応
- ディレクトリ内の複数ファイル一括処理
- カスタムプロンプト対応
- フィラー（「あー」「えー」など）の自動除去

### テキスト処理 (`process_text.py`)
- テキストファイル（.txt、.md）の詳細な要約（元文章の40-60%の長さ）
- 見出し付けによる構造化（元文章は改変せず見出しのみ追加）
- カスタムプロンプトによる柔軟な処理
- 表記ルール（YAML形式）の適用による文章校正
- ディレクトリ内の複数ファイル一括処理

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. APIキーの設定

Google AI StudioでAPIキーを取得し、`.env`ファイルに設定してください：

```
GEMINI_API_KEY=your-actual-api-key-here
```

APIキーの取得方法：
1. [Google AI Studio](https://aistudio.google.com/) にアクセス
2. 「Get API key」をクリック
3. 生成されたAPIキーをコピー

## 使い方

### 音声書き起こし

```bash
# 単一ファイルの書き起こし
python transcribe.py audio.mp3

# 出力ファイル名を指定
python transcribe.py audio.mp3 -o transcript.md

# ディレクトリ内のすべての音声ファイルを処理
python transcribe.py ./audio_folder/

# サブディレクトリも含めて処理
python transcribe.py ./audio_folder/ --recursive

# 特定のパターンのファイルのみ処理
python transcribe.py ./audio_folder/ --pattern "interview_*.mp3"

# カスタムプロンプトを使用
python transcribe.py audio.mp3 --prompt my_custom_prompt.txt

# 出力先ディレクトリを指定（複数ファイル処理時）
python transcribe.py ./audio_folder/ --output-dir ./transcripts/
```

### テキスト処理

```bash
# テキストファイルを要約
python process_text.py document.txt --task summarize

# 見出しを付けて構造化
python process_text.py report.md --task headline

# カスタムプロンプトで処理
python process_text.py data.txt --task custom --prompt analysis_prompt.txt

# 表記ルール（デフォルト: rules/writing-rules.yaml）を適用して要約
python process_text.py document.txt --task summarize --rules

# カスタム表記ルールファイルを指定
python process_text.py document.txt --task summarize --rules my_rules.yaml

# ディレクトリ内のすべてのテキストファイルを要約
python process_text.py ./documents/ --task summarize --recursive

# 特定のパターンのファイルのみ処理
python process_text.py ./texts/ --pattern "report_*.txt" --task headline

# 出力先ディレクトリを指定
python process_text.py ./inputs/ --task summarize --output-dir ./summaries/
```

## ファイル構成

```
transcribe/
├── transcribe.py      # 音声書き起こしツール
├── process_text.py    # テキスト処理ツール
├── common.py          # 共通処理モジュール
├── requirements.txt   # 依存パッケージ
├── .env              # APIキー設定（要作成）
├── prompts/          # デフォルトプロンプト
│   ├── transcribe.txt # 書き起こし用プロンプト
│   ├── summarize.txt  # 要約用プロンプト
│   └── headline.txt   # 見出し付け用プロンプト
└── rules/            # 表記ルール
    └── writing-rules.yaml # デフォルト表記ルール
```

## 出力ファイル

### ファイル形式
すべての出力ファイルはMarkdown形式（.md）で保存されます：
- 音声書き起こし: `audio_transcript.md`
- 要約: `document_summarize.md`
- 見出し付け: `document_headline.md`

## プロンプトのカスタマイズ

### デフォルトプロンプトの変更
`prompts/`ディレクトリ内のファイルを編集することで、デフォルトの動作をカスタマイズできます：
- `transcribe.txt`: フィラー除去など書き起こしルール
- `summarize.txt`: 詳細な要約（40-60%の長さ）
- `headline.txt`: 見出し付け（元文章は改変しない）

### カスタムプロンプトの使用
独自のプロンプトファイルを作成し、`--prompt`オプションで指定できます：

```bash
# 音声書き起こしでカスタムプロンプト使用
python transcribe.py audio.mp3 --prompt custom_transcribe.txt

# テキスト処理でカスタムプロンプト使用
python process_text.py doc.txt --task custom --prompt my_analysis.txt
```

### 表記ルールの適用
表記ルール（YAML形式）を使用して、文章の表記を統一できます：

```bash
# デフォルトの表記ルール（rules/writing-rules.yaml）を適用
python process_text.py document.txt --task summarize --rules

# カスタム表記ルールファイルを指定
python process_text.py document.txt --task summarize --rules custom_rules.yaml

# 表記ルールとカスタムプロンプトを併用
python process_text.py doc.txt --task custom --prompt my_prompt.txt --rules
```

表記ルールファイルはYAML形式で、以下のような構造で定義します：
- `判定`: 自動チェック/要文脈判断
- `正解`: 正しい表記
- `NG例`: 避けるべき表記
- `条件`: 適用条件
- `文章例`: 使用例
- `備考`: 補足情報

## 処理可能なファイル形式

### 音声ファイル
- MP3 (.mp3)
- WAV (.wav)
- AIFF (.aiff)
- AAC (.aac)
- OGG (.ogg)
- FLAC (.flac)

### テキストファイル
- プレーンテキスト (.txt)
- Markdown (.md)
- テキストファイル (.text)

## 処理の特徴

### 要約処理
- 元の文章の40-60%程度の長さで詳細に要約
- 文章形式（箇条書きではない）で出力
- 重要な情報、具体例、数値データを保持

### 見出し付け処理
- 元の文章は一切改変せず、見出しのみを追加
- 階層的な見出し（#、##、###）で構造化
- 内容の論理的な流れに基づいて見出しを配置

### 表記ルール適用
- YAML形式の表記ルールファイルに基づいて文章を校正
- 文脈を考慮した表記の統一（例：「言う」vs「いう」）
- 口語表現の書き言葉への変換
- 数字表記の統一

## 制限事項

### 音声ファイル
- 最大ファイルサイズ: 20MB（大きいファイルは警告表示）
- 最大音声長: 9.5時間
- 音声は16 Kbpsにダウンサンプリングされます

### テキストファイル
- 10MB以上のファイルは処理に時間がかかる可能性があります

## トラブルシューティング

### APIキーエラー
`.env`ファイルにAPIキーが正しく設定されているか確認してください。

### ファイルが見つからない
ファイルパスが正しいか、ファイルが存在するか確認してください。

### サポートされていないフォーマット
上記の「処理可能なファイル形式」を確認してください。

### 処理が失敗する場合
- ファイルサイズが大きすぎないか確認
- ネットワーク接続を確認
- APIの利用制限に達していないか確認

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。