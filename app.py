# DataBase Course Design for CSZ2018001 of Yangtze University
# Design and Coding by Tompes
# Github: https://Github.com/Tompes/LibraryManagementSys

import os
from flask import Flask
import flask_restful as restful
from resources.login import Login
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(64) #获取加密密钥

api = restful.Api(app)

api.add_resource(Login,'/login')

if __name__ == '__main__' :
	app.run(debug=True)