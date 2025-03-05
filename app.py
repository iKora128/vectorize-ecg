import streamlit as st
import os
import tempfile
from PIL import Image
import matplotlib.pyplot as plt
from mfer2img import plot_ecg_from_mfer
from search import get_image_embedding, search_similar_images
from MFER_Reader import MFER_12Leads
from config import IMAGE_BASE_DIR

# 定数
LEAD_NAMES = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF',
              'V1', 'V2', 'V3', 'V4', 'V5', 'V6']

def main():
    st.title("心電図類似検索システム")
    
    # サイドバーの設定
    st.sidebar.header("検索設定")
    top_k = st.sidebar.slider("表示する類似画像の数", 1, 20, 5)
    selected_lead = st.sidebar.selectbox("検索対象のリード", ['すべて'] + LEAD_NAMES)
    similarity_threshold = st.sidebar.slider("類似度しきい値", 0.0, 1.0, 0.5)
    
    # ファイルアップローダー
    uploaded_file = st.file_uploader("MFERファイルをアップロード", type=['mwf'])
    
    # image_paths変数を事前に初期化
    image_paths = {}
    
    if uploaded_file:
        try:
            # MFERファイルを画像に変換
            image_paths = convert_mfer_to_images(uploaded_file)
            
            # リード選択（複数の画像が生成された場合）
            if len(image_paths) > 1:
                selected_image = st.selectbox(
                    "検索に使用するリードを選択してください",
                    list(image_paths.keys())
                )
                query_image_path = image_paths[selected_image]
            else:
                query_image_path = list(image_paths.values())[0]
            
            # 検索実行ボタン
            if st.button("類似画像を検索"):
                with st.spinner("検索中..."):
                    # リードでフィルタリングするための検索条件を追加
                    search_params = {
                        "query_image_path": query_image_path,
                        "top_k": top_k,
                        "threshold": similarity_threshold
                    }
                    if selected_lead != 'すべて':
                        search_params["lead_filter"] = selected_lead
                    
                    results = search_similar_images(**search_params)
                    display_search_results(results, query_image_path)
                
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
            
        # 一時ファイルのクリーンアップ (image_pathsが存在する場合のみ)
        if image_paths:
            for path in image_paths.values():
                if os.path.exists(path):
                    os.unlink(path)

def convert_mfer_to_images(uploaded_file):
    """
    アップロードされたMFERファイルを一時ディレクトリに保存し、
    各誘導の心電図画像を生成して、そのパスを辞書で返す
    """
    # 一時ディレクトリを作成
    temp_dir = tempfile.mkdtemp()
    
    # アップロードされたファイルを一時ファイルとして保存
    temp_mfer_path = os.path.join(temp_dir, "temp.mwf")
    with open(temp_mfer_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # 画像保存用の一時ディレクトリ
    temp_img_dir = os.path.join(temp_dir, "images")
    os.makedirs(temp_img_dir, exist_ok=True)
    
    # MFERファイルから画像を生成
    try:
        plot_ecg_from_mfer(temp_mfer_path, save_dir=temp_img_dir)
        
        # 生成された画像のパスを取得
        image_paths = {}
        for lead in LEAD_NAMES:
            # 例: temp_I.png, temp_V1.png など
            img_path = os.path.join(temp_img_dir, f"temp_{lead}.png")
            if os.path.exists(img_path):
                image_paths[lead] = img_path
        
        return image_paths
    except Exception as e:
        st.error(f"心電図画像の生成中にエラーが発生しました: {str(e)}")
        raise e

def display_search_results(results, query_image_path):
    """
    検索結果を表示する関数
    """
    st.subheader("クエリ画像")
    query_img = Image.open(query_image_path)
    st.image(query_img, width=600)
    
    st.subheader("検索結果")
    
    # 結果が空の場合
    if not results:
        st.warning("類似した画像が見つかりませんでした")
        return
    
    # 結果の表示
    for i, result in enumerate(results):
        col1, col2 = st.columns([1, 3])
        
        # 画像の表示
        img_path = result["image_path"]
        similarity = result["similarity"]
        
        with col1:
            img = Image.open(img_path)
            st.image(img, width=300)
        
        # メタデータの表示
        with col2:
            st.write(f"**類似度**: {similarity:.4f}")
            
            # メタデータがある場合は表示
            if "metadata" in result and result["metadata"]:
                metadata = result["metadata"]
                st.write("**メタデータ**:")
                for key, value in metadata.items():
                    st.write(f"- {key}: {value}")
        
        st.markdown("---")

if __name__ == "__main__":
    main() 