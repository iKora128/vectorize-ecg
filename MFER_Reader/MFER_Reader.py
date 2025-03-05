import re,codecs,datetime,sys,os.path,os
import pandas as pd
import numpy as np

tag_dic={}
tagdesc_dic={}

tag_dic[11]='MWF_IVL'
tagdesc_dic[11]='サンプリング間隔'
tag_dic[12]='MWF_SEN'
tagdesc_dic[12]='サンプリング解像度'
tag_dic[4]='MWF_BLK'
tagdesc_dic[4]='データブロック長'
tag_dic[5]='MWF_CHN'
tagdesc_dic[5]='チャネル数'
tag_dic[6]='MWF_SEQ'
tagdesc_dic[6]='シーケンス数'
tag_dic[8]='MWF_WFM'
tagdesc_dic[8]='波形種別'
tag_dic[63]='MWF_ATT'
tagdesc_dic[63]='チャネル属性定義'
tag_dic[9]='MWF_LDN'
tagdesc_dic[9]='波形属性'
tag_dic[30]='MWF_WAV'
tagdesc_dic[30]='波形データ'
tag_dic[10]='MWF_DTP'
tagdesc_dic[10]='データタイプ'
tag_dic[13]='MWF_OFF'
tagdesc_dic[13]='オフセット'
tag_dic[18]='MWF_NUL'
tagdesc_dic[18]='NULL値'
tag_dic[7]='MWF_PNT'
tagdesc_dic[7]='ポインタ'
tag_dic[21]='MWF_INF'
tagdesc_dic[21]='付帯情報'
tag_dic[17]='MWF_FLT'
tagdesc_dic[17]='フィルタ情報'
tag_dic[15]='MWF_IPD'
tagdesc_dic[15]='補間、間引き'
tag_dic[1]='MWF_BLE'
tagdesc_dic[1]='バイト並び'
tag_dic[2]='MWF_VER'
tagdesc_dic[2]='バージョン番号'
tag_dic[3]='MWF_TXC'
tagdesc_dic[3]='文字コード'
tag_dic[0]='MWF_ZRO'
tagdesc_dic[0]='空・終了コンテンツ'
tag_dic[22]='MWF_NTE'
tagdesc_dic[22]='コメント'
tag_dic[23]='MWF_MAN'
tagdesc_dic[23]='機種情報'
tag_dic[14]='MWF_CMP'
tagdesc_dic[14]='圧縮'
tag_dic[64]='MWF_PRE'
tagdesc_dic[64]='プリアンブル'
tag_dic[65]='MWF_EVT'
tagdesc_dic[65]='イベント'
tag_dic[66]='MWF_VAL'
tagdesc_dic[66]='値'
tag_dic[67]='MWF_SKW'
tagdesc_dic[67]='ディジタル化時間誤差'
tag_dic[68]='MWF_CND'
tagdesc_dic[68]='記録・表示条件'
tag_dic[103]='MWF_SET'
tagdesc_dic[103]='グループ定義'
tag_dic[69]='MWF_RPT'
tagdesc_dic[69]='参照ポインタ'
tag_dic[70]='MWF_SIG'
tagdesc_dic[70]='ディジタル署名'
tag_dic[128]='MWF_END'
tagdesc_dic[128]='記述終了'
tag_dic[129]='MWF_PNM'
tagdesc_dic[129]='患者名'
tag_dic[130]='MWF_PID'
tagdesc_dic[130]='患者ID'
tag_dic[131]='MWF_AGE'
tagdesc_dic[131]='生年月日、年齢'
tag_dic[132]='MWF_SEX'
tagdesc_dic[132]='性別'
tag_dic[133]='MWF_TIM'
tagdesc_dic[133]='測定時刻'
tag_dic[134]='MWF_MSS'
tagdesc_dic[134]='メッセージ'
tag_dic[135]='MWF_UID'
tagdesc_dic[135]='オブジェクト識別子'
tag_dic[136]='MWF_MAP'
tagdesc_dic[136]='記述マップ'

tag_dic['630']='MY_ECG1'
tag_dic['631']='MY_ECG2'
tag_dic['632']='MY_ECG3'
tag_dic['633']='MY_ECG4'
tag_dic['634']='MY_ECG5'
tag_dic['635']='MY_ECG6'
tag_dic['636']='MY_ECG7'
tag_dic['637']='MY_ECG8'

tagdesc_dic['630']='ECG1'
tagdesc_dic['631']='ECG2'
tagdesc_dic['632']='ECG3'
tagdesc_dic['633']='ECG4'
tagdesc_dic['634']='ECG5'
tagdesc_dic['635']='ECG6'
tagdesc_dic['636']='ECG7'
tagdesc_dic['637']='ECG8'

lead_dic={}
lead_dic[0]='MWF_ECG_LEAD_CONFIG'
lead_dic[1]='MWF_ECG_LEAD_I'
lead_dic[2]='MWF_ECG_LEAD_II'
lead_dic[3]='MWF_ECG_LEAD_V1'
lead_dic[4]='MWF_ECG_LEAD_V2'
lead_dic[5]='MWF_ECG_LEAD_V3'
lead_dic[6]='MWF_ECG_LEAD_V4'
lead_dic[7]='MWF_ECG_LEAD_V5'
lead_dic[8]='MWF_ECG_LEAD_V6'
lead_dic[9]='MWF_ECG_LEAD_V7'
lead_dic[11]='MWF_ECG_LEAD_V3R'
lead_dic[12]='MWF_ECG_LEAD_V4R'
lead_dic[13]='MWF_ECG_LEAD_V5R'
lead_dic[14]='MWF_ECG_LEAD_V6R'
lead_dic[15]='MWF_ECG_LEAD_V7R'
lead_dic[16]='MWF_ECG_LEAD_X'
lead_dic[17]='MWF_ECG_LEAD_Y'
lead_dic[18]='MWF_ECG_LEAD_Z'
lead_dic[19]='MWF_ECG_LEAD_CC5'
lead_dic[20]='MWF_ECG_LEAD_CM5'
lead_dic[31]='MWF_ECG_LEAD_NASA'
lead_dic[61]='MWF_ECG_LEAD_III'
lead_dic[62]='MWF_ECG_LEAD_aVR'
lead_dic[63]='MWF_ECG_LEAD_aVL'
lead_dic[64]='MWF_ECG_LEAD_aVF'

def get_start_datetime(header_df):
    val=header_df[header_df['name']=='MWF_TIM'].iloc[0]['value']
    year=val[0]+16**2*val[1]
    month=val[2]
    day=val[3]
    hour=val[4]
    minute=val[5]
    sec=val[6]
    msec=val[7]+16**2*val[8]
    usec=val[9]+16**2*val[10]+1000*msec
    return datetime.datetime(year,month,day,hour,minute,sec,usec)

def s16(value):
    return -(value & 0b1000000000000000) | (value & 0b0111111111111111)

def s8(value):
    return -(value & 0b10000000) | (value & 0b01111111)

def decode_data(cut_data,bytes_):
    bytes_list=[]
    for i in range(bytes_):
        bytes_list.append(256**i)
    """データを行列形式に整理"""
    cut_data=[n for n in cut_data] #16進数を10進数に変換
    data_np=np.array(cut_data).reshape(-1,bytes_) #行列として格納
    """内積によってデータ作成し、s16で補数を変換"""
    result= s16(np.inner(bytes_list,data_np))
    return result
    
class MFER_12Leads:
    def __init__(self, mferfile, show_attrib=True):
        with open(mferfile,'rb') as f:
            data=f.read()

        df=pd.DataFrame(columns=['header','value']) #wave以外のinformationを記述
        h=True
        m=False
        v=False
        k=0
        row=0
        header_dic={}
        wave_data_lists=[]
        wave_data_list=[]
        lead_lists = []
        block_lengths=[]
        data_idx = 0
        while k<len(data):
            if h:
                header=data[k]
                if header==63:
                    k+=1
                    header=str(header)+str(data[k])
                    
                if header==30:
                    data_idx += 1
                    val=df[df['header']==8].iloc[-1]['value']
                    wfm = val[0]+256*val[1]
                    
                    val=df[df['header']==11].iloc[0]['value']
                    idx = s8(val[1])
                    assert val[0] == 1 or val[0] ==1
                    if val[0]==1:
                        ivl = val[2]*10**(idx)
                    else:
                        hz = val[2]*10**(idx)
                        ivl = 1/hz
                    assert ivl == 0.002

                    val=df[df['header']==12].iloc[-1]['value']
                    assert val[0] == 0
                    idx = s8(val[1])
                    sampling_sen = (val[2]+val[3]*256+val[4]*256**2+val[5]*256**3)*10**idx*1000
                    assert sampling_sen == 0.00125

                    val=df[df['header']==10].iloc[-1]['value']
                    data_type = val[0]
                    assert data_type == 0

                    val=df[df['header']==17].iloc[-1]['value']
                    filter_info = ''.join([chr(v) for v in val])
                    
                    val=df[df['header']==5].iloc[-1]['value']
                    chn = val[0]+256*val[1]+256**2*val[2]+256**3*val[3]
                    assert chn == 8

                    val=df[df['header']==4].iloc[-1]['value']
                    block_length = val[0]+256*val[1]+256**2*val[2]+256**3*val[3]
                    block_lengths.append(block_length)
                    
                    val=df[df['header']==6].iloc[-1]['value']
                    seq = val[0]+256*val[1]+256**2*val[2]+256**3*val[3]
                    assert seq == 1            

                    lead_list = []
                    for c in range(chn):
                        val = df[df["header"]=="63"+str(c)].iloc[-1]['value']
                        lead_list.append(lead_dic[val[2]])
                    lead_lists.append(lead_list)

                    if show_attrib:
                        print("============================")
                        print("waveform", data_idx)
                        
                        if wfm == 1:
                            print("波形種別","標準１２誘導心電図")
                        if wfm == 8:
                            print("波形種別","アベレージビート抽出波形")
                        if wfm == 9:
                            print("波形種別","ドミナントビート抽出波形")
                        
                        print("サンプリング間隔(msec)",ivl*1000)
                        print("サンプリング解像度(mV)",sampling_sen)
                        print("フィルタ情報",filter_info)
                        print("チャネル数",chn)
                        print("ブロック長",block_length)
                        print("シーケンス数",seq)
                                            
                    if len(wave_data_list)>0:
                        wave_data_lists.append(wave_data_list)
                        wave_data_list = []
                        
                    if data[k]==8*16:# 終わりのflag:80があったら止める
                        #print("Data End")
                        break
                    data_length=data[k+2]*16**6+data[k+3]*16**4+data[k+4]*16**2+data[k+5]
                    wave_data=[]

                    wave_data=data[k+6:k+6+data_length]
                        #1バイトごとに読み取り　1バイトごとに16進数を10進数として記録
                    wave_data_list.append(wave_data)

                    k+=data_length+6
                    h=True
                    v=False
                    continue
                m=True
                h=False
                k+=1
            if m:
                length=data[k]
                m=False
                v=True
                k+=1
            if v:
                values=[]
                for l in range(length):
                    values.append(data[k+l])
                value=data[k:k+length]
                h=True
                v=False
                k+=length
                df.loc[row]=[header,values]
                row+=1

        if len(wave_data_list)>0:
            wave_data_lists.append(wave_data_list)

        df['name']=df['header'].apply(lambda x:tag_dic[x])
        df['desc']=df['header'].apply(lambda x:tagdesc_dic[x])
        df['str']=df['value'].apply(lambda x:b''.join([v.to_bytes(1,'little') for v in x]))

        seq_length = 1
        channel_num = 8
        sampling_sen = 0.00125
        sampling_ivl = 2

        waveforms=[]
        for wave_idx in range(2):
            dflist=[]
            block_length = block_lengths[wave_idx]
            for seq in range(seq_length):
                _dfwave=pd.DataFrame()
                for chn in range(channel_num):
                    _dfwave[lead_lists[wave_idx][chn]] = decode_data(wave_data_lists[wave_idx][0][seq*block_length*2*channel_num+block_length*2*chn
                                :seq*block_length*2*channel_num+block_length*2*(chn+1)],2)*sampling_sen
                dflist.append(_dfwave)
            
            dfwave=pd.concat(dflist)
            dfwave["MWF_ECG_LEAD_III"] = dfwave["MWF_ECG_LEAD_I"] - dfwave["MWF_ECG_LEAD_II"]
            dfwave["MWF_ECG_LEAD_aVR"] = - (dfwave["MWF_ECG_LEAD_I"] + dfwave["MWF_ECG_LEAD_II"])/2
            dfwave["MWF_ECG_LEAD_aVL"] = dfwave["MWF_ECG_LEAD_I"] - dfwave["MWF_ECG_LEAD_II"]/2
            dfwave["MWF_ECG_LEAD_aVF"] = dfwave["MWF_ECG_LEAD_II"] - dfwave["MWF_ECG_LEAD_I"]/2
            dfwave["offset_msec"]=sampling_ivl*dfwave.index

            waveforms.append(dfwave)

        
        # 現在のファイルの場所を基準にcodes.xlsxのパスを設定
        current_dir = os.path.dirname(os.path.abspath(__file__))
        codes_path = os.path.join(current_dir, 'codes.xlsx')

        # codes_pathを使用してファイルを読み込む
        dfcode=pd.read_excel(codes_path)

        dfleads=pd.DataFrame()
        dftotal=pd.DataFrame()
        for idx,row in df[df["header"]==66].iterrows():
            val=row['value']
            dec=val[0]+val[1]*256
            if dfcode[dfcode["DEC"]==dec].shape[0]>0:
                dftotal.loc[dfcode[dfcode["DEC"]==dec].iloc[0]["日本語名称"],"val"]=int(''.join([chr(v) for v in val[6:]]).split("^")[0])
                dftotal.loc[dfcode[dfcode["DEC"]==dec].iloc[0]["日本語名称"],"unit"]=''.join([chr(v) for v in val[6:]]).split("^")[1]
            else:
                lead=dec-dec//256*256
                measure=dec//256*256
                if lead>0x80:
                    lead-=0x80
                    measure+=0x80
                if dfcode[dfcode["DEC"]==measure].shape[0]>0:
                    dfleads.loc[lead_dic[lead],dfcode[dfcode["DEC"]==measure].iloc[0]["英名称"]+" val"]=int(''.join([chr(v) for v in val[6:]]).split("^")[0])
                    dfleads.loc[lead_dic[lead],dfcode[dfcode["DEC"]==measure].iloc[0]["英名称"]+" unit"]=''.join([chr(v) for v in val[6:]]).split("^")[1]
                
        
        dftotal_evt=pd.DataFrame()
        dfleads_evt=pd.DataFrame()
        for idx,row in df[df["header"]==65].iterrows():
            val=row['value']
            dec=val[0]+val[1]*256
            if dfcode[dfcode["DEC"]==dec].shape[0]>0:
                dftotal_evt.loc[dfcode[dfcode["DEC"]==dec].iloc[0]["英名称"],"content"]=''.join([chr(v) for v in val[6:]])        
            else:
                lead=dec-dec//256*256
                measure=dec//256*256
                if lead>0x80:
                    lead-=0x80
                    measure+=0x80
                if dfcode[dfcode["DEC"]==measure].shape[0]>0:
                    dfleads_evt.loc[lead_dic[lead],dfcode[dfcode["DEC"]==measure].iloc[0]["英名称"]]=''.join([chr(v) for v in val[6:]])

        self.datetime = get_start_datetime(df)
        self.waveforms = waveforms
        self.total_info = dftotal
        self.leads_info = dfleads
        self.total_events = dftotal_evt
        #self.leads_events = dfleads_evt #常に空？
