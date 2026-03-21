from supabase import create_client, Client
from app.config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY

# Public client (uses anon key — respects RLS)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Service client (bypasses RLS — for backend-only operations)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
