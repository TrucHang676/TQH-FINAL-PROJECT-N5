import urllib.request
import json
import os

url = "https://raw.githubusercontent.com/Tiennm99/Vietnam-geojson/master/vietnam_provinces.geojson"
# Or alternatively, https://raw.githubusercontent.com/sunshine-1102/Vietnam-geojson/master/vietnam.geojson
# Let's try the first one, or use a known good one from highcharts.

# Let's use standard highcharts vietnam map data if possible, or github raw.
# A very stable one is from https://raw.githubusercontent.com/Tiennm99/Vietnam-geojson/master/vietnam.geojson 
# Actually, I'll use a reliable source:
# https://raw.githubusercontent.com/daohoangson/d3-geomap/master/topojson/countries/VNM.json
# Wait, topojson is not geojson.
url = "https://raw.githubusercontent.com/Vizzuality/growapp/master/public/vietnam.geojson"

# Let's search github for vietnam geojson.
url = "https://raw.githubusercontent.com/Tiennm99/Vietnam-geojson/master/vietnam_provinces.geojson"

try:
    print("Downloading GeoJSON...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        
    out_path = "d:/BaiTapKi2Nam3/TQHDL/Final/dashboard/assets/geo/vietnam_provinces.geojson"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    
    print(f"Downloaded successfully to {out_path}")
    print(f"Number of features: {len(data['features'])}")
    print("Sample feature properties:", data['features'][0]['properties'])
    
except Exception as e:
    print("Error:", e)
    # Fallback to another source
    fallback_url = "https://raw.githubusercontent.com/albert-hg/vietnam-geojson/master/geojson/tinh_thanh.geojson"
    print("Trying fallback URL:", fallback_url)
    try:
        req = urllib.request.Request(fallback_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        out_path = "d:/BaiTapKi2Nam3/TQHDL/Final/dashboard/assets/geo/vietnam_provinces.geojson"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            
        print(f"Downloaded successfully to {out_path}")
        print(f"Number of features: {len(data['features'])}")
        print("Sample feature properties:", data['features'][0]['properties'])
    except Exception as e2:
        print("Fallback error:", e2)
