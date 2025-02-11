import os
import matplotlib.pyplot as plt
from MFER_Reader.MFER_Reader import MFER_12Leads
import gc
from tqdm import tqdm
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='mfer_processing.log'
)

# 定数を上部で定義
LEAD_NAMES = ['MWF_ECG_LEAD_I', 'MWF_ECG_LEAD_II', 'MWF_ECG_LEAD_III', 
             'MWF_ECG_LEAD_aVR', 'MWF_ECG_LEAD_aVL', 'MWF_ECG_LEAD_aVF',
             'MWF_ECG_LEAD_V1', 'MWF_ECG_LEAD_V2', 'MWF_ECG_LEAD_V3',
             'MWF_ECG_LEAD_V4', 'MWF_ECG_LEAD_V5', 'MWF_ECG_LEAD_V6']
FIGURE_SIZE = (10, 4)
DPI = 100

def plot_ecg_from_mfer(mfer_path, save_dir=None):
    """MFERファイルから12誘導心電図をプロットし、各誘導ごとに保存する"""
    
    with plt.style.context('fast'):  # 高速プロット設定
        mfer = MFER_12Leads(mfer_path, show_attrib=False)
        wave_data = mfer.waveforms[0]
        
        for lead in LEAD_NAMES:
            fig, ax = plt.subplots(figsize=FIGURE_SIZE)
            ax.plot(wave_data['offset_msec'], wave_data[lead])
            ax.set_title(lead.replace('MWF_ECG_LEAD_', ''))
            ax.grid(True)
            
            if save_dir:
                # 誘導名を取得（例：I, II, V1など）
                lead_name = lead.replace('MWF_ECG_LEAD_', '')
                save_path = os.path.join(save_dir, f"{os.path.basename(mfer_path).replace('.mwf', '')}_{lead_name}.png")
                plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
            else:
                plt.show()
            plt.close(fig)  # 各反復でfigureを明示的にクローズ
        
        del wave_data
        del mfer
        gc.collect()

def process_mfer_files(mfer_dir, save_dir):
    """ディレクトリ内のすべてのMFERファイルを処理"""
    logging.info(f"処理開始: {mfer_dir}")
    mfer_files = []
    processed_files = 0
    skipped_files = 0
    
    for root, _, files in os.walk(mfer_dir):
        for file in files:
            if file.endswith('.mwf'):
                mfer_files.append(os.path.join(root, file))
    
    for mfer_path in tqdm(mfer_files, desc="ファイル処理中"):
        try:
            plot_ecg_from_mfer(mfer_path, save_dir)
            processed_files += 1
            logging.info(f"成功: {os.path.basename(mfer_path)}")
        except Exception as e:
            skipped_files += 1
            logging.error(f"エラー {os.path.basename(mfer_path)}: {str(e)}")
            plt.close('all')  # エラー時もfigureをクローズ
            continue  # 次のファイルに進む
    
    logging.info(f"処理完了 - 成功: {processed_files}件, スキップ: {skipped_files}件")

def process_root_directory(root_mfer_dir: str, root_save_dir: str):
    """
    MFERファイルの親ディレクトリを処理し、ディレクトリ構造を維持して保存
    
    Parameters:
    -----------
    root_mfer_dir: str
        MFERファイルのルートディレクトリ
    root_save_dir: str
        保存先のルートディレクトリ
    """
    logging.info(f"ルートディレクトリの処理開始: {root_mfer_dir}")
    
    # サブディレクトリを取得
    subdirs = [d for d in os.listdir(root_mfer_dir) 
              if os.path.isdir(os.path.join(root_mfer_dir, d))]
    
    total_stats = {'files': 0, 'success': 0, 'errors': 0}
    
    # サブディレクトリごとに処理
    for subdir in subdirs:
        current_mfer_dir = os.path.join(root_mfer_dir, subdir)
        current_save_dir = os.path.join(root_save_dir, subdir)
        
        logging.info(f"サブディレクトリの処理開始: {subdir}")
        os.makedirs(current_save_dir, exist_ok=True)
        
        # 既存のprocess_mfer_filesを利用
        process_mfer_files(current_mfer_dir, current_save_dir)
    
    logging.info(f"全ディレクトリの処理完了")

def main():
    # ログ設定
    log_filename = f"mfer_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )

    # ディレクトリ設定
    root_mfer_dir = "/home/nagashimadaichi/data/mfer"
    root_save_dir = "/home/nagashimadaichi/data/mfer_images"
    
    # 処理実行
    process_root_directory(root_mfer_dir, root_save_dir)

if __name__ == "__main__":
    main()
