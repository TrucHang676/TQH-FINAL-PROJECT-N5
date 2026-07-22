from pathlib import Path
import pandas as pd

_cached_df = None
_csv_path = Path(__file__).parent.parent.parent.parent.resolve() / "data" / "processed" / "vietnam_it_jobs_processed.csv"
_api_cache = {}

def get_df() -> pd.DataFrame:
    """
    Tải file CSV một lần duy nhất vào bộ nhớ (RAM).
    Các lần gọi tiếp theo sẽ trả về cached DataFrame giúp tăng tốc API gấp 10-50 lần.
    """
    global _cached_df
    if _cached_df is None:
        if _csv_path.exists():
            _cached_df = pd.read_csv(_csv_path)
        else:
            _cached_df = pd.DataFrame(columns=[
                'ten_cong_viec', 'ten_cong_ty', 'nhom_vi_tri', 'cap_do_kinh_nghiem', 
                'tinh_thanh', 'vung_mien', 'luong_tb', 'hinh_thuc_lam_viec', 'ngay_dang', 
                'thang_dang', 'nguon', 'ky_nang', 'luong_min', 'luong_max', 'loai_luong'
            ])
    return _cached_df

def make_cache_key(prefix: str, req) -> str:
    """Tạo cache key từ thông số bộ lọc request"""
    d = req.dict() if hasattr(req, 'dict') else dict(req)
    items = []
    for k, v in sorted(d.items()):
        if isinstance(v, list):
            items.append((k, tuple(sorted(v))))
        else:
            items.append((k, v))
    return f"{prefix}:{tuple(items)}"

def get_cached_response(key: str):
    return _api_cache.get(key)

def set_cached_response(key: str, value):
    _api_cache[key] = value
