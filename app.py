# app.py

from flask import Flask, Response, json

app = Flask(__name__)

# here is how we are handling routing with flask:
@app.route('/')
def index():
    return "Hello World!", 200

@app.route('/user', methods=["GET"])
def user():
    resp_dict = {"first_name": "John", "last_name": "doe"}
    response = Response(json.dumps(resp_dict), 200)
    return response

# include this for local dev

if __name__ == '__main__':
    app.run()
