import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title="E-Commerce Analytics | Dicoding",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
    <style>
    /* Header utama */
    .main-header {
        background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #3949ab 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
        text-align: center;
    }
    .main-header h1 { font-size: 1.9rem; margin: 0; font-weight: 700; }
    .main-header p  { font-size: 0.95rem; margin: 0.4rem 0 0; opacity: 0.85; }

    /* Kartu KPI */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #3949ab;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        font-weight: 600;
        padding: 0.4rem 1rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #F8F9FF; }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data():
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    main     = pd.read_csv(os.path.join(base, 'main_data.csv'))
    rfm      = pd.read_csv(os.path.join(base, 'rfm_segments.csv'))
    geo      = pd.read_csv(os.path.join(base, 'geographic_data.csv'))

    main['order_purchase_timestamp'] = pd.to_datetime(main['order_purchase_timestamp'])
    main['order_month_dt'] = main['order_purchase_timestamp'].dt.to_period('M').dt.to_timestamp()

    # *** FIX: Merge segmen ke main_data di sini, SEBELUM filter apapun. ***
    # Ini memastikan kolom 'segment' selalu ada di semua kombinasi filter
    # (tanggal, kategori, state) tanpa perlu merge ulang di setiap render.
    if 'segment' not in main.columns:
        main = main.merge(
            rfm[['customer_id', 'segment']],
            on='customer_id',
            how='left'
        )

    # Pastikan kolom geo benar
    if 'customer_city' not in geo.columns and geo.index.name == 'customer_city':
        geo = geo.reset_index()

    return main, rfm, geo

try:
    main_data, rfm_segments, geo_data = load_data()
except FileNotFoundError as e:
    st.error(f"❌ File data tidak ditemukan: {e}")
    st.info("Pastikan file berikut ada di folder yang sama dengan dashboard.py:\n"
            "- main_data.csv\n- rfm_segments.csv\n- geographic_data.csv")
    st.stop()

# ============================================================
# SIDEBAR — FILTER INTERAKTIF
# ============================================================
with st.sidebar:
    st.image("https://www.svgrepo.com/show/499870/shopping-cart.svg", width=60)
    st.title("🔍 Filter Data")
    st.markdown("---")

    # Filter tanggal
    min_date = main_data['order_purchase_timestamp'].min().date()
    max_date = main_data['order_purchase_timestamp'].max().date()

    st.subheader("📅 Periode Waktu")
    date_range = st.date_input(
        "Pilih rentang tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.subheader("📦 Kategori Produk")
    all_cats = sorted(main_data['product_category_name_english'].dropna().unique())
    selected_cats = st.multiselect(
        "Pilih kategori (kosongkan = semua)",
        options=all_cats,
        default=[],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.subheader("👥 Segmen Pelanggan")
    all_segs = sorted(rfm_segments['segment'].unique())
    selected_segs = st.multiselect(
        "Pilih segmen (kosongkan = semua)",
        options=all_segs,
        default=[],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.subheader("🗺️ Provinsi (State)")
    all_states = sorted(main_data['customer_state'].dropna().unique())
    selected_states = st.multiselect(
        "Pilih provinsi (kosongkan = semua)",
        options=all_states,
        default=[],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.caption("📊 Dashboard oleh: Chatrine Manurung\nDicoding Final Project 2025")

# ============================================================
# TERAPKAN FILTER
# ============================================================
# Catatan: main_data sudah berisi kolom 'segment' (di-merge saat load_data)
# sehingga filter apapun tidak akan menghilangkan data segmen.
filtered = main_data.copy()

if isinstance(date_range, tuple) and len(date_range) == 2:
    s, e = date_range
    filtered = filtered[
        (filtered['order_purchase_timestamp'].dt.date >= s) &
        (filtered['order_purchase_timestamp'].dt.date <= e)
    ]

if selected_cats:
    filtered = filtered[filtered['product_category_name_english'].isin(selected_cats)]

if selected_segs:
    # Langsung filter kolom 'segment' — tidak perlu lookup ke rfm_segments lagi
    filtered = filtered[filtered['segment'].isin(selected_segs)]

if selected_states:
    filtered = filtered[filtered['customer_state'].isin(selected_states)]

# Alias untuk kompatibilitas kode Tab RFM di bawah
filtered_with_seg = filtered

# ============================================================
# HEADER DASHBOARD
# ============================================================
st.markdown("""
    <div class="main-header">
        <h1>📊 E-Commerce Analytics Dashboard</h1>
        <p>Analisis Data E-Commerce Brazil 2018 &nbsp;|&nbsp; RFM Segmentation &nbsp;&bull;&nbsp; Geographic Analysis &nbsp;&bull;&nbsp; Category Performance</p>
    </div>
""", unsafe_allow_html=True)

# ============================================================
# KPI METRICS
# ============================================================
total_revenue    = filtered['payment_value'].sum()
total_orders     = filtered['order_id'].nunique()
total_customers  = filtered['customer_id'].nunique()
aov              = total_revenue / total_orders if total_orders else 0
acv              = total_revenue / total_customers if total_customers else 0

full_revenue = main_data['payment_value'].sum()
full_orders  = main_data['order_id'].nunique()
full_cust    = main_data['customer_id'].nunique()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("💰 Total Revenue",
              f"R$ {total_revenue/1e6:.2f}M",
              delta=f"{total_revenue/full_revenue*100:.1f}% dari total")
with col2:
    st.metric("📦 Total Orders",
              f"{total_orders:,}",
              delta=f"{total_orders/full_orders*100:.1f}% dari total")
with col3:
    st.metric("👥 Unique Customers",
              f"{total_customers:,}",
              delta=f"{total_customers/full_cust*100:.1f}% dari total")
with col4:
    st.metric("🛍️ Avg Order Value", f"R$ {aov:,.0f}")
with col5:
    st.metric("👤 Avg Customer Value", f"R$ {acv:,.0f}")

st.markdown("---")

# ============================================================
# TABS UTAMA
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Sales Overview",
    "👥 RFM Segmentation",
    "🗺️ Geographic Analysis",
    "📦 Category Analysis",
    "📋 Data Details"
])

# ──────────────────────────────────────────────────────────────
# TAB 1: SALES OVERVIEW
# ──────────────────────────────────────────────────────────────
with tab1:
    st.header("📈 Ringkasan Penjualan 2018")

    monthly = (
        filtered
        .groupby('order_month_dt')
        .agg(revenue=('payment_value', 'sum'), orders=('order_id', 'nunique'))
        .reset_index()
    )
    monthly['aov'] = monthly['revenue'] / monthly['orders']
    monthly['month_label'] = monthly['order_month_dt'].dt.strftime('%b %Y')

    col1, col2 = st.columns(2)

    with col1:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=monthly['month_label'], y=monthly['revenue']/1e6,
            name='Revenue (Juta R$)',
            marker_color='rgba(57,73,171,0.75)'
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=monthly['month_label'], y=monthly['orders'],
            name='Jumlah Order', mode='lines+markers',
            line=dict(color='#E53935', width=3)
        ), secondary_y=True)
        fig.update_layout(
            title='💹 Revenue Bulanan & Volume Order',
            hovermode='x unified', template='plotly_white', height=400
        )
        fig.update_yaxes(title_text="Revenue (Juta R$)", secondary_y=False)
        fig.update_yaxes(title_text="Order Count", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        status_data = filtered['order_status'].value_counts().reset_index()
        status_data.columns = ['status', 'count']
        fig2 = px.pie(
            status_data, values='count', names='status',
            title='📊 Distribusi Status Order',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.45
        )
        fig2.update_traces(textposition='inside', textinfo='percent+label')
        fig2.update_layout(height=400, template='plotly_white')
        st.plotly_chart(fig2, use_container_width=True)

    # AOV Trend
    fig3 = px.area(
        monthly, x='month_label', y='aov',
        title='📉 Tren Average Order Value (AOV) Bulanan',
        markers=True, color_discrete_sequence=['#3949AB']
    )
    fig3.update_layout(height=320, template='plotly_white', hovermode='x')
    fig3.update_yaxes(title_text="AOV (R$)")
    fig3.update_xaxes(title_text="Bulan")
    st.plotly_chart(fig3, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# TAB 2: RFM SEGMENTATION
# ──────────────────────────────────────────────────────────────
with tab2:
    st.header("👥 RFM Customer Segmentation")
    st.caption("Menjawab Pertanyaan Bisnis 1: Distribusi segmen pelanggan dan kontribusi revenue per segmen tahun 2018.")

    # Hanya ambil baris yang punya segmen (customer yang ada di rfm_segments)
    fws = filtered_with_seg.dropna(subset=['segment'])

    if fws.empty:
        st.warning("⚠️ Tidak ada data segmen untuk filter yang dipilih. "
                   "Coba perluas rentang tanggal atau hapus filter lain.")
    else:
        seg_summary = (
            fws
            .groupby('segment')
            .agg(
                pelanggan=('customer_id', 'nunique'),
                orders   =('order_id',   'nunique'),
                revenue  =('payment_value', 'sum')
            )
            .reset_index()
            .sort_values('revenue', ascending=False)
        )

        COLORS = {
            'Champions': '#2ECC71', 'Loyal Customers': '#27AE60',
            'Potential Loyalists': '#F39C12', 'Recent Customers': '#3498DB',
            "Can't Lose Them": '#9B59B6', 'At Risk': '#E67E22',
            'Need Attention': '#95A5A6', 'Lost': '#E74C3C'
        }
        seg_summary['color'] = seg_summary['segment'].map(COLORS).fillna('#BDC3C7')

        col1, col2 = st.columns(2)

        with col1:
            fig_pie = px.pie(
                seg_summary, values='pelanggan', names='segment',
                title='📊 Distribusi Pelanggan per Segmen',
                color='segment',
                color_discrete_map=COLORS,
                hole=0.4
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=400, template='plotly_white')
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            fig_rev = px.bar(
                seg_summary,
                x='revenue', y='segment',
                orientation='h',
                title='💰 Kontribusi Revenue per Segmen',
                color='revenue',
                color_continuous_scale='Blues',
                text_auto='.2s'
            )
            fig_rev.update_layout(height=400, template='plotly_white',
                                   coloraxis_showscale=False)
            fig_rev.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig_rev, use_container_width=True)

        # Heatmap profil RFM per segmen
        st.subheader("🔬 Profil RFM per Segmen")
        rfm_profile = (
            rfm_segments[rfm_segments['segment'].isin(seg_summary['segment'])]
            .groupby('segment')[['recency','frequency','monetary']]
            .mean()
            .round(1)
        )
        # Normalize
        rfm_norm = (rfm_profile - rfm_profile.min()) / (rfm_profile.max() - rfm_profile.min())
        rfm_norm['recency'] = 1 - rfm_norm['recency']   # Balik: recency kecil = baik

        fig_heat = px.imshow(
            rfm_norm.T,
            text_auto=False,
            color_continuous_scale='RdYlGn',
            title='Normalized RFM Score per Segmen (Hijau = Lebih Baik)',
            aspect='auto'
        )
        # Tambah anotasi nilai asli
        for i, row_name in enumerate(rfm_profile.columns):
            for j, seg in enumerate(rfm_profile.index):
                fig_heat.add_annotation(
                    x=j, y=i,
                    text=str(rfm_profile.loc[seg, row_name]),
                    showarrow=False, font=dict(size=11, color='black')
                )
        fig_heat.update_layout(height=280, template='plotly_white')
        st.plotly_chart(fig_heat, use_container_width=True)

        # Tabel ringkasan
        st.subheader("📋 Ringkasan Karakteristik Segmen")
        display_seg = seg_summary[['segment', 'pelanggan', 'orders', 'revenue']].copy()
        display_seg['revenue_share_%'] = (display_seg['revenue'] /
                                          display_seg['revenue'].sum() * 100).round(1)
        display_seg['revenue'] = display_seg['revenue'].map('R$ {:,.0f}'.format)
        st.dataframe(display_seg, use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────────────────────
# TAB 3: GEOGRAPHIC ANALYSIS
# ──────────────────────────────────────────────────────────────
with tab3:
    st.header("🗺️ Geographic Distribution Analysis")
    st.caption("Menjawab Pertanyaan Bisnis 2: Top 5 kota dengan AOV tertinggi dan distribusi geografis revenue.")

    city_agg = (
        filtered
        .groupby('customer_city')
        .agg(
            pelanggan=('customer_id', 'nunique'),
            orders   =('order_id',   'nunique'),
            revenue  =('payment_value', 'sum')
        )
        .reset_index()
    )
    city_agg['aov'] = city_agg['revenue'] / city_agg['orders']

    col1, col2 = st.columns(2)

    with col1:
        # TOP 5 by AOV
        top5_aov = (
            city_agg[city_agg['pelanggan'] >= 50]
            .sort_values('aov', ascending=False)
            .head(5)
        )
        fig_aov = px.bar(
            top5_aov,
            x='aov', y='customer_city',
            orientation='h',
            title='🏆 Top 5 Kota — Average Order Value Tertinggi\n(min. 50 pelanggan)',
            color='aov',
            color_continuous_scale='YlOrRd',
            text_auto='.0f'
        )
        fig_aov.update_layout(height=360, template='plotly_white',
                               coloraxis_showscale=False,
                               yaxis={'categoryorder': 'total ascending'})
        fig_aov.update_xaxes(title_text='Avg Order Value (R$)')
        fig_aov.update_yaxes(title_text='Kota')
        st.plotly_chart(fig_aov, use_container_width=True)

    with col2:
        # TOP 15 by Revenue
        top15_rev = city_agg.sort_values('revenue', ascending=False).head(15)
        fig_rev = px.bar(
            top15_rev,
            x='revenue', y='customer_city',
            orientation='h',
            title='💰 Top 15 Kota — Total Revenue',
            color='revenue',
            color_continuous_scale='Blues',
            text_auto='.2s'
        )
        fig_rev.update_layout(height=460, template='plotly_white',
                               coloraxis_showscale=False,
                               yaxis={'categoryorder': 'total ascending'})
        fig_rev.update_xaxes(title_text='Total Revenue (R$)')
        st.plotly_chart(fig_rev, use_container_width=True)

    # Revenue by State
    state_agg = (
        filtered
        .groupby('customer_state')
        .agg(revenue=('payment_value', 'sum'), pelanggan=('customer_id', 'nunique'))
        .reset_index()
        .sort_values('revenue', ascending=False)
        .head(15)
    )
    fig_state = px.bar(
        state_agg,
        x='customer_state', y='revenue',
        title='📍 Revenue per Provinsi (State) — Top 15',
        color='revenue',
        color_continuous_scale='Plasma',
        text_auto='.2s',
        labels={'customer_state': 'State', 'revenue': 'Total Revenue (R$)'}
    )
    fig_state.update_layout(height=380, template='plotly_white', showlegend=False)
    st.plotly_chart(fig_state, use_container_width=True)

    # Bubble chart
    st.subheader("📊 Pola AOV vs Volume Pelanggan (Bubble = Total Revenue)")
    bubble_data = city_agg[city_agg['pelanggan'] >= 20].nlargest(30, 'revenue')
    fig_bubble = px.scatter(
        bubble_data,
        x='pelanggan', y='aov',
        size='revenue', color='revenue',
        hover_name='customer_city',
        color_continuous_scale='YlOrRd',
        labels={'pelanggan': 'Jumlah Pelanggan', 'aov': 'Avg Order Value (R$)'},
        title='Kota Besar vs AOV — Temukan Peluang Pasar Tersembunyi'
    )
    fig_bubble.update_layout(height=420, template='plotly_white')
    st.plotly_chart(fig_bubble, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# TAB 4: CATEGORY ANALYSIS
# ──────────────────────────────────────────────────────────────
with tab4:
    st.header("📦 Product Category Performance")

    cat_agg = (
        filtered
        .groupby('product_category_name_english')
        .agg(orders=('order_id', 'nunique'), revenue=('payment_value', 'sum'))
        .reset_index()
        .sort_values('revenue', ascending=False)
    )
    cat_agg['aov']        = cat_agg['revenue'] / cat_agg['orders']
    cat_agg['rev_share%'] = (cat_agg['revenue'] / cat_agg['revenue'].sum() * 100).round(2)

    top15 = cat_agg.head(15)

    col1, col2 = st.columns(2)

    with col1:
        fig_c1 = px.bar(
            top15,
            x='revenue', y='product_category_name_english',
            orientation='h',
            title='💰 Top 15 Kategori — Revenue',
            color='revenue', color_continuous_scale='Reds', text_auto='.2s'
        )
        fig_c1.update_layout(height=500, template='plotly_white',
                              coloraxis_showscale=False,
                              yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_c1, use_container_width=True)

    with col2:
        fig_c2 = px.bar(
            top15,
            x='orders', y='product_category_name_english',
            orientation='h',
            title='📦 Top 15 Kategori — Volume Order',
            color='orders', color_continuous_scale='Greens', text_auto='d'
        )
        fig_c2.update_layout(height=500, template='plotly_white',
                              coloraxis_showscale=False,
                              yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_c2, use_container_width=True)

    # Treemap
    st.subheader("🌳 Treemap Pangsa Revenue per Kategori")
    fig_tree = px.treemap(
        cat_agg.head(20),
        path=['product_category_name_english'],
        values='revenue',
        color='aov',
        color_continuous_scale='RdYlGn',
        title='Treemap Revenue & AOV — Top 20 Kategori',
        hover_data={'rev_share%': True, 'aov': ':.0f'}
    )
    fig_tree.update_layout(height=450)
    st.plotly_chart(fig_tree, use_container_width=True)

    # Tabel
    st.subheader("📊 Tabel Lengkap Performa Kategori")
    display_cat = cat_agg.copy()
    display_cat['revenue'] = display_cat['revenue'].map('R$ {:,.0f}'.format)
    display_cat['aov']     = display_cat['aov'].map('R$ {:,.0f}'.format)
    st.dataframe(display_cat, use_container_width=True, hide_index=True, height=350)

# ──────────────────────────────────────────────────────────────
# TAB 5: DATA DETAILS
# ──────────────────────────────────────────────────────────────
with tab5:
    st.header("📋 Transaksi Detail")

    col1, col2, col3 = st.columns(3)
    with col1:
        rows_to_show = st.slider("Jumlah baris", 10, 200, 50)
    with col2:
        sort_by = st.selectbox("Urutkan berdasarkan",
                               ['Terbaru', 'Nilai Tertinggi', 'Nilai Terendah'])
    with col3:
        search_city = st.text_input("Cari kota", placeholder="Contoh: sao paulo")

    disp = filtered.copy()
    if search_city:
        disp = disp[disp['customer_city'].str.contains(search_city, case=False, na=False)]

    if sort_by == 'Terbaru':
        disp = disp.sort_values('order_purchase_timestamp', ascending=False)
    elif sort_by == 'Nilai Tertinggi':
        disp = disp.sort_values('payment_value', ascending=False)
    else:
        disp = disp.sort_values('payment_value', ascending=True)

    show_cols = ['order_id', 'customer_id', 'order_purchase_timestamp',
                 'customer_city', 'customer_state',
                 'product_category_name_english', 'payment_value', 'order_status']
    st.dataframe(
        disp[show_cols].head(rows_to_show),
        use_container_width=True, height=420
    )

    st.subheader("📥 Export Data")
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        csv = disp[show_cols].to_csv(index=False)
        st.download_button(
            "📥 Download Filtered Data (CSV)",
            data=csv,
            file_name="ecommerce_filtered_data.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_dl2:
        if 'segment' in filtered_with_seg.columns:
            rfm_export = rfm_segments.to_csv(index=False)
            st.download_button(
                "📥 Download RFM Segments (CSV)",
                data=rfm_export,
                file_name="rfm_segments.csv",
                mime="text/csv",
                use_container_width=True
            )

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align:center; color:#9E9E9E; font-size:12px; padding:1rem;'>
        📊 <b>E-Commerce Analytics Dashboard</b> &nbsp;|&nbsp;
        Analisis Data E-Commerce Brazil 2018 &nbsp;|&nbsp;
        Dibuat menggunakan Python · Pandas · Plotly · Streamlit<br>
        <i>Dicoding — Belajar Analisis Data dengan Python | Final Project</i>
    </div>
    """,
    unsafe_allow_html=True
)
