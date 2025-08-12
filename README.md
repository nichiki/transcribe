# 音声書き起こしアプリ (Gemini API)

GeminiのAPIを使用してMP3ファイルなどの音声ファイルを文字起こしするシンプルなPythonアプリケーションです。

## 機能

- MP3、WAV、AIFF、AAC、OGG、FLACフォーマットに対応
- コマンドラインから簡単に実行可能
- 書き起こし結果をテキストファイルに保存
- エラーハンドリングと進捗表示

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

### 基本的な使用方法

```bash
python transcribe.py audio.mp3
```

これにより、`audio_transcript.txt`というファイルが生成されます。

### 出力ファイル名を指定する場合

```bash
python transcribe.py audio.mp3 -o my_transcript.txt
```

### ヘルプの表示

```bash
python transcribe.py -h
```

## 例

```bash
# MP3ファイルを書き起こし
python transcribe.py interview.mp3

# 出力ファイル名を指定
python transcribe.py podcast.mp3 -o podcast_text.txt

# 別のフォルダにあるファイルを処理
python transcribe.py /path/to/audio/file.wav
```

## 制限事項

- 最大ファイルサイズ: 20MB（インライン送信の場合）
- 最大音声長: 9.5時間
- 音声は16 Kbpsにダウンサンプリングされます

## トラブルシューティング

### APIキーエラー
`.env`ファイルにAPIキーが正しく設定されているか確認してください。

### ファイルが見つからない
音声ファイルのパスが正しいか確認してください。

### サポートされていないフォーマット
対応フォーマット: MP3, WAV, AIFF, AAC, OGG, FLAC