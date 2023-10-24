import pymysql
import requests
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
            sql = f"SELECT url_exp FROM `province_list` WHERE `prov_code` = '{prov_code}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is None:
                return 0
            else:
                url_exp = result["url_exp"]
                print(url_exp)
                pass

    except Exception as e:
        print(e)
        return 0
    finally:
        connection.close()

    url_his_cid = config_env["URL_HIS_CID"]
    url = f"{url_exp}{url_his_cid}{hcode}?cid={cid}"

    response = requests.request("GET", url, headers={}, data={})

    print(response.text)
    data = response.json()
    position_allow = ["พยาบาล", "นายแพทย์", "นักวิชาการ"]

    matching_positions = [item for item in data if
                          item["position"] and isinstance(item["position"], str) and item["position"].startswith(
                              tuple(position_allow))]
    result = 1 if len(matching_positions) > 0 else 0

    return result