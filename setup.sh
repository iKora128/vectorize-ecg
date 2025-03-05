#!/bin/bash

# 必要なディレクトリの作成
mkdir -p snapshots
mkdir -p data/qdrant
mkdir -p data/images
mkdir -p data/xml

# スナップショットファイルのパスを変数に定義
SNAPSHOT_FILE="snapshots/ecg_images_enbedding_collection-vit-base-patch16-224-in21k.snapshot"

# 必要なパッケージのインストール
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# Hugging Face CLIのセットアップ
echo "Please enter your Hugging Face token:"
read -s token
export HF_TOKEN=$token
uv run huggingface-cli login --token $token

# データセットのダウンロードと展開（既存データの確認付き）
echo "Checking for existing data..."
if [ -d "data/images" ] && [ "$(find data/images -type f | wc -l)" -gt 10 ] && [ -d "data/xml" ] && [ "$(find data/xml -type f | wc -l)" -gt 10 ]; then
    echo "Existing data found. Skipping download..."
else
    echo "Downloading and extracting dataset..."
    uv run download_dataset.py
fi

# 展開の確認
echo "Checking directory structure..."
echo "Contents of data/images:"
find data/images -type f | head -n 5
echo "Contents of data/xml:"
find data/xml -type f | head -n 5

# 実際のディレクトリ構造に基づいてチェック
if ! find data/images -type f -name "*_2011*.png" -quit; then
    echo "Error: No 2011 images found"
    exit 1
fi

# スナップショットの存在確認
if [ ! -f "$SNAPSHOT_FILE" ]; then
    echo "Error: Snapshot file not found"
    exit 1
fi

# Dockerの起動
echo "Starting Qdrant..."
docker compose up -d

# Qdrantの起動を待つ
echo "Waiting for Qdrant to start..."
# Qdrantのヘルスチェックにより起動待ち（タイムアウト60秒）
timeout=0
while true; do
    if curl -s http://localhost:6333/healthz | grep -q "ok"; then
        echo "Qdrant is up!"
        break
    fi
    sleep 2
    timeout=$((timeout+2))
    if [ $timeout -ge 60 ]; then
        echo "Qdrant did not start within 60 seconds."
        exit 1
    fi
done

# コレクションの作成と復元
echo "Checking for existing collection..."
collection_exists=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:6333/collections/mfer_ecg)

if [ "$collection_exists" = "200" ]; then
    echo "Collection exists, deleting it first..."
    curl -X DELETE 'http://localhost:6333/collections/mfer_ecg'
    sleep 5
fi

echo "Creating collection..."
curl -X PUT 'http://localhost:6333/collections/mfer_ecg' \
    -H 'Content-Type: application/json' \
    -d '{
        "vectors": {
            "size": 768,
            "distance": "Cosine"
        }
    }'

# スナップショットパスの確認とデバッグ情報
echo "Checking snapshot location..."
ls -la snapshots/

# スナップショットの復元を試す（複数のエンドポイントを試行）
echo "Attempting snapshot recovery with multiple methods..."

# 方法1: POST /collections/{collection_name}/snapshots/upload
echo "Method 1: Uploading snapshot..."
curl -v -X POST 'http://localhost:6333/collections/mfer_ecg/snapshots/upload' \
    -H 'Content-Type: multipart/form-data' \
    -F "snapshot=@$SNAPSHOT_FILE" \
    || echo "Method 1 failed, trying next method"

sleep 5

# 方法2: POST /snapshots/recover (古いAPI)
echo "Method 2: Using legacy API..."
curl -v -X POST 'http://localhost:6333/snapshots/recover' \
    -H 'Content-Type: application/json' \
    -d '{
        "location":"'"$SNAPSHOT_FILE"'",
        "collection_name": "mfer_ecg"
    }' \
    || echo "Method 2 failed, trying next method"

sleep 5

# 方法3: PUT /collections/{collection_name}/snapshots/recover
echo "Method 3: Using new PUT API..."
curl -v -X PUT 'http://localhost:6333/collections/mfer_ecg/snapshots/recover' \
    -H 'Content-Type: application/json' \
    -d '{
        "location":"'"$SNAPSHOT_FILE"'"
    }' \
    || echo "Method 3 failed"

# 復元の確認
echo "Verifying collection..."
response=$(curl -s 'http://localhost:6333/collections/mfer_ecg')
points_count=$(echo "$response" | grep -o '"points_count":[0-9]\+' | cut -d ':' -f2)

# ポイント数が0の場合はエラーとして処理
if [ "$points_count" = "0" ]; then
    echo "Error: Snapshot recovery failed or empty snapshot. Please check the logs and the snapshot file."
    exit 1
fi

echo "Setup completed!" 