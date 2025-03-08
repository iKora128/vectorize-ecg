import os
import torch
from PIL import Image
from transformers import ViTImageProcessor, ViTModel
from qdrant_client import QdrantClient
from config import *

# ViTモデルのロード
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
image_processor = ViTImageProcessor.from_pretrained(MODEL_NAME)
model = ViTModel.from_pretrained(MODEL_NAME)
model.to(device)
model.eval()

# Qdrantクライアント接続
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

def get_image_embedding(image_path):
    """画像パスを読み込み、ViTで埋め込みベクトルを返す"""
    image = Image.open(image_path).convert("RGB")
    inputs = image_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**{k: v.to(device) for k, v in inputs.items()})
    embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy().flatten()
    return embedding

def search_similar_images(query_vector, top_k=5, score_threshold=0.5):
    client = QdrantClient("localhost", port=6333)
    
    # 検索を実行
    search_result = client.search(
        collection_name="mfer_ecg",
        query_vector=query_vector,
        limit=top_k,
        score_threshold=score_threshold
    )
    
    # 結果を整形して返す
    results = []
    for scored_point in search_result:
        result = {
            "image_path": scored_point.payload.get("image_path"),
            "similarity": scored_point.score,
            "metadata": {
                "id": scored_point.id,
                "datetime": scored_point.payload.get("datetime"),
                # その他必要なメタデータがあれば追加
            }
        }
        results.append(result)
    
    return results

def main():
    # 使用例
    query_image = input("検索する画像のパスを入力してください: ")
    top_k = int(input("表示する類似画像の数を入力してください（デフォルト: 5）: ") or "5")
    
    query_vector = get_image_embedding(query_image)
    results = search_similar_images(query_vector, top_k=top_k)
    
    print("\n検索結果:")
    for i, r in enumerate(results, 1):
        print(f"\n{i}番目の類似画像:")
        print(f"類似度スコア: {r['similarity']:.4f}")
        print("メタデータ:")
        print(f"- ファイル名: {r['image_path']}")
        print(f"- 検査日時: {r['metadata'].get('datetime')}")

if __name__ == "__main__":
    main() 