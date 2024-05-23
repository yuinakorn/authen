import pymysql.cursors
from dotenv import dotenv_values

config_env = dotenv_values(".env")

connection = pymysql.connect(host=config_env["DB_HOST"],
                             user=config_env["DB_USER"],
                             password=config_env["DB_PASSWORD"],
                             db=config_env["DB_NAME"],
                             charset=config_env["DB_CHARSET"],
                             port=int(config_env["DB_PORT"]),
                             cursorclass=pymysql.cursors.DictCursor
                             )