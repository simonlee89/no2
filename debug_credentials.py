import json
import logging
import os

logging.basicConfig(level=logging.DEBUG)

credentials = os.environ.get('GOOGLE_CREDENTIALS')
logging.debug("Credentials type: %s", type(credentials))
logging.debug("Credentials content: %s", credentials)

try:
    if isinstance(credentials, str):
        cred_info = json.loads(credentials)
        logging.debug("Service Account Email: %s", cred_info.get('client_email', 'Not found'))
except Exception as e:
    logging.error("Error parsing credentials: %s", str(e))
