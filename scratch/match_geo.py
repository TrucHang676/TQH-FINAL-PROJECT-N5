import pandas as pd
import json
import unicodedata

def normalize_name(name):
    if not isinstance(name, str):
        return ""
    # Map some common aliases manually
    manual_map = {
        'TP.HCM': 'Hồ Chí Minh city',
        'Ha Noi': 'Hà Nội',
        'Hanoi': 'Hà Nội',
        'Ho Chi Minh City': 'Hồ Chí Minh city',
        'Bà Rịa - Vũng Tàu': 'Bà Rịa-Vũng Tàu',
        'Thua Thien Hue': 'Thừa Thiên Huế',
        'Thừa Thiên Huế': 'Thừa Thiên Huế',
        'Hue': 'Thừa Thiên Huế'
    }
    if name in manual_map:
        return manual_map[name]
    
    return name.strip()

with open('d:/BaiTapKi2Nam3/TQHDL/Final/dashboard/assets/geo/vietnam_provinces.geojson', 'r', encoding='utf-8') as f:
    geo = json.load(f)

geo_names = [f['properties'].get('name') or f['properties'].get('woe-name') for f in geo['features']]

df = pd.read_csv('d:/BaiTapKi2Nam3/TQHDL/Final/data/processed/vietnam_it_jobs_processed.csv')
tinh_thanh = df['tinh_thanh'].unique()

print("GeoJSON sample names:", geo_names[:10])

unmatched = []
for t in tinh_thanh:
    if t in ['Khác', 'Từ xa / Remote']:
        continue
    norm_t = normalize_name(t)
    # try exact match
    if norm_t in geo_names:
        continue
        
    # Try removing accents and comparing lower
    def remove_accents(input_str):
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return u"".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()
        
    found = False
    for gn in geo_names:
        if not gn: continue
        if remove_accents(norm_t) == remove_accents(gn):
            print(f"Matched {t} -> {gn}")
            found = True
            break
    if not found:
        unmatched.append(t)

print("Unmatched:", unmatched)
