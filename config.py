
import os

# Google Sheets Configuration
SPREADSHEET_ID = "1C0-kWVHt_SvWIPfmCzKVOKr0pMFArixYNNhNw-vdCoE"
SHEET_RANGES = {
    '강남월세': "'[강남월세]'!A5:R",
    '강남전세': "'[강남전세]'!A5:R",
    '송파월세': "'[송파월세]'!A5:R",
    '송파전세': "'[송파전세]'!A5:R"
}

# Google Service Account Credentials
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")

# Naver Maps API Configuration
NAVER_CLIENT_ID = "l9h74kh0v2"
NAVER_CLIENT_SECRET = "uKth8NuQbVW2qAYlizyA7ZJX5FJfuxDa6"
