# app.py

from flask import Flask, Response, json, request
import os
import logging
from dotenv import load_dotenv, find_dotenv

# first, load your env file, replacing the path here with your own if it differs
# when using the local database make sure you change your path  to .dev.env, it should work smoothly.
load_dotenv()
# set globals
RDS_HOST = os.environ.get("DB_HOST")
RDS_PORT = int(os.environ.get("DB_PORT", 3306))
NAME = os.environ.get("DB_USERNAME")
PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")

# we need to instantiate the logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def connect():
    try:
        cursor = pymysql.cursors.DictCursor
        conn = pymysql.connect(RDS_HOST, user=NAME, passwd=PASSWORD, db=DB_NAME, port=RDS_PORT, cursorclass=cursor, connect_timeout=5)
        logger.info("SUCCESS: connection to RDS successful")
        return(conn)
    except Exception as e:
        logger.exception("Database Connection Error")

def build_response(resp_dict, status_code):
    response = Response(json.dumps(resp_dict), status_code)
    return response

def insert(data):
    uniq_id = (uuid5(uuid1(), (uuid1())))
    query = """insert into metadb.users (ID, first_name, last_name, email)
            values(%s, %s, %s, %s)
            """
    return (query, (uniq_id, data["first_name"], data["last_name"], data["email"]))

def validate(data):
    error_fields = []
    not_null = [
        "first_name",
        "last_name",
        "email"
    ]

    for x in not_null:
        if x not in data or len(data[x]) == 0:
            error_fields.append(x)
    return (len(error_fields) == 0, error_fields)

app = Flask(__name__)

# here is how we are handling routing with flask:
@app.route('/')
def index():
    connect()
    return "Hello World! Connected", 200

@app.route('/user', methods=["GET", "POST"])
def user():
    conn = connect()
    if request.method == "GET":
        items = []
        try:
            with conn.cursor() as cur:
                cur.execute("select * from User")
                for row in cur:
                    items.append(row)
                conn.commit()
        except Exception as e:
            logger.info(e)
            response = build_response({"status": "error", "message": "error getting users"}, 500)
            return response
        finally:
            conn.close()
        response = build_response({"rows": items, "status": "success"}, 200)
        return response
    if request.method == "POST":
        data = {
            "first_name": request.form.get("first_name", ""),
            "last_name": request.form.get("last_name", ""),
            "email": request.form.get("email", "")
        }
        valid, fields = validate(data)
        if not valid:
            error_fields = ', '.join(fields)
            error_message = "Data missing from these fields: %s" %error_fields
            return build_response({"status": "error", "message": error_message}, 400)
        query, vals = insert(data)
        try:
            with conn.cursor() as cur:
                cur.execute(query, vals)
                conn.commit()
        except Exception as e:
            logger.exception("insert error")
            return build_response({"status": "error", "message": "insert error"}, 500)
        finally:
            conn.close()
            cur.close()
        return build_response({"status": "success"}, 200)

# include this for local dev

if __name__ == '__main__':
    app.run()
