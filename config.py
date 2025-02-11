import os

# ベースディレクトリの設定
BASE_DIR = os.getenv('ECG_DATA_DIR', os.path.expanduser('~/data'))  # 環境変数から取得、なければデフォルト値

# データディレクトリの設定
IMAGE_BASE_DIR = os.path.join(BASE_DIR, "mfer_images")
XML_DIR = os.path.join(BASE_DIR, "xml")

# 処理対象の年リスト（2011年から2018年まで）
TARGET_YEARS = [f"{year}年" for year in range(2011, 2019)]

# Qdrantの設定
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "ecg_images_collection"

# モデルの設定
MODEL_NAME = "google/vit-base-patch16-224-in21k"

# XMLパース時のエラー処理設定
SKIP_MISSING_XML = True  # XMLファイルが見つからない場合はスキップ