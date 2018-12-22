from flask import session
from flask_restful import Resource, reqparse
from common.models import TbReaderType
from common.models import TbBook
from common.models import TbReader
from common.models import TbBorrow
from hashlib import md5
from common.errorTable import ERROR_NUM
from common.common import defaultPhoto, userStatusTable, emailReg, addslashes
import sqlalchemy as SQL
import time
import datetime
import re
from config.dbconfig import db


class UserList(Resource):
	def get(self, search=None):
		if 'userinfo' not in session:
			return ERROR_NUM['hasNotLogin']
		if session['userinfo']['rdAdminRoles'] != 8:
			return ERROR_NUM['noPermission']
		parser = reqparse.RequestParser(trim=True)
		parser.add_argument('rdName', type=str, required=False, help="params `rdName` refuse!")
		parser.add_argument('rdDept', type=str, required=False, help="params `rdDept` refuse!")
		parser.add_argument('rdType', type=str, required=False, help="params `rdType` refuse!")
		parser.add_argument('rdID', type=str, required=False, help="params `rdID` refuse!")
		args = parser.parse_args(strict=True)

		filterArgs = {}
		for item in args:
			if args[item] is not None and args[item] is not '':
				filterArgs[item] = args[item]
		t = ''
		i = 0
		if len(filterArgs) == 0:  # 搜索模式未给参数
			return ERROR_NUM['paramsErr']
		for k in filterArgs.keys():
			if i == 0:
				t += k + " like '%" + addslashes(filterArgs[k]) + "%' "
			else:
				t += " and " + k + " like '%" + addslashes(filterArgs[k]) + "%' "
			i += 1
		try:
			data = []
			if search is None:
				data = TbReader.query.all()
			if search == 'search':
				print('select * from Tb_Reader where {0}'.format(t))
				data = db.session.execute('select * from Tb_Reader where {0}'.format(t))
			# data = db.session.execute('select * from Tb_Reader')
			if data is None:
				return ERROR_NUM['queryFail']
			userList = []
			for item in data.fetchmany(10):
				user = {
					'rdID': item.rdID,
					'rdName': item.rdName,
					'rdSex': item.rdSex,
					'rdType': item.rdType,
					'rdDept': item.rdDept,
					'rdPhone': item.rdPhone,
					'rdEmail': item.rdEmail,
					'rdDateReg': str(item.rdDateReg),
					'rdPhoto': item.rdPhoto,
					'rdStatus': item.rdStatus,
					'rdBorrowQty': item.rdBorrowQty,
					'rdAdminRoles': item.rdAdminRoles
				}
				# user['rdPwd'] = item.rdPwd
				userList.append(user)
				db.session.commit()
			return {'error': 0, 'userList': userList}, 200
		except:
			db.session.rollback()
			return ERROR_NUM['failToGetUserList']


class UserTypeList(Resource):
	def get(self):
		try:
			typeList = []
			readerType = TbReaderType.query.all()
			for item in readerType:
				verb = {
					'rdType': item.rdType,
					'typeValue':item.rdType,
					'rdTypeName': item.rdTypeName,
					'typeKey':item.rdTypeName,
					'CanLendQty': item.CanLendQty,
					'CanLendDay': item.CanLendDay,
					'CanContinueTimes': item.CanContinueTimes,
					'PunishRate': item.PunishRate,
					'DateValid': item.DateValid,
				}
				typeList.append(verb)
				db.session.close()
			return {'error':0,'typeList':typeList}
		except:
			db.session.close()
			return ERROR_NUM['failTOGetTypeList']

	def post(self):
		if 'userinfo' not in session:
			return ERROR_NUM['hasNotLogin']
		if session['userinfo']['rdAdminRoles'] != 8:
			return ERROR_NUM['noPermission']
		parser = reqparse.RequestParser(trim=True)
		parser.add_argument('rdType', type=int, required=True, help="params `rdType` refuse!")
		parser.add_argument('rdTypeName', type=str, required=True, help="params `rdTypeName` refuse!")
		parser.add_argument('CanLendQty', type=int, required=True, help="params `CanLendQty` refuse!")
		parser.add_argument('CanLendDay', type=int, required=True, help="params `CanLendDay` refuse!")
		parser.add_argument('CanContinueTimes', type=int, required=True, help="params `CanContinueTimes` refuse!")
		parser.add_argument('PunishRate', type=float, required=True, help="params `PunishRate` refuse!")
		parser.add_argument('DateValid', type=int, required=True, help="params `DateValid` refuse!")
		args = parser.parse_args(strict=True)
		segment = TbReaderType(
			rdType=args['rdType'],
			rdTypeName=args['rdTypeName'],
			CanLendQty=args['CanLendQty'],
			CanLendDay=args['CanLendDay'],
			CanContinueTimes=args['CanContinueTimes'],
			PunishRate=args['PunishRate'],
			DateValid=args['DateValid']
		)
		try:
			db.session.add(segment)
			db.session.commit()
			return {'error':0,'msg':'创建用户类型成功！','createData':args}
		except Exception as e:
			db.session.rollback()
			return ERROR_NUM['failToCreateUserType']

	def put(self,rdType=None):
		if rdType is None:
			return ERROR_NUM['paramsErr']
		if 'userinfo' not in session:
			return ERROR_NUM['hasNotLogin']
		if session['userinfo']['rdAdminRoles'] != 8:
			return ERROR_NUM['noPermission']
		parser = reqparse.RequestParser(trim=True)
		# parser.add_argument('rdType', type=int, required=True, help="params `rdType` refuse!")
		parser.add_argument('rdTypeName', type=str, required=False, help="params `rdTypeName` refuse!")
		parser.add_argument('CanLendQty', type=int, required=False, help="params `CanLendQty` refuse!")
		parser.add_argument('CanLendDay', type=int, required=False, help="params `CanLendDay` refuse!")
		parser.add_argument('CanContinueTimes', type=int, required=False, help="params `CanContinueTimes` refuse!")
		parser.add_argument('PunishRate', type=float, required=False, help="params `PunishRate` refuse!")
		parser.add_argument('DateValid', type=int, required=False, help="params `DateValid` refuse!")
		args = parser.parse_args(strict=True)
		putData = {}
		for item in args:
			if args[item] is not None:
				putData[item] = args[item]
		if len(putData) ==0:
			return ERROR_NUM['paramsErr']
		try:
			execute = TbReaderType.query.filter_by(rdType=rdType).update(putData)
			if execute == 0 :
				return ERROR_NUM['failToUpdateUserType']
			db.session.commit()
			return {'error':0,'msg':'修改成功！','updatedDate':putData}
		except Exception as e:
			db.session.rollback()
			return ERROR_NUM['failToUpdateUserType']

class User(Resource):
	def get(self, rdID=None):
		if rdID is None:
			return ERROR_NUM['paramsErr']
		if 'userinfo' not in session:
			return ERROR_NUM['hasNotLogin']
		if session['userinfo']['rdAdminRoles'] != 8 and rdID != session['userinfo']['rdID']:
			return ERROR_NUM['noPermission']
		try:
			user = TbReader.query.filter_by(rdID=rdID).first()

			if user is None:
				return ERROR_NUM['userNotExist']
			doNotReturnedQuery = TbBorrow.query.filter_by(rdID=rdID, lsHasReturn=False).all()
			doNotReturnedBooks = []
			rdType = TbReaderType.query.filter_by(rdType=user.rdType).first()
			for item in doNotReturnedQuery:
				book = TbBook.query.filter_by(bkID=item.bkID).first()
				verb = {
					'rdID': rdID,
					'BorrowID': item.BorrowID,
					'bkID': item.bkID,
					'bkCode': book.bkCode,
					'bkName': book.bkName,
					'bkAuthor': book.bkAuthor,
					'ldContinueTimes': item.ldContinueTimes,
					'ldDateOut': str(item.ldDateOut),
					'ldDateRetPlan': str(item.ldDateRetPlan),
					'ldOverDay': item.ldOverDay,
					'ldOverMoney': float(item.ldOverMoney),
					'bkStatus': book.bkStatus
				}
				now = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
				                                 '%Y-%m-%d %H:%M:%S')
				if now > datetime.datetime.strptime(str(item.ldDateRetPlan), '%Y-%m-%d %H:%M:%S'):
					d = now - datetime.datetime.strptime(str(item.ldDateRetPlan), '%Y-%m-%d %H:%M:%S')
					verb['ldOverDay'] = str(d.days)
					verb['ldOverMoney'] = d.days * 0.1 * (1 - rdType.PunishRate)  # 1毛乘以比率
					print(d.days)
					TbBorrow.query.filter_by(BorrowID=item.BorrowID).update({
						'ldOverDay' : verb['ldOverDay'],
						'ldOverMoney' : verb['ldOverMoney']
					})
					db.session.commit()

				doNotReturnedBooks.append(verb)

			userInfo = {
				'rdID': user.rdID,
				'rdName': user.rdName,
				'rdSex': user.rdSex,
				'rdType': user.rdType,
				'rdDept': user.rdDept,
				'rdPhone': user.rdPhone,
				'rdEmail': user.rdEmail,
				'rdPhoto': user.rdPhoto,
				'rdStatus': user.rdStatus,
				'rdBorrowQty': user.rdBorrowQty,
				'CanLendQty': rdType.CanLendQty,
				'rdAdminRoles': user.rdAdminRoles,
				'doNotReturnedBooks': doNotReturnedBooks
			}
			return {'error': 0, 'userInfo': userInfo}

		except SQL.exc.OperationalError as e:
			return ERROR_NUM['SQLOperate']

	def post(self, rdID=None):
		if rdID != None:
			return ERROR_NUM['paramsErr']
		if 'userinfo' not in session:
			return ERROR_NUM['hasNotLogin']
		if session['userinfo']['rdAdminRoles'] != 8:
			return ERROR_NUM['noPermission']
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

		if args['rdStatus'] > len(userStatusTable):
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
			rdAdminRoles=args['rdAdminRoles']
		)
		try:
			db.session.add(segment)
			db.session.flush()
			db.session.commit()
			return {'error': 0, 'msg': 'Yes', 'rdID': segment.rdID}
		except:
			db.session.rollback()  # 回滚
			return ERROR_NUM['failToCreateUser']

	def put(self, rdID=None):
		if rdID is None:
			return ERROR_NUM['paramsErr']
		if 'userinfo' not in session:
			return ERROR_NUM['hasNotLogin']

		parser = reqparse.RequestParser(trim=True)
		parser.add_argument('rdName', type=str, required=False, help="params `rdName` refuse!")
		parser.add_argument('rdSex', type=str, required=False, help="params `rdSex` refuse!")
		parser.add_argument('rdType', type=str, required=False, help="params `rdType` refuse!")
		parser.add_argument('rdDept', type=str, required=False, help="params `rdDept` refuse!")
		parser.add_argument('rdPhone', type=str, required=False, help="params `rdPhone` refuse!")
		parser.add_argument('rdEmail', type=str, required=False, help="params `rdEmail` refuse!")
		parser.add_argument('rdPhoto', type=str, required=False, help="params `rdPhoto` refuse!")
		parser.add_argument('rdStatus', type=int, required=False, help="params `rdStatus` refuse!")
		parser.add_argument('rdPwd', type=str, required=False, help="params `rdPwd` refuse!")
		parser.add_argument('rdAdminRoles', type=str, required=False, help="params `rdAdminRoles` refuse!")

		args = parser.parse_args(strict=True)
		if rdID in args or len(args) < 1:
			return ERROR_NUM['paramsErr']

		putData = {}
		for item in args:
			if args[item] is not None and args[item] != '':
				if item == 'rdEmail' and re.match(emailReg, args['rdEmail']) == False:
					return ERROR_NUM['paramsErr']

				if item == 'rdStatus':
					if args['rdStatus'] > len(userStatusTable):
						return ERROR_NUM['paramsErr']
					args[item] = userStatusTable[args[item]]
				if item == 'rdPwd':
					m = md5()
					rdpwd = m.update(args[item].strip().encode("utf8"))
					rdpwd = m.hexdigest()
					args[item] = rdpwd

				putData[item] = args[item].strip()
		if len(putData) == 0:
			return ERROR_NUM['paramsErr']
		if session['userinfo']['rdAdminRoles'] != 8:
			if 'rdPwd' in putData and len(putData) > 1:
				return ERROR_NUM['noPermission']
			elif 'rdPwd' not in putData and len(putData) > 1:
				return ERROR_NUM['noPermission']
		try:
			user = TbReader.query.filter_by(rdID=rdID).first()
			if user is None:
				return ERROR_NUM['userNotExist']
			execute = TbReader.query.filter_by(rdID=rdID).update(putData)
			if execute is 0:
				return ERROR_NUM['failToUpdateUser']
			db.session.commit()
			return {'error': 0, 'msg': '更新用户信息成功！', 'rdID': rdID, 'updateData': putData}
		except SQL.exc.OperationalError as e:
			db.session.rollback()
			return ERROR_NUM['SQLOperate']

	def delete(self, rdID=None):
		if rdID is None:
			return ERROR_NUM['paramsErr']
		if 'userinfo' not in session:
			return ERROR_NUM['hasNotLogin']
		if session['userinfo']['rdAdminRoles'] != 8:
			return ERROR_NUM['noPermission']
		try:
			execute = TbReader.query.filter_by(rdID=rdID).delete()
			if execute is 0:
				db.session.rollback()
				return ERROR_NUM['failToDeleteUser']
			db.session.commit()
			return {'error': 0, 'msg': '删除用户成功！', 'rdID': rdID}
		except:
			db.session.rollback()
			return ERROR_NUM['SQLOperate']


class reRegister(Resource):
	def post(self, rdID=None):
		if rdID is None and rdID != '':
			return ERROR_NUM['paramsErr']
		if 'userinfo' not in session:
			return ERROR_NUM['hasNotLogin']
		if session['userinfo']['rdAdminRoles'] != 8:
			return ERROR_NUM['noPermission']
		try:
			reader = TbReader.query.filter_by(rdID=rdID).first()
			if reader is None:
				return ERROR_NUM['userNotExist']
			if reader.rdStatus == '注销':
				return ERROR_NUM['userStatusError']
			segment = TbReader(
				rdName=reader.rdName,
				rdSex=reader.rdSex,
				rdType=reader.rdType,
				rdDept=reader.rdDept,
				rdPhone=reader.rdPhone,
				rdEmail=reader.rdEmail,
				rdDateReg=reader.rdDateReg,
				rdPhoto=reader.rdPhoto,
				rdStatus=reader.rdStatus,
				rdBorrowQty=reader.rdBorrowQty,
				rdPwd=reader.rdPwd,
				rdAdminRoles=reader.rdAdminRoles
			)
			execute = db.session.add(segment)
			db.session.flush()
			dispear = TbReader.query.filter_by(rdID=rdID).update({'rdStatus': '注销'})
			borrow = TbBorrow.query.filter_by(rdID=rdID).update({'rdID': segment.rdID})
			db.session.commit()
			return {'error': 0, 'msg': '补办成功！', 'oldRdID': rdID, 'newRdID': segment.rdID}
		except:
			db.session.rollback()
			return ERROR_NUM['failToReRegister']
