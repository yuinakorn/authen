import base64
import datetime
import json
import urllib
from datetime import datetime, timedelta

import jwt
import pymysql.cursors
import pytz
import requests
from dotenv import dotenv_values
# from fastapi import HTTPException, FastAPI
# from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response

from controller.check_permis_controller import check_permis, get_exp_url
import jsonpickle

import re

from user_agents import parse

config_env = dotenv_values(".env")


def check_login(req):  # login by username and password
    username = req.username
    password = req.password
    token = req.account_token
    hoscode = req.hoscode
    thaid_id = req.thaid_id

    # print("tha_id: ", thaid_id)

    user_not_allow = ["admin", "root", "sa", "sysadmin", "sys", "system", "administrator", "superuser", "super", "adm",
                      "user", "test", "guest", "demo"]

    if check_account_token(token)["result"] == 0:
        return Response(content=jsonpickle.encode({"detail": f"Unauthorized, token is invalid."}),
                        status_code=401,
                        media_type="application/json")
    else:
        # pass  # just test
        # check password is secure or not with regex pattern 8 digit, 1 uppercase, 1 lowercase, 1 special character
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]"

        length_password = 8
        length_username = 2

        if len(password) < length_password or len(username) < length_username:
            return Response(content=jsonpickle.encode({"status": "error", "http_status": "400", "error": "1",
                                                       "detail": f"Username ต้องยาวกว่า {length_username} ตัวอักษร, Password ต้องยาว {length_password} ตัวอักษรขึ้นไป"}),
                            status_code=200,
                            media_type="application/json")
        elif username in user_not_allow:
            return Response(content=jsonpickle.encode(
                {"status": "error", "http_status": "400", "error": "2",
                 "detail": f"Username {username} ไม่สามารถใช้งานได้ เนื่องจากความปลอดภัย"}),
                status_code=200,
                media_type="application/json")

        elif not re.search(pattern, password):
            return Response(content=jsonpickle.encode(
                {"status": "error", "http_status": "400", "error": "3",
                 "detail": f"โปรดตั้ง Password ให้ปลอดภัย"}),
                # {"status": "error", "http_status": "400", "error": "3",
                #  "detail": f"Password ต้องมีอย่างน้อย 1 ตัวอักษรพิมพ์เล็ก, 1 ตัวอักษรพิมพ์ใหญ่, 1 ตัวเลข, 1 ตัวอักษรพิเศษ"}),
                status_code=200,
                media_type="application/json")
        else:
            pass

    payload = {}
    headers = {}

    url_exp = get_exp_url(thaid_id)

    url = url_exp + "/query/user_authen/" + f"{hoscode}?user={username}&password={password}"
    print("url_exp: " + url)
    response = requests.request("GET", url, headers=headers, data=payload)

    with open('position.json', 'r') as file:
        # Load the JSON data from the file
        position_list = json.load(file)
    position_allow = position_list

    data = response.json()

    # if data[0]["entryposition"]:
    #     position = data[0]["entryposition"]
    # else:
    #     position = data[0]["position"]

    if not data:
        data = {
            "account_token": token,
            "hoscode": hoscode,
            "username": username,
            "cid": None,
            "position": None,
            "thaid_id": thaid_id,
            "ip": req.ip,
            "datetime": req.datetime,
            "status": "fail",
            "login_type": req.login_type
        }
        result_log = create_login_log(data)
        return Response(content=jsonpickle.encode({"status": "error", "http_status": "400", "error": "4",
                                                   "detail": f"Unauthorized, username or password is invalid."}),
                        status_code=200,
                        media_type="application/json")
    else:
        position = data[0].get("entryposition", data[0].get("position"))
        pass

    # matching_positions = [item for item in data if
    #                       item["entryposition"] and isinstance(item["entryposition"], str) and
    #                       any(pos in item["entryposition"] for pos in position_allow)]
    # result = 1 if len(matching_positions) > 0 else 0

    matching_positions = [item for item in data if
                          position and isinstance(position, str) and
                          any(pos in position for pos in position_allow)]
    result = 1 if len(matching_positions) > 0 else 0

    if result == 1:
        data = {
            "account_token": token,
            "hoscode": hoscode,
            "username": username,
            "cid": data[0]["cid"],
            "position": position,
            "thaid_id": thaid_id,
            "ip": req.ip,
            "datetime": req.datetime,
            "status": "success",
            "login_type": req.login_type
        }
        result_log = create_login_log(data)
        print("result_log: ", result_log)
        return {"status": "success", "result": result, "detail": response.json()}
    else:
        cidd = data[0]["cid"] if data[0]["cid"] else "0"
        data = {
            "account_token": token,
            "hoscode": hoscode,
            "username": username,
            "cid": cidd,
            "position": position,
            "thaid_id": thaid_id,
            "ip": req.ip,
            "datetime": req.datetime,
            "status": "fail",
            "login_type": req.login_type
        }
        result_log = create_login_log(data)
        print("result_log: ", result_log)
        # return 200 because for App can not read 401
        return Response(content=jsonpickle.encode({"status": "error", "http_status": "401", "error": "4",
                                                   "detail": f"Unauthorized, username or password or position is invalid."}),
                        status_code=200,
                        media_type="application/json")


def create_login_log(data_insert: dict):
    try:
        connection = pymysql.connect(host=config_env["DB_HOST"],
                                     user=config_env["DB_USER"],
                                     password=config_env["DB_PASSWORD"],
                                     db=config_env["DB_NAME"],
                                     charset=config_env["DB_CHARSET"],
                                     port=int(config_env["DB_PORT"]),
                                     cursorclass=pymysql.cursors.DictCursor
                                     )

        with connection.cursor() as cursor:
            sql = "INSERT INTO viewer_login_logs (account_token,hoscode,username,cid,position,thaid_id,ip,datetime,status,login_type) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (data_insert["account_token"], data_insert["hoscode"], data_insert["username"],
                                 data_insert["cid"], data_insert["position"], data_insert["thaid_id"],
                                 data_insert["ip"], data_insert["datetime"],
                                 data_insert["status"], data_insert["login_type"]))

            connection.commit()
        return True

    except Exception as e:
        print(e)
        return False


def get_public_ip():
    response = requests.get('https://httpbin.org/ip')
    ip_data = response.json()
    return ip_data.get('origin')


def get_client(request):
    client_ip = request.client.host
    # public_ip = get_public_ip()
    user_agent_string = request.headers.get('user-agent')
    user_agent = parse(user_agent_string)
    browser = user_agent.browser.family if user_agent.browser else "Unknown"
    operating_system = user_agent.os.family if user_agent.os else "Unknown"

    return {"client_ip": client_ip, "browser": browser, "os": operating_system, "user_agent": user_agent}


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
            sql = "SELECT * FROM service_api INNER JOIN thaid_client ON service_api.thaid_id = thaid_client.id WHERE account_token = %s"
            cursor.execute(sql, token)
            result = cursor.fetchone()
            if result is None:
                raise JSONResponse(content={"detail": f"Unauthorized"}, status_code=401)
            else:
                pass

        url = config_env["URL_AUTH"]
        client_id = result["client_id"]
        redirect_uri = result["callback_url"]
        scope = result["scope"]
        response_type = config_env["RESPONSE_TYPE"]

        get_url = f"{url}?response_type={response_type}&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&state={state}"

        return {"url": get_url}

    except Exception as e:
        print(e)
        return e


def get_callback(code, state):
    try:
        print("\nstart get_callback")
        connection = pymysql.connect(host=config_env["DB_HOST"],
                                     user=config_env["DB_USER"],
                                     password=config_env["DB_PASSWORD"],
                                     db=config_env["DB_NAME"],
                                     charset=config_env["DB_CHARSET"],
                                     port=int(config_env["DB_PORT"]),
                                     cursorclass=pymysql.cursors.DictCursor
                                     )

        if code.strip() and state.strip():
            service_id = state.split("|")[0]
            client_id = state.split("|")[1]
            prov_code = state.split("|")[2]
            hcode = state.split("|")[3]

            # Set the time zone to Thailand
            thailand_tz = pytz.timezone('Asia/Bangkok')
            utc_now = datetime.now(pytz.utc)
            created_date = utc_now.astimezone(thailand_tz)

            # grant_type = config_env["GRANT_TYPE"]

            with connection.cursor() as cursor:
                sql = "SELECT * FROM service_api " \
                      "INNER JOIN thaid_client ON service_api.thaid_id = thaid_client.id " \
                      "WHERE service_id = %s"
                cursor.execute(sql, service_id)
                result = cursor.fetchone()
                if result is None:
                    return Response(content=jsonpickle.encode({"detail": f"Unauthorized, Service id is invalid."}),
                                    status_code=401,
                                    media_type="application/json")
                else:
                    thaid_redirect_uri = result["callback_url"]
                    thaid_client_id = result["client_id"]
                    thaid_client_secret = result["client_secret"]
                    print("thaid_redirect_uri: ", thaid_redirect_uri)

                    # redirect_uri = config_env["REDIRECT_URI"]
                    # auth_basic = config_env["AUTH_BASIC"]

                    # make base64 with client_id and client_secret
                    client_id_secret = thaid_client_id + ":" + thaid_client_secret
                    print("client_id_secret: ", client_id_secret)

                    auth_basic_with_b = base64.b64encode(client_id_secret.encode("utf-8"))
                    auth_basic = str(auth_basic_with_b).split("'")[1].split("'")[0]

                    print("auth_basic: ", auth_basic)

                    encoded_url = urllib.parse.quote(thaid_redirect_uri, safe="")

                    payload = f"grant_type=authorization_code&code={code}&redirect_uri={encoded_url}"

                    headers = {
                        'Content-Type': config_env["CONTENT_TYPE"],
                        'Authorization': f'Basic {auth_basic}',
                    }

                    response = requests.request("POST", config_env["URL_TOKEN"], headers=headers, data=payload)

                    print("response.text: ", response.text)

                    # API step 3 Check Active CID
                    access_token = response.json()["access_token"]

                    payload2 = f"token=Bearer {access_token}"

                    res_active = requests.request("POST", config_env["URL_ACTIVE"], headers=headers, data=payload2)

                    print("res_active.text: ", res_active.text)

                    if res_active.json()["active"] is True:
                        # Check permission
                        level = check_permis(prov_code, hcode, response.json()["pid"])

                        scope_return = response.json()["pid"] + "," + response.json()["given_name"] + "," + \
                                       response.json()[
                                           "family_name"]
                        # active = res_active.json()["active"]
                        active = 1
                        print("active: ", active)

                        with connection.cursor() as cursor:
                            sql = "INSERT INTO service_requested (service_id, client_id, hcode, scope, state, level, active, created_date) " \
                                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                            cursor.execute(sql,
                                           (service_id, client_id, hcode, scope_return, state, level, active,
                                            created_date))
                            # how to print sql after execute

                            print("cursor.rowcount: ", cursor.rowcount)

                        # if inserted to return
                        if cursor.rowcount == 1:
                            # 1. insert to temporary table
                            connection.commit()
                            with connection.cursor() as cursor2:
                                sql = "INSERT INTO log_service_requested (service_id, client_id, hcode, scope, state, level, active, created_date) " \
                                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                                cursor2.execute(sql,
                                                (
                                                    service_id, client_id, hcode, scope_return, state, level, active,
                                                    created_date))
                                # 2. insert to log
                                connection.commit()

                            # return {"active": res_active.json()["active"], "detail": response.json()}
                            print("service_id: ", service_id)
                            print("type of service_id: ", type(service_id))
                            if service_id == "1":
                                print("กำลังดำเนินการ")
                                return "กำลังดำเนินการ"
                            elif service_id == "2":
                                print("กำลังตรวจสอบสิทธิ กรุณารอสักครู่...")
                                return "กำลังตรวจสอบสิทธิ กรุณารอสักครู่..."
                            else:
                                print("กำลังดำเนินการ โปรดรอสักครู่...")
                                return "กำลังดำเนินการ โปรดรอสักครู่..."

                        else:
                            return Response(content=jsonpickle.encode({"detail": f"Insert failed."}),
                                            status_code=400,
                                            media_type="application/json")

                    else:
                        return Response(content=jsonpickle.encode({"detail": f"Unauthorized, CID is not active."}),
                                        status_code=401,
                                        media_type="application/json")

        else:
            return Response(content=jsonpickle.encode({"detail": f"Invalid input. Code and state are required."}),
                            status_code=400,
                            media_type="application/json")

    except Exception as e:
        print(e)
        return e


# def run_sync(coro_func):
#     def wrapper(*args, **kwargs):
#         loop = asyncio.get_event_loop()
#         return loop.run_in_executor(ThreadPoolExecutor(), lambda: asyncio.ensure_future(coro_func(*args, **kwargs)))
#     return wrapper
#

def check_account_token(token):
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
            # print("result in chk token = ", result)
            if result is None:
                return {"result": 0}
            else:
                return {"result": 1}

    except Exception as e:
        print(e)
        return {"result": 0}


def get_active_by_state(request_token, state):
    token = request_token.account_token
    is_token = check_account_token(token)
    if is_token["result"] == 0:
        return Response(content=jsonpickle.encode({"detail": f"Unauthorized, Service id is invalid."}),
                        status_code=401,
                        media_type="application/json")
    else:
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
                sql = "SELECT * FROM service_requested WHERE state = %s " \
                      "ORDER BY created_date DESC LIMIT 1"
                cursor.execute(sql, state)
                result = cursor.fetchone()
                if result is None:
                    return Response(content=jsonpickle.encode({"detail": f"Unauthorized, state deleted"}),
                                    status_code=401,
                                    media_type="application/json")
                else:
                    print("result => ", result)
                    return result

        except Exception as e:
            print(e)
            return e

        finally:
            with connection.cursor() as cursor:
                sql = "DELETE FROM service_requested WHERE state = %s"
                cursor.execute(sql, state)
                connection.commit()


def get_active_by_client_id(request_token, client_id):
    token = request_token.account_token
    is_token = check_account_token(token)
    if is_token["result"] == 0:
        return Response(content=jsonpickle.encode({"detail": f"Unauthorized, Service id is invalid."}),
                        status_code=401,
                        media_type="application/json")
    else:
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
                sql = "SELECT * FROM service_requested WHERE client_id = %s"
                cursor.execute(sql, client_id)
                result = cursor.fetchone()
                if result is None:
                    return Response(content=jsonpickle.encode({"detail": f"Unauthorized, state deleted"}),
                                    status_code=401,
                                    media_type="application/json")
                else:
                    return result

        except Exception as e:
            print(e)
            return e

        finally:
            with connection.cursor() as cursor:
                sql = "DELETE FROM service_requested WHERE client_id = %s"
                cursor.execute(sql, client_id)
                connection.commit()


# return is_token
# pass
# print("token return", is_token["result"])
# if is_token["result"] == 0:
#     print("token is ", is_token)
#     raise JSONResponse(content={"detail": f"Unauthorized"}, status_code=401)
#
# else:
#     # print(is_token)
#     return {"detail": f"Authorized"}
# pass
# connection = pymysql.connect(host=config_env["DB_HOST"],
#                              user=config_env["DB_USER"],
#                              password=config_env["DB_PASSWORD"],
#                              db=config_env["DB_NAME"],
#                              charset=config_env["DB_CHARSET"],
#                              port=int(config_env["DB_PORT"]),
#                              cursorclass=pymysql.cursors.DictCursor
#                              )
# try:
#     with connection.cursor() as cursor:
#         sql = "SELECT * FROM service_requested WHERE state = %s"
#         cursor.execute(sql, state)
#         result = cursor.fetchone()
#         if result is None:
#             raise JSONResponse(content={"detail": f"Unauthorized, state deleted"}, status_code=401)
#         else:
#             return result
#
# except Exception as e:
#     print(e)
#     return e
#
# finally:
#     with connection.cursor() as cursor:
#         sql = "DELETE FROM service_requested WHERE state = %s"
#         cursor.execute(sql, state)
#         connection.commit()


def create_jwt_token(request_viewer, expires_delta: timedelta):
    payload = {
        "hosCode": request_viewer.hosCode,
        "cid": request_viewer.cid,
        "patientCid": request_viewer.patientCid,
        "patientHosCode": request_viewer.patientHosCode,
    }

    expire = datetime.utcnow() + expires_delta
    to_encode = {**payload, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, config_env["SECRET_KEY"], algorithm="HS256")
    return encoded_jwt


def get_token_viewer(request_viewer):
    token = request_viewer.account_token
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
                return Response(content=jsonpickle.encode({"detail": "Unauthorized, token is invalid."}),
                                status_code=401,
                                media_type="application/json")
            else:
                access_token_expires = timedelta(minutes=30)  # Token expiration time
                access_token = create_jwt_token(request_viewer, expires_delta=access_token_expires)
                return {"access_token": access_token}
                # return create_jwt_token(request_viewer)

    except Exception as e:
        print(e)
        return e


def post_log(request_log):
    token = request_log.account_token
    is_token = check_account_token(token)
    if is_token["result"] == 0:
        return Response(content=jsonpickle.encode({"detail": f"Unauthorized, Service id is invalid."}),
                        status_code=401,
                        media_type="application/json")
    else:
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
                sql = "INSERT INTO viewer_logs (account_token,hoscode,cid,patient_cid,patient_hoscode,ip,datetime) " \
                      "VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (request_log.account_token, request_log.hosCode, request_log.cid,
                                     request_log.patientCid, request_log.patientHosCode, request_log.ip,
                                     request_log.datetime))
                connection.commit()
                # return True
                return {"status": "success", "detail": {
                    "hoscode": request_log.hosCode,
                    "cid": request_log.cid,
                    "patient_cid": request_log.patientCid,
                    "patient_hoscode": request_log.patientHosCode,
                    "ip": request_log.ip,
                    "datetime": request_log.datetime
                }}

        except Exception as e:
            print(e)
            return e


def get_province(request_token):
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
            sql = "SELECT * FROM service_api  WHERE account_token = %s"
            cursor.execute(sql, request_token.account_token)
            result = cursor.fetchone()
            if result is None:
                return Response(content=jsonpickle.encode({"detail": "Unauthorized, token is invalid."}),
                                status_code=401,
                                media_type="application/json")
            else:
                with connection.cursor() as cursor:
                    sql = "SELECT province_list.*,service_api.account_token FROM province_list " \
                          " INNER JOIN service_api ON province_list.service_id = service_api.service_id"
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    if result is None:
                        return Response(content=jsonpickle.encode({"detail": "Not found."}),
                                        status_code=404,
                                        media_type="application/json")
                    else:
                        return result
    except Exception as e:
        print(e)
        return e


def get_hosname(hoscode):
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
            sql = (
                "SELECT hoscode, REPLACE(hosname,'โรงพยาบาลส่งเสริมสุขภาพตำบล','รพ.สต.') hosname FROM chospital WHERE hoscode = %s "
                " AND provcode in ('50','51','58') LIMIT 1")
            cursor.execute(sql, hoscode)
            result = cursor.fetchone()

            if result is None or result["hosname"] is None:
                return Response(content=jsonpickle.encode({"detail": f"Hcode {hoscode} Not found."}), status_code=404,
                                media_type="application/json")
                # raise HTTPException(status_code=404, detail="Not found.")
            else:
                return result

    except Exception as e:
        print(e)
        return e


def get_hosname_all():
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
            sql = "SELECT hoscode," \
                  "REPLACE(hosname,'โรงพยาบาลส่งเสริมสุขภาพตำบล','รพ.สต.') hosname, provcode FROM chospital " \
                  "WHERE hostype not in ('01','02','03','10','13','14','15','16') " \
                  "AND provcode in ('50','51','58','85','94')"
            cursor.execute(sql)
            result = cursor.fetchall()
            if result is None:
                return Response(content=jsonpickle.encode({"detail": f"Not found."}), status_code=404,
                                media_type="application/json")
            else:
                return result
    except Exception as e:
        print(e)
        return e


def get_script_provider(request_token):
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
            cursor.execute(sql, request_token.account_token)
            result = cursor.fetchone()
            if result is None:
                return Response(content=jsonpickle.encode({"detail": "Unauthorized, token is invalid."}),
                                status_code=401,
                                media_type="application/json")
            else:
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM c_script_provider WHERE active = 1"
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    if result is None:
                        raise JSONResponse(content={"detail": f"Not found."}, status_code=404)
                    else:
                        return result
    except Exception as e:
        print(e)
        return e


def get_province_code():
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
            sql = "SELECT * FROM cprovince"
            cursor.execute(sql)
            result = cursor.fetchall()
            if result is None:
                return Response(content=jsonpickle.encode({"detail": f"Not found."}), status_code=404,
                                media_type="application/json")
            else:
                return result
    except Exception as e:
        print(e)
        return e


def post_version(request_token):
    token = request_token.account_token
    is_token = check_account_token(token)
    if is_token["result"] == 0:
        return Response(content=jsonpickle.encode({"detail": f"Unauthorized, Service id is invalid."}),
                        status_code=401,
                        media_type="application/json")
    else:
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
                sql = "SELECT * FROM sys_config"
                cursor.execute(sql)
                result = cursor.fetchall()
                if result is None:
                    return Response(content=jsonpickle.encode({"detail": f"Unauthorized, Service id is invalid."}),
                                    status_code=401,
                                    media_type="application/json")
                else:
                    return result

        except Exception as e:
            print(e)
            return e
