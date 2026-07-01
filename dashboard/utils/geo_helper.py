import urllib.request
import json
import os

def fetch_vietnam_geojson():
    url = "https://code.highcharts.com/mapdata/countries/vn/vn-all.geo.json"
    geo_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'geo')
    out_path = os.path.join(geo_dir, 'vietnam_provinces.geojson')
    
    if not os.path.exists(geo_dir):
        os.makedirs(geo_dir)
        
    print(f"Downloading GeoJSON from {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        
        print(f"Downloaded successfully to {out_path}")
        print(f"Number of features: {len(data['features'])}")
        
        # Print sample properties to understand how to map them
        print("Sample properties:")
        for i in range(min(5, len(data['features']))):
            print(data['features'][i]['properties'])
            
    except Exception as e:
        print(f"Error fetching GeoJSON: {e}")

if __name__ == "__main__":
    fetch_vietnam_geojson()
