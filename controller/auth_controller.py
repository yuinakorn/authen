import urllib
import requests
from dotenv import dotenv_values
from fastapi import HTTPException
from starlette.responses import JSONResponse

from models.database import connection

import datetime
import pytz

config_env = dotenv_values(".env")


def get_generate_qrcode(request_token, state: str):
    token = request_token.account_token
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM service_api WHERE account_token = %s"
            cursor.execute(sql, token)
            result = cursor.fetchone()
            if result is None:
                raise JSONResponse(content={"detail": f"Unauthorized"}, status_code=401)
            else:
                pass

        url = config_env["URL_AUTH"]
        client_id = config_env["CLIENT_ID"]
        redirect_uri = config_env["REDIRECT_URI"]
        scope = config_env["SCOPE"]
        response_type = config_env["RESPONSE_TYPE"]

        get_url = f"{url}?response_type={response_type}&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&state={state}"

        return {"url": get_url}

    except Exception as e:
        print(e)
        return e


def get_callback(code, state):
    try:
        if code.strip() and state.strip():
            service_id = state.split("-")[0]
            client_id = state.split("-")[1]

            # Set the time zone to Thailand
            thailand_tz = pytz.timezone('Asia/Bangkok')
            utc_now = datetime.datetime.now(pytz.utc)
            created_date = utc_now.astimezone(thailand_tz)

            grant_type = config_env["GRANT_TYPE"]
            redirect_uri = config_env["REDIRECT_URI"]
            auth_basic = config_env["AUTH_BASIC"]

            encoded_url = urllib.parse.quote(redirect_uri, safe="")

            payload = f"grant_type={grant_type}&code={code}&redirect_uri={encoded_url}"

            headers = {
                'Content-Type': config_env["CONTENT_TYPE"],
                'Authorization': f'Basic {auth_basic}',
            }

            response = requests.request("POST", config_env["URL_TOKEN"], headers=headers, data=payload)

            print(response.text)

            # API step 3 Check Active CID
            access_token = response.json()["access_token"]

            payload2 = f"token=Bearer {access_token}"

            response2 = requests.request("POST", config_env["URL_ACTIVE"], headers=headers, data=payload2)

            print(response2.text)

            if response2.json()["active"] is True:
                # insert state into database
                with connection.cursor() as cursor:
                    sql = "INSERT INTO service_request (service_id,client_id,account_token, state,created_date) " \
                          "VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(sql, (service_id, client_id, access_token, state, created_date))
                #     if inserted to return
                if cursor.rowcount == 1:
                    connection.commit()
                    return {"active": response2.json()["active"], "detail": response.json()}
                else:
                    raise HTTPException(status_code=400, detail="Insert failed.")

            else:
                raise HTTPException(status_code=400, detail="It is not active.")

        else:
            raise HTTPException(status_code=400, detail="Invalid input. Code and state are required.")
    except Exception as e:
        print(e)
        return e
