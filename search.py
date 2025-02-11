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

def search_similar_images(query_image_path, top_k=5, threshold=0.5, lead_filter=None):
    """類似画像を検索する
    
    Parameters:
    -----------
    query_image_path : str
        検索クエリとなる画像のパス
    top_k : int
        返す結果の最大数
    threshold : float
        類似度のしきい値（0-1）
    lead_filter : str, optional
        特定のリードでフィルタリング
    """
    query_vector = get_image_embedding(query_image_path)
    
    # 検索フィルター条件の設定
    search_params = {
        "collection_name": COLLECTION_NAME,
        "query_vector": query_vector,
        "limit": top_k,
        "score_threshold": threshold
    }
    
    # リードでフィルタリング
    if lead_filter:
        search_params["query_filter"] = {
            "must": [
                {
                    "key": "lead_name",
                    "match": {"value": lead_filter}
                }
            ]
        }
    
    search_result = qdrant_client.search(**search_params)
    return search_result

def main():
    # 使用例
    query_image = input("検索する画像のパスを入力してください: ")
    top_k = int(input("表示する類似画像の数を入力してください（デフォルト: 5）: ") or "5")
    
    results = search_similar_images(query_image, top_k=top_k)
    
    print("\n検索結果:")
    for i, r in enumerate(results, 1):
        print(f"\n{i}番目の類似画像:")
        print(f"類似度スコア: {r.score:.4f}")
        print("メタデータ:")
        print(f"- ファイル名: {r.payload['file_name']}")
        print(f"- リード名: {r.payload['lead_name']}")
        if 'metadata' in r.payload:
            meta = r.payload['metadata']
            print(f"- 検査日時: {meta.get('exam_datetime')}")
            print(f"- 性別: {meta.get('gender')}")
            if 'diagnoses' in meta:
                print("- 診断:")
                for diag in meta['diagnoses']:
                    print(f"  - {diag['text']}")

if __name__ == "__main__":
    main() 