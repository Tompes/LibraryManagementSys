from flask_restful import Resource, reqparse
from common.models import TbReaderType
from common.models import TbBook
from common.models import TbReader
from common.models import TbBorrow
from hashlib import md5
from common.errorTable import ERROR_NUM
from common.common import defaultPhoto, userStatusTable, emailReg
import sqlalchemy as SQL
import time
import re
from config.dbconfig import db


class UserList(Resource,search=None):
	def get(self):
		try:
			data = TbReader.query.all()
			if data is None:
				return ERROR_NUM['queryFail']
			userList = []
			for item in data:
				user = {}
				user['rdID'] = item.rdID
				user['rdName'] = item.rdName
				user['rdSex'] = item.rdSex
				user['rdType'] = item.rdType
				user['rdDept'] = item.rdDept
				user['rdPhone'] = item.rdPhone
				user['rdEmail'] = item.rdEmail
				user['rdDateReg'] = str(item.rdDateReg)
				user['rdPhoto'] = item.rdPhoto
				user['rdStatus'] = item.rdStatus
				user['rdBorrowQty'] = item.rdBorrowQty
				# user['rdPwd'] = item.rdPwd
				user['rdAdminRoles'] = item.rdAdminRoles
				userList.append(user)
			return {'error': 0, 'userList': userList}, 200
		except SQL.exc.OperationalError as e:
			return ERROR_NUM['SQLOperate'], 500




class User(Resource):
	def get(self, rdID=None):
		if rdID is None:
			return ERROR_NUM['paramsErr']
		try:
			user = TbReader.query.filter_by(rdID=rdID).first()
			if user is None:
				return ERROR_NUM['userNotExist']
			doNotReturnedQuery = TbBorrow.query.filter_by(rdID=rdID,lsHasReturn=0).all()
			doNotReturnedBooks = []
			for item in doNotReturnedQuery:
				book = TbBook.query.filter_by(bkID=item.bkID).first()
				verb = {
					'borrowID':item.BorrowID,
					'bkID':item.bkID,
					'bkName':book.bkName,
					'ldContinueTimes':item.ldContinueTimes,
					'ldDateOut':item.ldDateOut,
					'ldDateRetPlan':item.ldDateRetPlan,
					'ldOverDay':item.ldOverDay,
				}
				doNotReturnedBooks.append(verb)

			userInfo = {
				'error': 0,
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
				'doNotReturnedBooks':doNotReturnedBooks
			}
			return  {'error':0,'userInfo':userInfo}

		except SQL.exc.OperationalError as e:
			return ERROR_NUM['SQLOperate'], 500

	def post(self, rdID=None):
		if rdID != None:
			return ERROR_NUM['paramsErr']
		parser = reqparse.RequestParser(trim=True)
		parser.add_argument('rdName', type=str, required=True, help="params `rdName` refuse!")
		parser.add_argument('rdSex', type=str, required=True, help="params `rdSex` refuse!")
		parser.add_argument('rdType', type=int, required=True, help="params `rdType` refuse!")
		parser.add_argument('rdDept', type=str, required=True, help="params `rdDept` refuse!")
		parser.add_argument('rdPhone', type=str, required=True, help="params `rdPhone` refuse!")
		parser.add_argument('rdEmail', type=str, required=True, help="params `rdEmail` refuse!")
		parser.add_argument('rdPhoto', type=str, required=False, help="params `rdPhoto` refuse!")
		parser.add_argument('rdStatus', type=int, required=True, help="params `rdStatus` refuse!")
		parser.add_argument('rdPwd', type=str, required=True, help="params `rdPwd` refuse!")
		parser.add_argument('rdAdminRoles', type=str, required=True, help="params `rdAdminRoles` refuse!")

		args = parser.parse_args(strict=True)
		headPic = ''  # 头像
		if args['rdSex'] == '男':
			headPic = defaultPhoto['man']
		else:
			headPic = defaultPhoto['woman']

		if args['rdStatus'] > len(userStatusTable) :
			return ERROR_NUM['paramsErr']
		if re.match(emailReg, args['rdEmail']) is False:
			return ERROR_NUM['emailRefuse']
		status = userStatusTable[args['rdStatus']]

		m = md5()
		rdpwd = m.update(args['rdPwd'].strip().encode("utf8"))
		rdpwd = m.hexdigest()
		segment = TbReader(
			rdName=args['rdName'].strip(),
			rdSex=args['rdSex'].strip(),
			rdType=args['rdType'],
			rdDept=args['rdDept'].strip(),
			rdPhone=args['rdPhone'].strip(),
			rdEmail=args['rdEmail'].strip(),
			rdDateReg=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
			rdPhoto=headPic.strip(),
			rdStatus=status,
			rdBorrowQty=0,
			rdPwd=rdpwd,
			rdAdminRoles=args['rdAdminRoles'],
		)
		try:
			db.session.add(segment)
			db.session.flush()
			db.session.commit()
			return {'error': 0, 'msg': 'Yes','rdId':segment.rdID}
		except :
			db.session.rollback()  # 回滚
			return ERROR_NUM['failToCreateUser'],400

	def put(self, rdID=None):
		if rdID is None:
			return ERROR_NUM['paramsErr']

		parser = reqparse.RequestParser(trim=True)
		parser.add_argument('rdName', type=str, required=False, help="params `rdName` refuse!")
		parser.add_argument('rdSex', type=str, required=False, help="params `rdSex` refuse!")
		parser.add_argument('rdType', type=int, required=False, help="params `rdType` refuse!")
		parser.add_argument('rdDept', type=str, required=False, help="params `rdDept` refuse!")
		parser.add_argument('rdPhone', type=str, required=False, help="params `rdPhone` refuse!")
		parser.add_argument('rdEmail', type=str, required=False, help="params `rdEmail` refuse!")
		parser.add_argument('rdPhoto', type=str, required=False, help="params `rdPhoto` refuse!")
		parser.add_argument('rdStatus', type=int, required=False, help="params `rdStatus` refuse!")
		parser.add_argument('rdPwd', type=str, required=False, help="params `rdPwd` refuse!")
		parser.add_argument('rdAdminRoles', type=str, required=False, help="params `rdAdminRoles` refuse!")

		args = parser.parse_args(strict=True)
		if rdID in args or len(args) < 1:
			return ERROR_NUM['paramsErr'], 400

		putData = {}
		for item in args:
			if args[item] is not None:
				if item == 'rdEmail' and re.match(emailReg, args['rdEmail']) == False:
					return ERROR_NUM['paramsErr'], 400

				if item == 'rdStatus':
					if args['rdStatus'] > len(userStatusTable):
						return ERROR_NUM['paramsErr'], 400
					args[item] = userStatusTable[args[item]]

				putData[item] = args[item].strip()

		try:
			user = TbReader.query.filter_by(rdID=rdID).first()
			if user is None:
				return ERROR_NUM['userNotExist']
			execute = TbReader.query.filter_by(rdID=rdID).update(putData)
			if execute is 0:
				return ERROR_NUM['failToUpdateUser'], 400
			db.session.commit()
			return {'error': 0, 'msg': '更新用户信息成功！','rdID':rdID,'updateData':putData}
		except SQL.exc.OperationalError as e:
			db.session.rollback()
			return ERROR_NUM['SQLOperate'], 500

	def delete(self, rdID=None):
		if rdID is None:
			return ERROR_NUM['paramsErr']
		try:
			execute = TbReader.query.filter_by(rdID=rdID).delete()
			if execute is 0:
				db.session.rollback()
				return ERROR_NUM['failToDeleteUser']
			db.session.commit()
			return {'error':'0','msg':'删除用户成功！','rdID':rdID}
		except :
			db.session.rollback()
			return ERROR_NUM['SQLOperate'],500

