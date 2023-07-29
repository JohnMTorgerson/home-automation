import os
import dotenv
dotenv.load_dotenv()
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")

# # use the following when testing wyze_sdk from local fork
# import sys
# # insert at 1: 0 is the script path (or '' in REPL)
# sys.path.insert(1, os.path.abspath('../../!...Forks/'))

from wyze_sdk import Client
from wyze_sdk.errors import WyzeApiError


def get_client():
    try:
        print("Trying access token...")
        client = Client(token=os.environ['WYZE_ACCESS_TOKEN'])
        client.devices_list() # check if we have client access
    except Exception as e:
        try:
            print(repr(e))
            print(f"Didn't work, trying refresh token...")
            client = Client(token=os.environ['WYZE_REFRESH_TOKEN'])
            client.devices_list() # check if we have client access
        except Exception as e:
            print(repr(e))
            print(f"Didn't work, trying regular login and saving new access/refresh tokens...")
            response = Client().login(email=os.environ['WYZE_EMAIL'], password=os.environ['WYZE_PASSWORD'], key_id=os.environ['WYZE_KEY_ID'], api_key=os.environ['WYZE_API_KEY'])
            print(f"access token: {response['access_token']}")
            print(f"refresh token: {response['refresh_token']}")
            dotenv.set_key(dotenv_path,'WYZE_ACCESS_TOKEN',response['access_token'])
            dotenv.set_key(dotenv_path,'WYZE_REFRESH_TOKEN',response['refresh_token'])

            client = Client(token=response['access_token'])
            client.devices_list() # check if we have client access

    print("successfully logged in to client...")

    return client



# def get_access_token():
#     # POST /app/user/refresh_token HTTP/1.1

#     # Host: api.wyzecam.com

#     # Content-Type: application/json

#     # Content-Length: 100

#     request_body = {
#         "app_ver": os.environ['WYZE_API_KEY'],
#         "app_version": os.environ['WYZE_API_KEY'],
#         "phone_id": os.environ['WYZE_API_KEY'],
#         "refresh_token": os.environ['WYZE_REFRESH_TOKEN'],
#         "sc": os.environ['WYZE_API_KEY'],
#         "sv": os.environ['WYZE_API_KEY'],
#         "ts": 4070908800000
#     }

if __name__ == "__main__" :
    get_client()