import os

# Tokens for user role registration
ROLE_TOKENS = {
    "Admin": os.getenv("ADMIN_TOKEN"),
    "Editor": os.getenv("EDITOR_TOKEN"),
    "Viewer": os.getenv("VIEWER_TOKEN"),
}

# AliExpress Affiliate API key
AFFILIATE_APP_KEY = os.getenv("AFFILIATE_APP_KEY")