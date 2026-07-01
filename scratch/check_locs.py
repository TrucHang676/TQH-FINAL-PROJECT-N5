import pandas as pd

try:
    df_raw = pd.read_csv('d:/BaiTapKi2Nam3/TQHDL/Final/data/raw/vietnam_it_jobs_raw.csv')
    print(df_raw['dia_diem'].unique()[:10])
except Exception as e:
    pass
    
df_proc = pd.read_csv('d:/BaiTapKi2Nam3/TQHDL/Final/data/processed/vietnam_it_jobs_processed.csv')
with open('d:/BaiTapKi2Nam3/TQHDL/Final/locs.txt', 'w', encoding='utf-8') as f:
    f.write("Tinh thanh: " + str(df_proc['tinh_thanh'].unique().tolist()) + "\n")
    f.write("Vung mien: " + str(df_proc['vung_mien'].unique().tolist()) + "\n")
