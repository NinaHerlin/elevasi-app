import os
import json
import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

# =========================
# CONFIG
# =========================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

LOCAL_CRED_PATH = os.path.join("credentials", "service_account.json")

# 🔥 FIX NAMA SPREADSHEET
SPREADSHEET_NAME = "Data Prediksi Elevasi"


# =========================
# GET CREDENTIALS (ANTI ERROR)
# =========================
def _get_credentials():

    # 🔥 1. Coba Streamlit Secrets (DEPLOY)
    try:
        if "gcp_service_account" in st.secrets:
            return ServiceAccountCredentials.from_json_keyfile_dict(
                st.secrets["gcp_service_account"], scope
            )
    except Exception:
        pass  # kalau secrets belum ada di lokal → lanjut

    # 🟡 2. ENV VARIABLE
    sa_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if sa_json:
        try:
            sa_dict = json.loads(sa_json)
            return ServiceAccountCredentials.from_json_keyfile_dict(sa_dict, scope)
        except json.JSONDecodeError as exc:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON bukan JSON valid") from exc

    # 💻 3. LOCAL FILE (INI YANG DIPAKAI DI LAPTOP KAMU)
    if os.path.exists(LOCAL_CRED_PATH):
        return ServiceAccountCredentials.from_json_keyfile_name(
            LOCAL_CRED_PATH, scope
        )

    raise FileNotFoundError(
        "❌ Credentials tidak ditemukan.\n"
        "- Gunakan Streamlit Secrets (production)\n"
        "- Atau ENV GOOGLE_SERVICE_ACCOUNT_JSON\n"
        "- Atau file lokal credentials/service_account.json"
    )


# =========================
# CONNECT
# =========================
creds = _get_credentials()
client = gspread.authorize(creds)

try:
    sheet = client.open(SPREADSHEET_NAME).sheet1
except Exception as e:
    raise Exception(
        f"❌ Gagal membuka spreadsheet '{SPREADSHEET_NAME}'.\n"
        f"Pastikan:\n"
        f"- Nama spreadsheet sama persis\n"
        f"- Sudah di-share ke service account\n\n"
        f"Error: {e}"
    )


# =========================
# SAVE FUNCTION
# =========================
def save_to_sheets(data):
    try:
        all_data = sheet.get_all_values()
        next_row = len(all_data) + 1

        sheet.update(f"A{next_row}", [data])

    except Exception as e:
        print("❌ Error saving to sheets:", e)
        raise