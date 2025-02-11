# 心電図類似検索システム

## 概要
このプロジェクトは、MFER形式の心電図データを画像に変換し、ViTモデルを使用して類似画像検索を行うシステムです。Hugging Faceのデータセットとqdrantベクトルデータベースを使用して、効率的な類似画像検索を実現します。

## 必要環境
- Python >= 3.8
- Docker（Qdrantサーバー用）
- ストレージ容量: 約70GB
- Hugging Faceアカウントとアクセストークン

## セットアップ手順

### 1. リポジトリのクローン
```bash
git clone https://github.com/yourusername/vectorize-ecg.git
cd vectorize-ecg
```

### 2. 環境変数の設定
```bash
# Hugging Faceのトークンを設定（必須）
export HF_TOKEN=your_huggingface_token

# データ保存先の設定（オプション、デフォルト: ~/data）
export ECG_DATA_DIR=~/data
```

### 3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

### 4. データセットのダウンロード
```bash
python scripts/download_dataset.py
```
このスクリプトは以下のファイルをダウンロードして展開します：
- mfer_images_part1.zip (48.6GB)
- mfer_images_part2.zip (18GB)
- mfer_xml.zip (237MB)

### 5. Qdrantサーバーの起動
```bash
docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
```

### 6. ベクトルデータベースの構築
```bash
python vectorize.py
```

### 7. アプリケーションの起動
```bash
streamlit run app.py
```

## データセット構造
```
~/data/
├── mfer_images/          # 画像データ
│   ├── 2011年/
│   │   ├── {ID}_{日時}_{リード名}.png
│   │   └── ...
│   └── ...
└── xml/                  # メタデータ
    ├── 2011年/
    │   ├── {ID}_{日時}.xml
    │   └── ...
    └── ...
```

## 機能
- MFERファイルのアップロードと画像変換
- 12誘導別の類似画像検索
- 類似度に基づくフィルタリング
- メタデータの表示（検査日時、性別、診断情報など）

## 使用方法

### Webインターフェース
1. ブラウザで http://localhost:8501 にアクセス
2. MFERファイルをアップロード
3. 検索パラメータを設定
   - 表示する類似画像の数（1-20）
   - 検索対象のリード（I, II, III, など）
   - 類似度しきい値（0.0-1.0）
4. 「類似画像を検索」ボタンをクリック

### 主要コンポーネント
- `app.py`: Streamlitウェブアプリケーション
- `vectorize.py`: 画像のベクトル化とQdrantへの登録
- `search.py`: 類似画像検索の実装
- `mfer2img.py`: MFERファイルから画像への変換
- `config.py`: 設定ファイル
- `scripts/download_dataset.py`: データセットダウンロードスクリプト

## 設定
`config.py`で以下の設定が可能です：
- `ECG_DATA_DIR`: データディレクトリのパス（環境変数で上書き可能）
- `QDRANT_HOST`: Qdrantサーバーのホスト
- `QDRANT_PORT`: Qdrantサーバーのポート
- `MODEL_NAME`: 使用するViTモデル
- `TARGET_YEARS`: 処理対象の年リスト

## トラブルシューティング

### データセットのダウンロードに失敗する場合
1. Hugging Faceトークンの確認
```bash
echo $HF_TOKEN
```

2. ストレージ容量の確認
```bash
df -h $ECG_DATA_DIR
```

### Qdrantに接続できない場合
```bash
docker ps  # コンテナの状態確認
docker logs qdrant  # ログの確認
```

### メモリ不足の場合
- `config.py`のバッチサイズを調整
- 必要に応じてスワップ領域を増設

## 注意事項
- データセットは約70GB必要です
- 初回のベクトル化には時間がかかります
- Hugging Faceのプライベートデータセットにアクセスするにはトークンが必要です

## ライセンス
MITライセンス