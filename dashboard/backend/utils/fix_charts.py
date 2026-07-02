import pandas as pd

with open('D:\\BaiTapKi2Nam3\\TQHDL\\Final\\backend\\utils\\charts.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Add cliponaxis
text = text.replace(
    "textposition='outside',",
    "textposition='outside',\n        cliponaxis=False,"
)

# Add range limit for create_region_vertical_chart
old_yaxes = """    fig.update_yaxes(
        showgrid=True,
        gridcolor='#f1f5f9',
        linecolor='#e5e7eb',
        tickfont=dict(size=9, color='#4b5563'),
        title_text="Số lượng tin",
        title_font=dict(size=10, color='#6b7280')
    )

    apply_layout_styles(fig)
    fig.update_layout(margin=dict(l=40, r=20, t=40, b=10), bargap=0.3)

    return fig"""

new_yaxes = """    import pandas as pd
    max_count = region_counts['count'].max()

    fig.update_yaxes(
        showgrid=True,
        gridcolor='#f1f5f9',
        linecolor='#e5e7eb',
        tickfont=dict(size=9, color='#4b5563'),
        title_text="Số lượng tin",
        title_font=dict(size=10, color='#6b7280'),
        range=[0, max_count * 1.15] if not pd.isna(max_count) else None
    )

    apply_layout_styles(fig)
    fig.update_layout(margin=dict(l=40, r=20, t=40, b=10), bargap=0.3)

    return fig"""

if old_yaxes in text:
    text = text.replace(old_yaxes, new_yaxes)
else:
    print('Failed to find yaxes replace target!')

with open('D:\\BaiTapKi2Nam3\\TQHDL\\Final\\backend\\utils\\charts.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Done')
