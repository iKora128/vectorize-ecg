# MFER心電図画像検索システム

## 概要
このプロジェクトは、MFER形式の心電図画像を解析し、ディープラーニング（ViTモデル）による画像のベクトル化と、Qdrant を使用した類似画像検索を実現するシステムです。研究・プロトタイプ用途を念頭に、効率的かつ継続的なデータ検索、管理、復元を可能にします。

## 機能概要
- **MFERファイルの解析と画像変換**  
  MFERファイルから心電図データを抽出し、画像に変換します。
- **画像のベクトル化**  
  変換された画像を ViT-BASE モデルを用いて 768 次元のベクトルに変換します。
- **高速類似画像検索**  
  Qdrant ベクトルデータベースにより、類似画像の高速な検索を実現します。
- **スナップショット復元**  
  Qdrant のスナップショット機能により、データの永続化と復元が可能です。

## 前提条件
- Python 3.10 以上
- Docker
- wget, curl

※ 本プロジェクトでは [uv](https://astral.sh/uv) を利用して、依存パッケージの同期やデータセットのダウンロード、Hugging Face CLI のログインなどを自動化しています。  
setup.sh 内で自動的に uv のインストールおよび設定が行われるため、ユーザ側での事前インストールは不要です。

## セットアップ手順

### 1. リポジトリのクローン
以下のコマンドでリポジトリをクローンしてください：
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. セットアップスクリプトの実行
`setup.sh` スクリプトは以下の処理を自動で行います：

- 必要なディレクトリ（snapshots, data/qdrant, data/images, data/xml）の作成
- uv のインストールと同期（`uv sync`）
- Hugging Face CLI のセットアップ（`uv run huggingface-cli login --token <token>`）  
- データセットのダウンロード（既存データが存在しない場合、`uv run download_dataset.py` の実行）
- Docker Compose による Qdrant サーバの起動とヘルスチェック
- Qdrant コレクションの作成およびスナップショット復元の試行

実行方法は以下の通り：
```bash
chmod +x setup.sh
./setup.sh
```

### 3. アプリケーションの起動
セットアップが完了したら、以下のコマンドでアプリケーションを起動してください：
```bash
python app.py
```

## UV の利用方法について
本プロジェクトでは uv コマンドを以下のタスクに活用しています：
- **依存パッケージの同期**  
  `uv sync` により、必要な依存関係が整えられます。
- **Hugging Face CLI の認証**  
  `uv run huggingface-cli login --token <token>` を用いて、Hugging Face のトークンを用いたログインが行われます。
- **データセットのダウンロード**  
  `uv run download_dataset.py` により、必要なデータセットがダウンロードおよび展開されます。

setup.sh でこれらのコマンドが順次実行されるため、各ツールの個別実行は不要となっています。

## APIエンドポイント

### 新規データのアップロード
- **エンドポイント**: POST /upload_mfer  
- **入力**: MFERデータのZIPファイル（画像とXML）

### 類似画像検索
- **エンドポイント**: POST /search  
- **入力**: 検索対象の心電図画像  
- **出力**: 類似度の高い画像と、対応するメタデータ

## Docker と Qdrant
本プロジェクトは Docker Compose を使用して Qdrant サーバを管理しています。  
**docker-compose.yml** の設定例：
- REST API（ポート 6333）および GRPC API（ポート 6334）の公開
- データ永続化用ディレクトリとして `./data/qdrant` を利用
- スナップショット保存用ディレクトリとして `./snapshots` を指定

setup.sh では Qdrant のヘルスチェックを実施し、最大 60 秒以内にサーバが起動したかを確認します。また、複数の API（POST、PUT 等）を試行して、スナップショットからの復元を行っています。

## ディレクトリ構成例
```
.
├── app.py               # アプリケーションエントリーポイント
├── config.py            # システム設定 (Qdrantホスト、画像ディレクトリ等)
├── docker-compose.yml   # Qdrantサーバの Docker Compose 設定
├── setup.sh             # セットアップスクリプト（uv 利用）
├── vectorize.py         # 画像ベクトル化処理
├── search.py            # 類似画像検索ロジック
├── MFER_Reader/         # MFERファイル処理ライブラリ
│   ├── __init__.py
│   └── MFER_Reader.py
├── snapshots/           # スナップショットファイル（Git 管理対象外）
└── data/                # 画像、Qdrantデータ、XML 等のデータ（Git 管理対象外）
```

## 注意事項
- Qdrant のコレクション作成前には、setup.sh 内でスナップショット復元処理が実行されます。正しいスナップショットファイル（`snapshots/ecg_images_enbedding_collection-vit-base-patch16-224-in21k.snapshot`）が配置されているか確認してください。
- ベクトル次元（768）は ViT-BASE モデルの出力に合わせています。モデル変更時にはこの値の更新が必要となります。
- 本システムは研究・プロトタイプ目的で作成されています。