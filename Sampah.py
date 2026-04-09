import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import folium_static
from folium.plugins import Fullscreen, MeasureControl

st.set_page_config(layout="wide", page_title="Dashboard Bank Sampah Surabaya")

st.title("🗑️ **Dashboard Bank Sampah KOTA SURABAYA**")
st.markdown("**Peta Interaktif + Statistik + Filter Wilayah**")

@st.cache_data
def load_data():
    """DATA 12 BANK SAMPAH KOTA SURABAYA - SEMUA 12 ITEMS ✅"""
    data = pd.DataFrame({
        'nama': ['Bank Sampah Induk', 'Bank Sampah Barokah', 'Bank Sampah Wani', 
                'Bank Sampah Rukun Jaya', 'Bank Sampah Dinoyo Resik', 'Bank Sampah Dinoyo', 
                'Bank Sampah Sektoral', 'Bank Sampah Bintang Mangrove', 'Bank Sampah Pelita', 
                'Bank Sampah Cahaya Asia', 'Bank Sampah Ngagel', 'Bank Sampah JW Project'],
        'lat': [-7.2755, -7.2641, -7.2134, -7.3097, -7.2776, -7.2355, 
                -7.3142, -7.3428, -7.3436, -7.2653, -7.2854, -7.3101],
        'lon': [112.7631, 112.7353, 112.7320, 112.7118, 112.7451, 112.7753, 
                112.6814, 112.8076, 112.8007, 112.7118, 112.7471, 112.7358],
        'alamat': ['Jl. Raya Menur No.31-A', 'Jl. Surabayan III No.28', 'Jl. Tlk. Aru IV POS No.9', 
                  'RT.03/RW.04', 'Jl. Jambangan No.1', 'Jl. Dinoyo Gang 10', 'Jl. Dukuh Setro VIII No.8', 
                  'Jl. Babatan Pilang XIV/G1 no.15', 'Kawasan Mangrove Gununganyar', 'Jl. Gn. Anyar Tambak No.3', 
                  'Jl. Simo Kalangan Baru No.6', 'PP7W+2VH'],
        'kelurahan': ['Manyar Sabrangan', 'Kedungdoro', 'Perak Utara', 'Jambangan', 
                     'Keputran', 'Dinoyo', 'Babatan', 'Gn. Anyar Tambak', 'Gn. Anyar Tambak', 
                     'Simomulyo', 'Ngagel', 'Margorejo'],
        'kecamatan': ['Mulyorejo', 'Tegalsari', 'Pabean Cantian', 'Jambangan', 'Tegalsari', 
                     'Tambaksari', 'Wiyung', 'Gn. Anyar', 'Gn. Anyar', 'Sukomanunggal', 
                     'Wonokromo', 'Wonocolo'],
        'volume_harian': [1500, 2200, 800, 1800, 1200, 900, 1600, 2000, 2500, 1100, 1300, 1700],
        'jenis_sampah': ['Plastik', 'Plastik', 'Kertas', 'Plastik', 'Organik', 'Kertas', 
                        'Plastik', 'Organik', 'Plastik', 'Kertas', 'Plastik', 'Organik'],
        'status': ['Aktif', 'Aktif', 'Aktif', 'Aktif', 'Aktif', 'Aktif', 'Aktif', 'Aktif', 
                  'Aktif', 'Aktif', 'Aktif', 'Aktif']
    })
    return data

df = load_data()

# SIDEBAR FILTER ✅ SAFE DEFAULT
st.sidebar.header("🔍 **Filter**")
kecamatan = st.sidebar.multiselect("Kecamatan", df['kecamatan'].unique(), default=df['kecamatan'].unique())
jenis = st.sidebar.multiselect("Jenis Sampah", df['jenis_sampah'].unique(), default=df['jenis_sampah'].unique())

df_filtered = df[df['kecamatan'].isin(kecamatan) & df['jenis_sampah'].isin(jenis)]

# METRICS
col1, col2, col3, col4 = st.columns(4)
col1.metric("🏭 Total Bank Sampah", len(df_filtered))
col2.metric("📈 Volume Harian", f"{df_filtered['volume_harian'].sum():,} kg")
col3.metric("✅ Aktif", len(df_filtered[df_filtered['status']=='Aktif']))
col4.metric("🥇 Terbesar", f"{df_filtered['volume_harian'].max():,} kg")

st.markdown("---")

# DASHBOARD LAYOUT
col_left, col_right = st.columns([2, 1])

# Di dalam col_left (bagian peta):
with col_left:
    st.header("🗺️ **Peta Bank Sampah Surabaya**")
    
    # Map Surabaya + Fullscreen
    m = folium.Map(
        location=[-7.28, 112.75], 
        zoom_start=11,
        tiles="OpenStreetMap"
    )
    
    # FULLSCREEN BUTTON ✅
    from folium.plugins import Fullscreen
    Fullscreen(position="topright").add_to(m)
    
    # MARKERS Bank Sampah
    for idx, row in df_filtered.iterrows():
        folium.Marker(
            [row['lat'], row['lon']],
            popup=f"""
            <b>{row['nama']}</b><br>
            <b>{row['alamat']}</b><br>
            📊 {row['volume_harian']:,} kg/hari<br>
            {row['kelurahan']}, {row['kecamatan']}
            """,
            tooltip=row['nama'],
            icon=folium.Icon(color="green", icon="recycle")
        ).add_to(m)
    
    # ✅ FIXED - NO returned_objects
    folium_static(m, width="100%", height=600)

with col_right:
    st.header("📊 **Statistik**")
    
    # Pie Chart
    fig_pie = px.pie(df_filtered, names='jenis_sampah', values='volume_harian', 
                    title="Komposisi Sampah")
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Bar Chart
    kec_vol = df_filtered.groupby('kecamatan')['volume_harian'].sum().reset_index()
    fig_bar = px.bar(kec_vol, x='kecamatan', y='volume_harian', 
                    title="Volume per Kecamatan")
    st.plotly_chart(fig_bar, use_container_width=True)

# TABEL
st.header("📋 **Data Lengkap**")
st.dataframe(df_filtered, use_container_width=True)

# DOWNLOAD
csv = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button("💾 Download CSV", csv, "bank_sampah_surabaya.csv", "text/csv")

with st.expander("ℹ️ Update Data"):
    st.write("**Tambah data baru:** Edit `load_data()` → Commit → Auto-update!")
