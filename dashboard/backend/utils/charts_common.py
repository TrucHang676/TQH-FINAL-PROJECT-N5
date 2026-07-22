# Nhập các thư viện cần thiết cho tính toán và vẽ biểu đồ Plotly
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import json

# Tọa độ địa lý của các tỉnh thành Việt Nam để vẽ bản đồ
PROVINCE_COORDINATES = {
    'TP.HCM': {'lat': 10.8231, 'lon': 106.6297},
    'Hà Nội': {'lat': 21.0285, 'lon': 105.8542},
    'Đà Nẵng': {'lat': 16.0544, 'lon': 108.2022},
    'Bắc Ninh': {'lat': 21.1861, 'lon': 106.0763},
    'Hải Phòng': {'lat': 20.8449, 'lon': 106.6881},
    'Thái Nguyên': {'lat': 21.5939, 'lon': 105.8442},
    'Khánh Hòa': {'lat': 12.2388, 'lon': 109.1967},
    'Đồng Nai': {'lat': 10.9574, 'lon': 106.8427},
    'Hưng Yên': {'lat': 20.6465, 'lon': 106.0511},
    'Thừa Thiên Huế': {'lat': 16.4633, 'lon': 107.5909},
    'Bà Rịa - Vũng Tàu': {'lat': 10.4113, 'lon': 107.1360},
    'Quảng Ninh': {'lat': 20.9599, 'lon': 107.0476},
    'Cần Thơ': {'lat': 10.0452, 'lon': 105.7469},
    'Lâm Đồng': {'lat': 11.9404, 'lon': 108.4583},
    'Nghệ An': {'lat': 19.1671, 'lon': 104.9126},
    'Đắk Lắk': {'lat': 12.6784, 'lon': 108.0383},
    'Bình Dương': {'lat': 10.9805, 'lon': 106.6518}
}

# Bảng màu đại diện cho các vùng miền của Việt Nam
REGION_COLORS = {
    'Bắc': '#FA6781',       # Đỏ san hô (Bắc)
    'Nam': '#59B292',       # Xanh lá cây (Nam)
    'Trung': '#FFC94D',     # Vàng hổ phách (Trung)
    'Từ xa / Remote': '#3B82F6', # Xanh dương (Remote)
    'Khác': '#9ca3af'       # Xám trung tính
}

# Hàm cấu hình layout chung cho tất cả biểu đồ (font, màu nền, tooltip style)
def apply_layout_styles(fig):
    fig.update_layout(
        font_family="Inter, system-ui, -apple-system, sans-serif",
        font_color="#1e293b",
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode="closest",
        showlegend=False,
        transition=dict(duration=400, easing="cubic-in-out"),
        hoverlabel=dict(
            bgcolor="#FFE066",
            bordercolor="#F5B000",
            font_size=12,
            font_family="Inter, system-ui, -apple-system, sans-serif",
            font_color="#1a1a1a",
            namelength=-1,
            align="left"
        )
    )
    return fig
