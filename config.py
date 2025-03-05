import os
import torch

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
COLLECTION_NAME = "mfer_ecg"

# モデルの設定
MODEL_NAME = "google/vit-base-patch16-224-in21k"

# XMLパース時のエラー処理設定
SKIP_MISSING_XML = True  # XMLファイルが見つからない場合はスキップ

# GPU設定
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
USE_GPU = torch.cuda.is_available()

# バッチ処理設定
BATCH_SIZE = 32 if USE_GPU else 16

# 画像の設定
IMAGE_SIZE = 224  # VIT modelの入力サイズ
VECTOR_SIZE = 768  # VIT-BASE の出力次元