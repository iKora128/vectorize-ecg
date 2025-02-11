import streamlit as st
import os
import tempfile
from PIL import Image
import matplotlib.pyplot as plt
from mfer2img import plot_ecg_from_mfer
from search import get_image_embedding, search_similar_images
from MFER_Reader.MFER_Reader import MFER_12Leads
from dev.vectorize-ecg.config import IMAGE_BASE_DIR

# 定数
LEAD_NAMES = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF',
              'V1', 'V2', 'V3', 'V4', 'V5', 'V6']

def convert_mfer_to_images(uploaded_file):
    """アップロードされたMFERファイルを画像に変換"""
    # 一時ファイルとして保存
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mwf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    # 一時ディレクトリの作成
    temp_dir = tempfile.mkdtemp()
    
    # MFERファイルを画像に変換
    plot_ecg_from_mfer(tmp_path, temp_dir)
    
    # 生成された画像のパスを取得
    image_paths = {}
    for lead in LEAD_NAMES:
        img_path = os.path.join(temp_dir, f"{os.path.basename(tmp_path).replace('.mwf', '')}_{lead}.png")
        if os.path.exists(img_path):
            image_paths[lead] = img_path
    
    # 一時MFERファイルを削除
    os.unlink(tmp_path)
    
    return image_paths

def display_search_results(results, query_image_path):
    """検索結果の表示"""
    st.subheader("クエリ画像")
    st.image(query_image_path, use_column_width=True)
    
    st.subheader("類似画像")
    for i, result in enumerate(results, 1):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # 相対パスで画像を読み込む
            year = result.payload['year']
            file_name = result.payload['file_name']
            image_path = os.path.join(IMAGE_BASE_DIR, year, file_name)
            
            if os.path.exists(image_path):
                st.image(image_path, use_column_width=True)
            else:
                st.error(f"画像が見つかりません: {image_path}")
            st.write(f"類似度: {result.score:.4f}")
        
        with col2:
            st.write("メタデータ:")
            st.write(f"- リード: {result.payload['lead_name']}")
            if 'metadata' in result.payload:
                meta = result.payload['metadata']
                st.write(f"- 検査日時: {meta.get('exam_datetime', '不明')}")
                st.write(f"- 性別: {meta.get('gender', '不明')}")
                if 'diagnoses' in meta:
                    st.write("- 診断:")
                    for diag in meta['diagnoses']:
                        st.write(f"  - {diag['text']}")

def main():
    st.title("心電図類似検索システム")
    
    # サイドバーの設定
    st.sidebar.header("検索設定")
    top_k = st.sidebar.slider("表示する類似画像の数", 1, 20, 5)
    selected_lead = st.sidebar.selectbox("検索対象のリード", ['すべて'] + LEAD_NAMES)
    similarity_threshold = st.sidebar.slider("類似度しきい値", 0.0, 1.0, 0.5)
    
    # ファイルアップローダー
    uploaded_file = st.file_uploader("MFERファイルをアップロード", type=['mwf'])
    
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
            
        # 一時ファイルのクリーンアップ
        for path in image_paths.values():
            if os.path.exists(path):
                os.unlink(path)

if __name__ == "__main__":
    main() 