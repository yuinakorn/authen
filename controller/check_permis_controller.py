import pymysql
import requests
import json
from dotenv import dotenv_values

config_env = dotenv_values(".env")


def check_permis(prov_code, hcode, cid):
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
            sql = f"SELECT url_exp FROM province_list WHERE prov_code = '{prov_code}'"
            print("sql in check_permis: ", sql)
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is None:
                return 0
            else:
                # url exp ของจังหวัดนั้น ๆ
                url_exp = result["url_exp"]
                url_his_cid = config_env["URL_HIS_CID"]
                # url เต็ม โดยส่ง cid ไปเช็ค
                url = f"{url_exp}{url_his_cid}{hcode}?cid={cid}"

                response = requests.request("GET", url, headers={}, data={})

                print("res position from exp: ", response.text)
                data = response.json()
                # get data from json file
                with open('position.json', 'r') as file:
                    # Load the JSON data from the file
                    position_list = json.load(file)
                position_allow = position_list

                # matching_positions = [item for item in data if
                #                       item["position"] and isinstance(item["position"], str) and item[
                #                           "position"].startswith(
                #                           tuple(position_allow))]

                # result = 1 if len(matching_positions) > 0 else 0

                matching_positions = [item for item in data if
                                      item["position"] and isinstance(item["position"], str) and
                                      any(pos in item["position"] for pos in position_allow)]

                # ถ้ามีการ match กับ position ที่อนุญาตให้เข้าถึง จะ return 1 ถ้าไม่มีจะ return 0
                level = 1 if len(matching_positions) > 0 else 0
                his_position = matching_positions[0]["position"] if len(matching_positions) > 0 else None
                return level, his_position

    except Exception as e:
        print(e)
        return 0


def get_exp_url(id: int):
    print("id in get_exp_url: ", id)
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
            sql = f"SELECT * FROM thaid_client WHERE id = {id}"
            print("sql in get_exp_url: ", sql)
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is None:
                return 0
            else:
                url_exp = result["url_exp"]
                return url_exp

    except Exception as e:
        print(e)
        return 0

