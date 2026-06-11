import streamlit as st

from supabase import create_client, Client

_SUPABASE_KEY_NAMES = ("SUPABASE_KEY", "SUPABASE_ANON_KEY")


def _get_secret(name):
    value = st.secrets.get(name)
    return value.strip() if isinstance(value, str) else value


supabase_url = _get_secret("SUPABASE_URL")
supabase_key = None
for key_name in _SUPABASE_KEY_NAMES:
    supabase_key = _get_secret(key_name)
    if supabase_key:
        break

if not supabase_url or not supabase_key:
    st.error(
        "Supabase is not configured. Add SUPABASE_URL and SUPABASE_KEY "
        "or SUPABASE_ANON_KEY to Streamlit secrets."
    )
    st.stop()

supabase: Client = create_client(supabase_url, supabase_key)

