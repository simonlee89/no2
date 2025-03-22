import json
import logging
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import SPREADSHEET_ID, SHEET_RANGES, GOOGLE_CREDENTIALS

logging.basicConfig(level=logging.INFO)

def determine_status(q_value, sheet_type):
    """
    Q열 값을 바탕으로 갠매 여부만 판단하는 함수
    """
    if not q_value:
        return '일반'

    # 앞뒤 공백 및 non-breaking space 제거
    normalized = q_value.strip().replace('\u00A0', '').strip()

    # 시트별 상태 판정 로직
    if sheet_type == '강남월세':
        if re.search(r'갠\s*매', normalized):
            logging.info(f"갠매 발견: '{normalized}'")
            return '갠매'
    elif sheet_type == '강남전세':
        if re.search(r'직\s*거\s*래|개\s*인|갠\s*매', normalized):
            logging.info(f"갠매/직거래/개인 발견: '{normalized}'")
            return '갠매'
    elif sheet_type == '송파월세':
        if re.search(r'갠\s*매', normalized):
            logging.info(f"갠매 발견: '{normalized}'")
            return '갠매'
    elif sheet_type == '송파전세':
        if re.search(r'갠\s*매', normalized):
            logging.info(f"갠매 발견: '{normalized}'")
            return '갠매'

    return '일반'

def get_sheets_service():
    try:
        credentials_info = json.loads(GOOGLE_CREDENTIALS) if isinstance(GOOGLE_CREDENTIALS, str) else GOOGLE_CREDENTIALS
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        return build('sheets', 'v4', credentials=credentials)
    except Exception as e:
        logging.error(f"Failed to create sheets service: {str(e)}")
        raise

def get_property_data(sheet_type='강남월세'):
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()

        range_name = "'[강남전세]'!A5:R" if sheet_type == '강남전세' else SHEET_RANGES.get(sheet_type)
        if not range_name:
            logging.error(f"Invalid sheet type: {sheet_type}")
            return []

        logging.debug(f"Attempting to fetch data with range: {range_name}")
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name
        ).execute()

        values = result.get('values', [])
        if not values:
            return []

        properties = []
        status_counts = {'갠매': 0, '일반': 0}

        logging.info(f"{sheet_type} 데이터 처리 시작")

        for row in values:
            try:
                if len(row) < 17:  # Q열(16)까지 필요
                    continue

                property_id = row[0].strip()
                reg_date = row[1].strip() if len(row) > 1 else ''
                location = row[15].strip()
                q_value = str(row[16]).strip() if len(row) > 16 else ''

                if not property_id or not location:
                    continue

                status = determine_status(q_value, sheet_type)
                status_counts[status] += 1

                property_data = {
                    'id': property_id,
                    'reg_date': reg_date,
                    'hyperlink': f"https://new.land.naver.com/houses?articleNo={property_id}",
                    'location': location,
                    'status': status,
                    'deposit': row[9].strip() if len(row) > 9 else '',
                    'monthly_rent': row[10].strip() if len(row) > 10 else ''
                }

                properties.append(property_data)

            except Exception as e:
                logging.error(f"Error processing row: {str(e)}")
                continue

        logging.info("\n=== 처리 결과 요약 ===")
        logging.info(f"총 매물 수: {len(properties)}개")
        logging.info(f"갠매: {status_counts['갠매']}개")
        logging.info(f"일반: {status_counts['일반']}개")

        return properties

    except Exception as e:
        logging.error(f"Failed to fetch property data: {str(e)}")
        return []