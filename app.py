# app.py

from flask import Flask, Response, json, request, make_response
import os
import logging
from dotenv import load_dotenv, find_dotenv
import pymysql
from Mysql import MysqlDatabase
from flask import json as flask_json

db = MysqlDatabase()

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

def jsonResponse(obj, status=200, headers=None):
    responseHeaders = headers or {}
    responseHeaders.update({
        "Content-type": "application/json"
    })
    data = flask_json.dumps(obj)

    rsp = make_response(data, status)
    for x in responseHeaders:
        rsp.headers[x] = responseHeaders[x]

    logger.debug("Response: %s" % repr(rsp))
    return rsp

def connect():
    try:
        cursor = pymysql.cursors.DictCursor
        conn = pymysql.connect(RDS_HOST, user=NAME, passwd=PASSWORD, port=RDS_PORT, cursorclass=cursor, connect_timeout=5)
        logger.info("SUCCESS: connection to RDS successful")
        return(conn)
    except Exception as e:
        logger.exception("Database Connection Error")

def build_response(resp_dict, status_code):
    response = Response(json.dumps(resp_dict), status_code)
    return response

def insert(data):
    query = """insert into metadb.users (first_name, last_name, email)
            values(%s, %s, %s)
            """
    return (query, (data["first_name"], data["last_name"], data["email"]))

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

@app.route('/getUsers', methods=["GET", "POST"])
def getUsers():
    rsp = db.SELECT('getUsers')
    return jsonResponse(rsp)

@app.route('/createUser', methods=["GET", "POST"])
def createUser():

    first_name = request.form.get('first_name')
    print(first_name)
    last_name = request.form.get('last_name')
    print(last_name)
    email = request.form.get('email')
    print(email)

    rsp = db.INSERT('createUser', {'first_name': first_name, 'last_name': last_name, 'email': email})
    return jsonResponse(rsp)

@app.route('/user', methods=["GET", "POST"])
def user():
    conn = connect()
    if request.method == "GET":
        items = []
        try:
            with conn.cursor() as cur:
                cur.execute("select * from metadb.users")
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
            "first_name": request.form.get('first_name'),
            "last_name": request.form.get('last_name'),
            "email": request.form.get('email')
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
