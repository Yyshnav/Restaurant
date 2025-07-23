import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Replace with your actual service account path
SERVICE_ACCOUNT_FILE = 'ichat-1b6d6-firebase-adminsdk-pndsj-d04ef131bb.json'

def get_access_token():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/firebase.messaging"]
    )
    credentials.refresh(Request())
    return credentials.token

def send_fcm_notification(token, title, body):
    access_token = get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; UTF-8",
    }

    message = {
        "message": {
            "token": token,
            "notification": {
                "title": title,
                "body": body
            }
        }
    }

    project_id = "ichat-1b6d6"  # Check this in Firebase > Project settings
    url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

    response = requests.post(url, headers=headers, data=json.dumps(message))
    return {
        'status_code': response.status_code,
        'response': response.json() if response.content else {}
    }