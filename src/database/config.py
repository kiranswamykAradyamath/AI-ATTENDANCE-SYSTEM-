import os
import streamlit as st

from supabase import create_client, Client

# Retrieve Supabase credentials safely
supabase_url = None
supabase_key = None

# First, try Streamlit secrets
try:
    if "SUPABASE_URL" in st.secrets:
        supabase_url = st.secrets["SUPABASE_URL"]
    if "SUPABASE_KEY" in st.secrets:
        supabase_key = st.secrets["SUPABASE_KEY"]
except Exception:
    pass

# Fallback to environment variables
if not supabase_url:
    supabase_url = os.environ.get("SUPABASE_URL")
if not supabase_key:
    supabase_key = os.environ.get("SUPABASE_KEY")

# Fallback placeholders to prevent startup crashes if not configured yet
if not supabase_url:
    supabase_url = "https://placeholder-please-configure.supabase.co"
if not supabase_key:
    supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZpa3l1Z2d2d3huZG9qbXdmbHZmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzczNDY3MDEsImV4cCI6MjA5MjkyMjcwMX0.yh4BJZS9deInj_dLoKwXUgZTSRqNNnlzO2skhgpTB64"

supabase: Client = create_client(supabase_url, supabase_key)