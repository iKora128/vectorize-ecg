from huggingface_hub import upload_file

# 既存のスナップショットをアップロード
snapshot_name = "ecg_images_enbedding_collection-vit-base-patch16-224-in21k.snapshot"
upload_file(
    path_or_fileobj=f"/home/nagashimadaichi/dev/vectorize-ecg/snapshot.tar",
    path_in_repo=snapshot_name,
    repo_id="longisland3/mfer-images",
    repo_type="dataset"
) 