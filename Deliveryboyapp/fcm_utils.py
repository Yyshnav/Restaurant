# import json
# import requests
# from google.oauth2 import service_account
# from google.auth.transport.requests import Request

# SERVICE_ACCOUNT_FILE = 'dinetime-62391-firebase-adminsdk-fbsvc-c71a48d528.json'

# def get_access_token():
#     credentials = service_account.Credentials.from_service_account_file(
#         SERVICE_ACCOUNT_FILE,
#         scopes=["https://www.googleapis.com/auth/firebase.messaging"]
#     )
#     credentials.refresh(Request())
#     return credentials.token

# def send_fcm_notification(token, title, body):
#     access_token = get_access_token()

#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json; UTF-8",
#     }

#     message = {
#         "message": {
#             "token": token,
#             "notification": {
#                 "title": title,
#                 "body": body
#             }
#         }
#     }

#     project_id = "dinetime-62391"  
#     url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

#     response = requests.post(url, headers=headers, data=json.dumps(message))
#     return {
#         'status_code': response.status_code,
#         'response': response.json() if response.content else {}
#     }

# import os
# import json
# import requests
# from google.oauth2 import service_account
# from google.auth.transport.requests import Request

# # -------------------------------
# # Path to Firebase Service Account
# # -------------------------------
# # Make sure your JSON file is in your Django project, e.g.:
# # myproject/credentials/dinetime-62391-firebase-adminsdk-fbsvc-c71a48d528.json

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# SERVICE_ACCOUNT_FILE = r"D:\TryCodeWp\RESTAURANT\Restaurant\Restaurant\credentials\dinetime-62391-firebase-adminsdk-fbsvc-db5549a1cb.json"


# # -------------------------------
# # Get access token from Firebase
# # -------------------------------
# def get_access_token():
#     credentials = service_account.Credentials.from_service_account_file(
#         SERVICE_ACCOUNT_FILE,
#         scopes=["https://www.googleapis.com/auth/firebase.messaging"]
#     )
#     credentials.refresh(Request())
#     return credentials.token

# # -------------------------------
# # Send FCM notification
# # -------------------------------
# def send_fcm_notification(token, title, body):
#     access_token = get_access_token()

#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json; charset=UTF-8",
#     }

#     message = {
#         "message": {
#             "token": token,
#             "notification": {
#                 "title": title,
#                 "body": body
#             }
#         }
#     }

#     project_id = "dinetime-62391"
#     url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

#     response = requests.post(url, headers=headers, json=message)

#     try:
#         resp_json = response.json()
#     except Exception:
#         resp_json = response.text

#     return {
#         "status_code": response.status_code,
#         "response": resp_json
#     }

# # -------------------------------
# # Example usage (Django shell)
# # -------------------------------
# if __name__ == "__main__":
#     from django.contrib.auth import get_user_model
#     User = get_user_model()
#     user = User.objects.first()  # replace with your test user
#     if user and user.notification_token:
#         print(send_fcm_notification(
#             token=user.notification_token,
#             title="Test Notification 🚀",
#             body="Hello from Django!"
#         ))
#     else:
#         print("User has no notification token!")


import os
import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# -------------------------------
# BASE DIRECTORY
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# -------------------------------
# Firebase Project Credentials
# -------------------------------
FIREBASE_PROJECTS = {
    "user": {
        "file": os.path.join(BASE_DIR, "Restaurant", "credentials", "dinetime-62391-firebase-adminsdk-fbsvc-db5549a1cb.json"),
        "project_id": "dinetime-62391",
    },
    "delivery": {
        "file": os.path.join(BASE_DIR, "Restaurant", "credentials", "dropgo-a03cb-firebase-adminsdk-fbsvc-75ab97774e.json"),
        "project_id": "dropgo-a03cb",
    },
}


# -------------------------------
# Helper: Get access token from Firebase
# -------------------------------
def get_access_token(project="user"):
    project_conf = FIREBASE_PROJECTS.get(project)
    if not project_conf:
        raise ValueError(f"Invalid project type: {project}")

    credentials = service_account.Credentials.from_service_account_file(
        project_conf["file"],
        scopes=["https://www.googleapis.com/auth/firebase.messaging"]
    )
    credentials.refresh(Request())
    return credentials.token, project_conf["project_id"]


# -------------------------------
# Main Notification Function
# -------------------------------
def send_fcm_notification(token, title, body, project="user"):
    try:
        access_token, project_id = get_access_token(project)

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
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

        url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
        response = requests.post(url, headers=headers, json=message)

        try:
            resp_json = response.json()
        except Exception:
            resp_json = response.text

        print(f"✅ FCM ({project}) → {token[:10]}... : {response.status_code}")
        return {"status_code": response.status_code, "response": resp_json}

    except Exception as e:
        print(f"❌ FCM Error ({project}):", e)
        return {"error": str(e)}
 