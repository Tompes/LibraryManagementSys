from flask import Flask ,jsonify,session
from flask_restful import Resource,reqparse
from common.models import TbReaderType
from common.models import TbBook
from common.models import TbReader
from common.models import TbBorrow
import copy
from common.errorTable import ERROR_NUM
import sqlalchemy as SQL
from hashlib import md5
from config.dbconfig import db
# parser = restful.reqparse
# Resources = restful.Resource
class Login(Resource):
	def post(self):
		parser = reqparse.RequestParser(trim=True)
		parser.add_argument('username', type=int, required=True,help="`username` Type Error!")
		parser.add_argument('passwd', type=str, required=True,help="`passwd` Type Error!")


		args = parser.parse_args(strict=True)
		if 'username' and 'passwd' in args :
			m = md5()
			rdpwd = m.update(args['passwd'].strip().encode("utf8"))
			rdpwd = m.hexdigest()
			user = TbReader.query.filter_by(rdID=args['username'],rdPwd=rdpwd).first()
			if user is None:
				return ERROR_NUM['LoginFail'],404
			if user.rdStatus != '有效':
				return ERROR_NUM['userStatusError']
			varb = {
				'rdID': user.rdID,
				'rdName': user.rdName,
				'rdSex': user.rdSex,
				'rdType': user.rdType,
				'rdDept': user.rdDept,
				'rdPhone': user.rdPhone,
				'rdEmail': user.rdEmail,
				'rdPhoto': user.rdPhoto,
				'rdStatus': user.rdStatus,
				'rdAdminRoles': user.rdAdminRoles,
				'rdBorrowQty': user.rdBorrowQty,
				'rdDateReg': str(user.rdDateReg),
			}
			session['userinfo'] = copy.deepcopy(varb)
			session['userinfo'].pop('rdPhoto')
			db.session.close()
			return {'error':0 , 'msg' : '登录成功','userInfo':varb}
		else:
			db.session.close()
			return ERROR_NUM['unknow'],404

	def get(self):
		if 'userinfo' in session :
			try:
				user = TbReader.query.filter_by(rdID=session['userinfo']['rdID']).first()
				if user is None:
					return ERROR_NUM['LoginFail']
				if user.rdStatus != '有效':
					return ERROR_NUM['userStatusError']
				verb = {
					'rdID': user.rdID,
					'rdName': user.rdName,
					'rdSex': user.rdSex,
					'rdType': user.rdType,
					'rdDept': user.rdDept,
					'rdPhone': user.rdPhone,
					'rdEmail': user.rdEmail,
					'rdPhoto': user.rdPhoto,
					'rdStatus': user.rdStatus,
					'rdAdminRoles': user.rdAdminRoles,
					'rdBorrowQty': user.rdBorrowQty,
					'rdDateReg': str(user.rdDateReg),
				}
				session['userinfo'] =  copy.deepcopy(verb)
				session['userinfo'].pop('rdPhoto')
				db.session.close()
				return {'error': 0, 'msg': '状态正常', 'userInfo': verb}
			except :
				db.session.close()
				return ERROR_NUM['LoginFail']

		else:
			return ERROR_NUM['hasNotLogin']

	def delete(self):
		if 'userinfo' in session:
			session.pop('userinfo')
			return {'error':0,'msg':'退出登录成功！'}
		else:
			return ERROR_NUM['hasNotLogin']