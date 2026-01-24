from supabase import create_client, Client

# --- CONFIGURACIÓN DE SUPABASE ---
# Reemplaza con tus credenciales reales si cambian
SUPABASE_URL = "https://kdgjkiptelkrzahmfafi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtkZ2praXB0ZWxrcnphaG1mYWZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgwMTg3OTgsImV4cCI6MjA4MzU5NDc5OH0.QUz5Z3OGQ4a44zhQ4Xokbpc5AKDP4sSmFsJwftTsSUI"

_supabase: Client = None

def get_supabase_client() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase
