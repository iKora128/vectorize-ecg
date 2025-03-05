from huggingface_hub import hf_hub_download
import os
import zipfile
from tqdm import tqdm

def normalize_path(path):
    """パス内の余分なディレクトリ構造を削除しつつ、必要な構造は維持"""
    parts = path.split('/')
    print(f"Processing path: {path}")  # デバッグ用
    
    # ファイル名から年を抽出
    filename = parts[-1]
    if '_2011' in filename:  # 例: 000000002064_20110811103702_V4.png
        year = '2011年'
        return os.path.join(year, filename)
    
    # mferディレクトリは無視
    if 'mfer' in parts:
        parts = [p for p in parts if p != 'mfer']
    
    # 年を含むパスを探す
    for i, part in enumerate(parts):
        if '年' in part:
            result = '/'.join(parts[i:])
            print(f"Normalized to: {result}")  # デバッグ用
            return result
            
    print(f"No year found in path: {path}")  # デバッグ用
    return filename  # ファイル名のみを返す

def download_and_extract():
    """
    Hugging Faceからデータセットをダウンロードして展開する
    データセット: longisland3/mfer-images
    """
    # ダウンロード先ディレクトリの作成
    base_dir = os.path.join(os.getcwd(), 'data')  # カレントディレクトリの下のdataフォルダを使用
    os.makedirs(base_dir, exist_ok=True)

    # スナップショットのダウンロード
    print("\nDownloading snapshot...")
    snapshot_path = hf_hub_download(
        repo_id="longisland3/mfer-images",
        filename="ecg_images_enbedding_collection-vit-base-patch16-224-in21k.snapshot",
        repo_type="dataset",
        token=os.getenv('HF_TOKEN')
    )
    # スナップショットを適切な場所にコピー
    os.makedirs("snapshots", exist_ok=True)
    os.system(f"cp {snapshot_path} snapshots/")
    print("Snapshot downloaded and copied to snapshots directory")

    # ダウンロードするファイルリスト
    files = [
        ('mfer_images_part1.zip', '48.6GB'),
        ('mfer_images_part2.zip', '18GB'),
        ('mfer_xml.zip', '237MB')
    ]

    for file, size in files:
        print(f"\nDownloading {file} (約{size})...")
        try:
            path = hf_hub_download(
                repo_id="longisland3/mfer-images",
                filename=file,
                repo_type="dataset",
                token=os.getenv('HF_TOKEN')
            )
            
            print(f"Extracting {file}...")
            with zipfile.ZipFile(path, 'r') as zip_ref:
                extract_dir = os.path.join(base_dir, 'xml' if 'xml' in file else 'images')
                os.makedirs(extract_dir, exist_ok=True)
                
                # 修正された展開処理
                for member in tqdm(zip_ref.namelist(), desc=f"Extracting {file}"):
                    # 絶対パスを相対パスに変換
                    normalized_path = normalize_path(member)
                    if normalized_path:  # 空でない場合のみ展開
                        source = zip_ref.read(member)
                        target_path = os.path.join(extract_dir, normalized_path)
                        # ディレクトリの場合
                        if member.endswith('/'):
                            os.makedirs(target_path, exist_ok=True)
                        # ファイルの場合
                        else:
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            with open(target_path, 'wb') as f:
                                f.write(source)
            
            print(f"{file}の展開が完了しました")
            
        except Exception as e:
            print(f"Error downloading/extracting {file}: {str(e)}")
            continue

    print("\nAll files have been downloaded and extracted!")
    print(f"データは {base_dir} に保存されました")

if __name__ == "__main__":
    download_and_extract() 