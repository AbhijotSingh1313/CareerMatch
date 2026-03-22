import httpx
import warnings

# ─── Disable SSL verification for corporate/college proxy networks ───
# The Supabase SDK uses httpx internally. On networks with self-signed
# certificates in the chain, SSL verification fails. This monkey-patches
# httpx to skip verification by default.
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

_orig_client_init = httpx.Client.__init__

def _patched_client_init(self, *args, **kwargs):
    kwargs.setdefault("verify", False)
    _orig_client_init(self, *args, **kwargs)

httpx.Client.__init__ = _patched_client_init

# ─── Now create Supabase clients ───
from supabase import create_client, Client
from app.config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY

# Public client (uses anon key — respects RLS)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Service client (bypasses RLS — for backend-only operations)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
