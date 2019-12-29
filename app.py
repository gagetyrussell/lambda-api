# app.py

from flask import Flask, Response, json, request, make_response
import os
import logging
from dotenv import load_dotenv, find_dotenv

from Mysql import MysqlDatabase
from flask import json as flask_json
from Util import Response, Validate

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

app = Flask(__name__)

@app.route('/getUsers', methods=["GET", "POST"])
def getUsers():
    rsp = db.SELECT('getUsers')
    return Response.jsonResponse(rsp)

@app.route('/createUser', methods=["GET", "POST"])
def createUser():
    data = {
        'first_name': request.form.get('first_name'),
        'last_name': request.form.get('last_name'),
        'email': request.form.get('email')
    }
    valid, fields = Validate.validateRequestData(data, required_fields=['first_name', 'last_name', 'email'])
    if not valid:
        error_fields = ', '.join(fields)
        error_message = f"Data missing from these fields: {error_fields}"
        return Response.jsonResponse({"status": "error", "message": error_message}, 400)

    rsp = db.INSERT('createUser', data)
    return Response.jsonResponse(rsp)

# include this for local dev

if __name__ == '__main__':
    app.run()
