# app.py

from flask import Flask, Response, json, request, make_response
import os
import logging
from dotenv import load_dotenv, find_dotenv

from Mysql import MysqlDatabase
from S3 import create_bucket, add_user_key
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
PRIMARY_REGION = os.environ.get("PRIMARY_REGION")


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

@app.route('/cognitoUserToRDS', methods=["POST"])
def cognitoUserToRDS():
    data = {
        'email': request.form.get('email'),
        'email_verified': request.form.get('email_verified'),
        'user_pool_id': request.form.get('userPoolId'),
        'user_id': request.form.get('userName'),
    }
    valid, fields = Validate.validateRequestData(data, required_fields=['email', 'email_verified', 'user_pool_id', 'user_id'])
    if not valid:
        error_fields = ', '.join(fields)
        error_message = f"Data missing from these fields: {error_fields}"
        return Response.jsonResponse({"status": "error", "message": error_message}, 400)

    rsp = db.INSERT('cognitoUserToRDS', data)
    return Response.jsonResponse(rsp)

@app.route('/createCognitoUserBucket', methods=["POST"])
def createCognitoUserBucket():
    data = {
        'email': request.form.get('email'),
        'email_verified': request.form.get('email_verified'),
        'user_pool_id': request.form.get('userPoolId'),
        'user_id': request.form.get('userName'),
    }
    valid, fields = Validate.validateRequestData(data, required_fields=['email', 'email_verified', 'user_pool_id', 'user_id'])
    creation = add_user_key(bucket_name="mgr.users.data", user_id=data['user_id'], metadata=data)
    return str(creation)

# include this for local dev

if __name__ == '__main__':
    app.run()
