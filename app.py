# DataBase Course Design for CSZ11801 of Yangtze University
# Design and Coding by Tompes
# Github: https://Github.com/Tompes/LibraryManagementSys

import os
from flask import Flask,render_template,session
import flask_restful as restful
from flask_cors import *
from flask import make_response
from resources.loginSys import Login
from resources.userSys import UserList,User,reRegister,UserTypeList
from resources.booksSys import BookList,Book
from resources.borrowSys import BorrowList,Borrow
from hashlib import md5
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(64) #获取加密密钥
CORS(app, supports_credentials=True) #支持跨域请求
api = restful.Api(app)

class index(restful.Resource):
	def get(self):
		headers = {
			'Content-type':'text/html'
		}
		resp = make_response(render_template('index.html'), 200)
		resp.headers.extend(headers or {})
		return resp

class test(restful.Resource):
	def get(self):
		m = md5()
		strs = 'Hello'
		m.update(strs.encode("utf8"))

		return {'hello':m.hexdigest()}

api.add_resource(index,'/')
api.add_resource(Login,'/login')
api.add_resource(UserList,'/userlist/<string:search>','/userlist')
api.add_resource(User,'/user/<int:rdID>','/user')
api.add_resource(UserTypeList,'/usertype')
api.add_resource(reRegister,'/reissue/<int:rdID>','/reissue')
api.add_resource(BookList,'/booklist/<string:search>','/booklist')
api.add_resource(Book,'/book/<int:bkID>','/book')
api.add_resource(BorrowList,'/borrowlist/<int:lsHasReturn>','/borrowlist')
api.add_resource(Borrow,'/borrow/<int:borrowID>','/borrow')
api.add_resource(test,'/test')


if __name__ == '__main__' :
	app.run(debug=True)