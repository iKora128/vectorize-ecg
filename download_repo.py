from huggingface_hub import snapshot_download

# レポジトリをダウンロード
repo_id = "longisland3/mfer-images"
local_dir = snapshot_download(
    repo_id=repo_id,
    repo_type="dataset",
    cache_dir="./cache",
    local_dir="/home/nagashimadaichi/data",
    ignore_patterns=["*.msgpack", "*.h5", "*.ot"],
)

print(f"モデルは {local_dir} にダウンロードされました") 