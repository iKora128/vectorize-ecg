import os
import torch
from PIL import Image
from transformers import ViTImageProcessor, ViTModel
from qdrant_client import QdrantClient
from qdrant_client.models import CollectionInfo, VectorParams, Distance, PointStruct
import xml.etree.ElementTree as ET
from datetime import datetime
from config import *  # 設定をインポート
from tqdm import tqdm
import itertools

# Qdrantサーバが立ち上がっている前提
# 例: docker run -p 6333:6333 qdrant/qdrant

# 1) ViTのモデルとImageProcessorのロード
model_name_or_path = "google/vit-base-patch16-224-in21k"  # お好みで変更可能
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

image_processor = ViTImageProcessor.from_pretrained(model_name_or_path)
model = ViTModel.from_pretrained(model_name_or_path)
model.to(device)
model.eval()

# 2) Qdrantクライアント接続
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# 3) コレクションの作成(まだない場合)
collection_name = COLLECTION_NAME
dimension = 768  # ViT-baseの埋め込み次元

if qdrant_client.collection_exists(collection_name):
    qdrant_client.delete_collection(collection_name)

qdrant_client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
)

def get_image_embedding(image_path):
    """画像パスを読み込み、ViTで埋め込みベクトルを返す"""
    image = Image.open(image_path).convert("RGB")
    inputs = image_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**{k: v.to(device) for k, v in inputs.items()})
    # outputs.last_hidden_state: (batch, seq_len, hidden_size)
    # ViTModelの最終トークン(CLSトークン)を取得して埋め込みとする例:
    embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy().flatten()
    return embedding

def parse_ecg_xml(xml_path):
    """ECG XMLファイルからメタデータを抽出する"""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # 名前空間の定義
        ns = {'v3': 'urn:hl7-org:v3'}
        
        # 基本情報の抽出
        effective_time = root.find('.//v3:effectiveTime/v3:low', ns)
        exam_datetime = datetime.strptime(effective_time.get('value'), '%Y%m%d%H%M%S') if effective_time is not None else None
        
        # 患者情報
        gender = root.find('.//v3:administrativeGenderCode', ns)
        gender_code = gender.get('code') if gender is not None else None
        
        # 測定値の抽出
        measurements = {}
        for measured_value in root.findall('.//v3:measuredValue', ns):
            code = measured_value.find('v3:code', ns)
            value = measured_value.find('v3:value', ns)
            if code is not None and value is not None:
                code_name = code.get('displayName')
                measurements[code_name] = {
                    'value': value.get('value'),
                    'unit': value.get('unit')
                }
        
        # 診断情報の抽出
        diagnoses = []
        for interpretation in root.findall('.//v3:interpretationResult', ns):
            text = interpretation.find('v3:text', ns)
            value = interpretation.find('v3:value', ns)
            if text is not None and text.text and text.text.strip():
                diagnoses.append({
                    'text': text.text.strip(),
                    'code': value.text if value is not None else None
                })
        
        # ミネソタコードの抽出（エラー処理を追加）
        minnesota_codes = []
        try:
            for group in root.findall('.//v3:justifiedDecisionGroup', ns):
                code = group.find('v3:interpretationCode', ns)
                if code is not None and code.get('displayName') == 'ミネソタコード':
                    for result in group.findall('.//v3:interpretationResult/v3:value', ns):
                        if result.text and result.text.strip():
                            minnesota_codes.append(result.text.strip())
        except Exception as e:
            print(f"Warning: Error parsing Minnesota codes: {e}")
        
        # メタデータの構築
        metadata = {
            'exam_datetime': exam_datetime.isoformat() if exam_datetime else None,
            'gender': gender_code,
            'measurements': measurements,
            'diagnoses': diagnoses,
            'minnesota_codes': minnesota_codes
        }
        
        return metadata
    except Exception as e:
        print(f"Warning: Error parsing XML {xml_path}: {e}")
        return {}

# ファイルパスの設定を明示的に行う
base_image_dir = IMAGE_BASE_DIR
base_xml_dir = XML_DIR

# ファイル処理部分の修正
def find_xml_path(base_name, xml_date, base_xml_dir):
    """XMLファイルのパスを探索する"""
    xml_file = f"{base_name}_{xml_date}.xml"
    
    # 直接パスを試す
    direct_path = os.path.join(base_xml_dir, xml_file)
    if os.path.exists(direct_path):
        return direct_path
    
    # サブディレクトリを探索
    for root, _, files in os.walk(base_xml_dir):
        if xml_file in files:
            return os.path.join(root, xml_file)
    
    return None

def process_year_directory(year_dir, base_xml_dir, point_id_start=0):
    """年別ディレクトリの処理"""
    file_list = sorted([f for f in os.listdir(year_dir) if f.endswith('.png')])
    
    batch_size = 64
    point_id = point_id_start
    batch_vectors = []
    batch_payloads = []
    
    # tqdmでプログレスバーを表示
    for i, file_name in enumerate(tqdm(file_list, desc=f"Processing {os.path.basename(year_dir)}")):
        image_path = os.path.join(year_dir, file_name)
        embedding_vector = get_image_embedding(image_path)
        
        base_name = file_name.split('_')[0]
        xml_date = file_name.split('_')[1]
        xml_path = find_xml_path(base_name, xml_date, base_xml_dir)
        
        lead_name = file_name.split('_')[-1].replace('.png', '')
        metadata = parse_ecg_xml(xml_path) if xml_path else {}
        
        if not xml_path:
            print(f"Warning: XML file not found for image {file_name}")
        
        payload = {
            "file_name": file_name,
            "lead_name": lead_name,
            "metadata": metadata,
            "xml_path": xml_path,
            "year": os.path.basename(year_dir)  # 年情報を追加
        }
        
        batch_vectors.append(embedding_vector)
        batch_payloads.append(payload)
        
        if (i + 1) % batch_size == 0 or (i + 1) == len(file_list):
            points = [
                PointStruct(
                    id=point_id + j,
                    vector=vec,
                    payload=payload
                )
                for j, (vec, payload) in enumerate(zip(batch_vectors, batch_payloads))
            ]
            qdrant_client.upsert(collection_name=collection_name, points=points)
            point_id += len(batch_vectors)
            batch_vectors = []
            batch_payloads = []
    
    return point_id

# メイン処理
def main():
    point_id = 0
    
    # 各年のディレクトリを処理
    for year in tqdm(TARGET_YEARS, desc="Processing years"):
        year_dir = os.path.join(IMAGE_BASE_DIR, year)
        if os.path.exists(year_dir):
            print(f"\nProcessing directory: {year_dir}")
            point_id = process_year_directory(year_dir, XML_DIR, point_id)
        else:
            print(f"Warning: Directory not found: {year_dir}")
    
    print("\nAll images have been processed and upserted to Qdrant!")

if __name__ == "__main__":
    main()
