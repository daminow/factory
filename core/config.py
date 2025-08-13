import os

# Platforms list (comma-separated)
PLATFORMS = os.getenv("PLATFORMS", "vk,tiktok,instagram,telegram").split(",")

# AliExpress Affiliate API key
AFFILIATE_APP_KEY = os.getenv("AFFILIATE_APP_KEY")