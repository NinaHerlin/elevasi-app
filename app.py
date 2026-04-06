import streamlit as st
import pickle
import numpy as np
from utils.sheets import save_to_sheets
import datetime
import sklearn

# =========================
# CONFIG PAGE
# =========================
st.set_page_config(
    page_title="Prediksi Elevasi Muka Air Pori",
    page_icon="🌊",
    layout="centered"
)

# =========================
# LOAD CUSTOM CSS
# =========================
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# =========================
# LOAD MODEL (CACHE PENGGUNAAN MEMORI)
# =========================
@st.cache_resource(show_spinner="Memuat model Machine Learning...")
def load_all_models():
    models = {}
    model_names = ["F2B", "F2R", "F3B", "F3R", "F5B", "F5R", "F8G", "F11G", "F11N", "F11R"]
    for name in model_names:
        with open(f'model/gbr_model_{name}.pkl', 'rb') as f:
            models[name] = pickle.load(f)
    return models

models_dict = None
load_error = None
try:
    models_dict = load_all_models()
except Exception as e:
    load_error = e

if load_error:
    st.title("⚠️ Gagal Memuat Model")
    st.error(
        "Gagal memuat model Machine Learning. Ini biasanya terjadi karena versi scikit-learn saat ini "
        f"({sklearn.__version__}) berbeda dari versi yang digunakan untuk menyimpan model."
    )
    st.markdown(
        "Silakan gunakan lingkungan Python dan scikit-learn yang sama dengan model, atau buat ulang file model `*.pkl` "
        "dengan versi yang terpasang saat ini."
    )
    st.exception(load_error)
    st.stop()

# =========================
# TITLE & PANDUAN
# =========================
st.title("🌊 Prediksi Elevasi Muka Air Pori")

with st.expander("ℹ️ **Petunjuk Penggunaan** (Klik untuk membuka)"):
    st.markdown("""
    Aplikasi ini menggunakan model **Machine Learning** untuk memprediksi elevasi muka air pori (mdpl) berdasarkan data pembacaan piezometer.
    
    **Langkah-langkah:**
    1. Masukkan data real-time **TMA Waduk** dan **Curah Hujan** historis (H-1 hingga H-3).
    2. Pilih target **Titik Prediksi**.
    3. Masukkan data historis elevasi titik tersebut 2 hari ke belakang.
    4. Klik **Prediksi Sekarang** untuk melihat estimasi analisis muka air pori secara cepat.
    """)

st.divider()

# =========================
# FORM INPUT (Mencegah reload otomatis tiap ketikan)
# =========================
with st.form("prediction_form"):
    st.subheader("Input Data Umum")
    
    col1, col2 = st.columns(2)
    with col1:
        tma = st.number_input("TMA Waduk (Mdpl)", value=100.0)
    with col2:
        rain_1 = st.number_input("Curah Hujan t-1", value=0.0)
        
    col3, col4 = st.columns(2)
    with col3:
        rain_2 = st.number_input("Curah Hujan t-2", value=0.0)
    with col4:
        rain_3 = st.number_input("Curah Hujan t-3", value=0.0)

    st.divider()

    # PILIH MODEL
    st.subheader("Pilih Titik Prediksi Piezometer Casagrade")
    selected_model = st.selectbox(
        "", 
        ["F2B", "F2R", "F3B", "F3R", "F5B", "F5R", "F8G", "F11G", "F11N", "F11R"]
    )

    # INPUT DINAMIS
    st.subheader("Input Historis Elevasi Muka Air Pori (Mdpl)")
    col5, col6 = st.columns(2)
    with col5:
        f1 = st.number_input(f"Lag t-1", value=100.0)
    with col6:
        f2 = st.number_input(f"Lag t-2", value=100.0)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # SUBMIT FORM
    submitted = st.form_submit_button("Prediksi Sekarang")

# =========================
# PROSES PREDIKSI & UI/UX EFFECTS
# =========================
if submitted:
    try:
        with st.spinner("System sedang menganalisis pola data Anda..."):
            
            input_data = np.array([[tma, rain_1, rain_2, rain_3, f1, f2]])

            if selected_model in models_dict:
                prediction = models_dict[selected_model].predict(input_data)[0]

        # =========================
        # OUTPUT
        # =========================
        st.subheader("Hasil Analisis Prediksi")

        st.metric(
            label=f"Estimasi Elevasi {selected_model}",
            value=f"{prediction:.2f} mdpl"
        )
        
        # Toast notification interaktif (muncul di pojok bawah)
        st.toast('Analisis berhasil! Sedang menyimpan data ke Cloud...', icon='✅')

        # =========================
        # SIMPAN KE GOOGLE SHEETS
        # =========================
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        save_to_sheets([
            timestamp,
            selected_model,
            tma,
            rain_1,
            rain_2,
            rain_3,
            f1,
            f2,
            float(prediction)
        ])

        st.success("**Selesai!** Data prediksi berhasil disimpan ke sistem (Google Sheets).")

    except Exception as e:
        st.error(f"Terjadi kesalahan pada sistem: {e}")