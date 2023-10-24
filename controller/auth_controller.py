import urllib
import requests
from dotenv import dotenv_values
from fastapi import HTTPException
from starlette.responses import JSONResponse
from controller.check_permis_controller import check_permis
# from models.database import connection
import pymysql.cursors
import datetime
import pytz

config_env = dotenv_values(".env")


def get_generate_qrcode(request_token, state: str):
    token = request_token.account_token
    connection = pymysql.connect(host=config_env["DB_HOST"],
                                 user=config_env["DB_USER"],
                                 password=config_env["DB_PASSWORD"],
                                 db=config_env["DB_NAME"],
                                 charset=config_env["DB_CHARSET"],
                                 port=int(config_env["DB_PORT"]),
                                 cursorclass=pymysql.cursors.DictCursor
                                 )
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
    connection = pymysql.connect(host=config_env["DB_HOST"],
                                 user=config_env["DB_USER"],
                                 password=config_env["DB_PASSWORD"],
                                 db=config_env["DB_NAME"],
                                 charset=config_env["DB_CHARSET"],
                                 port=int(config_env["DB_PORT"]),
                                 cursorclass=pymysql.cursors.DictCursor
                                 )
    try:
        if code.strip() and state.strip():
            service_id = state.split("|")[0]
            client_id = state.split("|")[1]
            hcode = state.split("|")[2]

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

            res_active = requests.request("POST", config_env["URL_ACTIVE"], headers=headers, data=payload2)

            print(res_active.text)

            if res_active.json()["active"] is True:
                # Check permission
                level = check_permis(hcode, response.json()["pid"])

                scope_return = response.json()["pid"] + "," + response.json()["given_name"] + "," + response.json()[
                    "family_name"]
                active = res_active.json()["active"]

                with connection.cursor() as cursor:
                    sql = "INSERT INTO service_requested (service_id, client_id, scope, state, level, active, created_date) " \
                          "VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (service_id, client_id, scope_return, state, level, active, created_date))
                #     if inserted to return
                if cursor.rowcount == 1:
                    connection.commit()
                    # return {"active": res_active.json()["active"], "detail": response.json()}
                    return {"active": res_active.json()["active"]}
                else:
                    raise HTTPException(status_code=400, detail="Insert failed.")

            else:
                raise HTTPException(status_code=400, detail="It is not active.")

        else:
            raise HTTPException(status_code=400, detail="Invalid input. Code and state are required.")
    except Exception as e:
        print(e)
        return e
