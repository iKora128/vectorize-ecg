from huggingface_hub import hf_hub_download
import os
import zipfile
from tqdm import tqdm

def download_and_extract():
    """
    Hugging Faceからデータセットをダウンロードして展開する
    データセット: longisland3/mfer-images
    """
    # ダウンロード先ディレクトリの作成
    base_dir = os.getenv('ECG_DATA_DIR', os.path.expanduser('~/data'))
    os.makedirs(base_dir, exist_ok=True)

    # ダウンロードするファイルリスト
    files = [
        ('mfer_images_part1.zip', '48.6GB'),
        ('mfer_images_part2.zip', '18GB'),
        ('mfer_xml.zip', '237MB')
    ]

    # トークンの確認
    token = os.getenv('HF_TOKEN')
    if not token:
        print("Warning: HF_TOKEN環境変数が設定されていません。")
        print("Private datasetにアクセスするにはトークンが必要です。")
        print("https://huggingface.co/settings/tokens でトークンを作成し、")
        print("export HF_TOKEN=your_token を実行してください。")
        return

    for file, size in files:
        print(f"\nDownloading {file} (約{size})...")
        try:
            path = hf_hub_download(
                repo_id="longisland3/mfer-images",
                filename=file,
                repo_type="dataset",
                token=token
            )
            
            print(f"Extracting {file}...")
            with zipfile.ZipFile(path, 'r') as zip_ref:
                # 展開先ディレクトリの決定
                extract_dir = os.path.join(base_dir, 'xml' if 'xml' in file else 'mfer_images')
                os.makedirs(extract_dir, exist_ok=True)
                
                # プログレスバー付きで展開
                for member in tqdm(zip_ref.namelist(), desc=f"Extracting {file}"):
                    zip_ref.extract(member, extract_dir)
            
            print(f"{file}の展開が完了しました")
            
        except Exception as e:
            print(f"Error downloading/extracting {file}: {str(e)}")
            continue

    print("\nAll files have been downloaded and extracted!")
    print(f"データは {base_dir} に保存されました")

if __name__ == "__main__":
    download_and_extract() 