from supabase import create_client, Client

# --- CONFIGURACIÓN DE SUPABASE ---
# Reemplaza con tus credenciales reales si cambian
SUPABASE_URL = "https://yuaxnqjqxrmahlmlbujj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl1YXhucWpxeHJtYWhsbWxidWpqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3OTE2NjE1NCwiZXhwIjoyMDk0NzQyMTU0fQ.Ogh2OkTGlrEFSRkSJAmQCl1f94_iiBYKpYoxy04_-Sc"

_supabase: Client = None

def get_supabase_client() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase
