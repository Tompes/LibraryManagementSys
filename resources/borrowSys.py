from flask_restful import Resource, reqparse
from common.models import TbReaderType
from common.models import TbBook
from common.models import TbReader
from common.models import TbBorrow
from hashlib import md5
from common.errorTable import ERROR_NUM
from common.common import defaultBookCover, bookStatusTable, userStatusTable
import sqlalchemy as SQL
import time
from dateutil import parser as dateParser
import datetime
import re
from config.dbconfig import db


class BorrowList(Resource):
	def get(self, lsHasReturn=None):
		type = '所有记录'
		try:
			borrow = []
			if lsHasReturn is None:
				borrow = TbBorrow.query.all()
			elif lsHasReturn == 0:  # 查未归还的
				borrow = TbBorrow.query.filter_by(lsHasReturn=0)
				type = '所有未还记录'
			elif lsHasReturn == 1:
				borrow = TbBorrow.query.filter_by(lsHasReturn=1)
				type = '所有已还记录'
			else:
				return ERROR_NUM['paramsErr']
			borrowList = []
			for item in borrow:
				verb = {
					'BorrowID': item.BorrowID,
					'rdID': item.rdID,
					'bkID': item.bkID,
					'ldContinueTimes': item.ldContinueTimes,
					'ldDateOut': str(item.ldDateOut),  # 类型转换 datetime -> str
					'ldDateRetPlan': str(item.ldDateRetPlan),  # 类型转换 datetime -> str
					'ldDateRetAct': str(item.ldDateRetAct),  # 类型转换 datetime -> str
					'ldOverDay': item.ldOverDay,
					'ldOverMoney': float(item.ldOverMoney),  # 类型转换 MONEY -> float
					'ldPunishMoney': float(item.ldPunishMoney),  # 类型转换 MONEY -> float
					'lsHasReturn': item.lsHasReturn,
					'OperatorLend': item.OperatorLend,
					'OperatorRet': item.OperatorRet
				}
				borrowList.append(verb)
			return {'error': 0, 'type': type, 'borrowList': borrowList}
		except:
			return ERROR_NUM['queryFail']


class Borrow(Resource):
	def get(self, borrowID=None):
		if borrowID is None:
			return ERROR_NUM['paramsErr']
		try:
			borrow = TbBorrow.query.filter_by(borrowID=borrowID).first()
			if borrow is None:
				return ERROR_NUM['borrowSegmentNotExist']
			borrowInfo = {
				'BorrowID': borrow.BorrowID,
				'rdID': borrow.rdID,
				'bkID': borrow.bkID,
				'ldContinueTimes': borrow.ldContinueTimes,
				'ldDateOut': borrow.ldDateOut,
				'ldDateRetPlan': borrow.ldDateRetPlan,
				'ldDateRetAct': borrow.ldDateRetAct,
				'ldOverDay': borrow.ldOverDay,
				'ldOverMoney': borrow.ldOverMoney,
				'ldPunishMoney': borrow.ldPunishMoney,
				'lsHasReturn': borrow.lsHasReturn,
				'OperatorLend': borrow.OperatorLend,
				'OperatorRet': borrow.OperatorRet
			}
			return {'error': 0, 'borrowInfo': borrowInfo}
		except:
			return ERROR_NUM['SQLOperate']

	def post(self, borrowID=None):
		if borrowID is not None:
			return ERROR_NUM['paramsErr']

		parser = reqparse.RequestParser(trim=True)
		parser.add_argument('rdID', type=int, required=True, help="params `rdID` refuse!")
		parser.add_argument('bkID', type=int, required=True, help="params `bkID` refuse!")
		parser.add_argument('OperatorLend', type=str, required=True, help="params `OperatorLend` refuse!")
		parser.add_argument('OperatorRet', type=str, required=False, help="params `OperatorRet` refuse!")

		args = parser.parse_args(strict=True)

		try:  # 查看书籍和用户状态
			reader = TbReader.query.filter_by(rdID=args['rdID']).first()
			book = TbBook.query.filter_by(bkID=args['bkID']).first()
			if reader is None:
				return ERROR_NUM['userNotExist']
			if book is None:
				return ERROR_NUM['bookNotExist']

			reader_type = TbReaderType.query.filter_by(rdType=reader.rdType).first()
			if reader_type.CanLendQty - reader.rdBorrowQty <= 0:  # 借书数量到上限
				return ERROR_NUM['canNotBorrowAnyMore']
			if book.bkStatus != '在馆':  # 书籍状态不在馆
				return ERROR_NUM['bookStatusErr']
		except:
			return ERROR_NUM['SQLOperate']
		timeStamp = time.time()
		timeArray = time.localtime(timeStamp)
		segment = TbBorrow(
			rdID=args['rdID'],
			bkID=args['bkID'],
			ldContinueTimes=0,
			ldDateOut=time.strftime('%Y-%m-%d %H:%M:%S', timeArray),
			ldDateRetPlan=time.strftime('%Y-%m-%d %H:%M:%S',
			                            time.localtime(timeStamp + (60 * 60 * 24 * reader_type.CanLendDay))),  # 可借时长
			ldDateRetAct=None,
			ldOverDay=0,
			ldOverMoney=0.00,
			ldPunishMoney=0.00,
			lsHasReturn=0,  # 默认未归还
			OperatorLend=args['OperatorLend'],  # 借书操作员
			OperatorRet=None
		)

		try:
			db.session.add(segment)
			db.session.flush()
			bk = TbBook.query.filter_by(bkID=args['bkID']).update({'bkStatus': bookStatusTable[0]})
			bkInfo = TbBook.query.filter_by(bkID=args['bkID']).first()
			rd = TbReader.query.filter_by(rdID=args['rdID']).first()
			rdExec = TbReader.query.filter_by(rdID=args['rdID']).update({'rdBorrowQty': rd.rdBorrowQty + 1})
			if bk is 0:
				db.session.rollback()
				return ERROR_NUM['failToBorrowBook']
			if rdExec is 0:
				db.session.rollback()
				return ERROR_NUM['failToBorrowBook']
			db.session.commit()
			return {
				'error': 0,
				'msg': '借书成功！',
				'borrowID': segment.BorrowID,
				'rdID': segment.rdID,
				'bkID': segment.bkID,
				'bkName': bkInfo.bkName,
				'ldDateRetPlan': segment.ldDateRetPlan
			}
		except:
			db.session.rollback()
			return ERROR_NUM['failToBorrowBook']

	def put(self, borrowID=None):  # 续借、修改借阅信息
		if borrowID is None:
			return ERROR_NUM['paramsErr']
		parser = reqparse.RequestParser(trim=True)
		parser.add_argument('ldContinueTimes', type=int, required=False, help="params `ldContinueTimes` refuse!")
		parser.add_argument('ldDateRetPlan', type=str, required=False, help="params `ldDateRetPlan` refuse!")
		# parser.add_argument('ldOverDay', type=int, required=True, help="params `rdID` refuse!")
		parser.add_argument('ldOverMoney', type=float, required=False, help="params `ldOverMoney` refuse!")
		parser.add_argument('ldPunishMoney', type=float, required=False, help="params `ldPunishMoney` refuse!")
		parser.add_argument('lsHasReturn', type=int, required=False, help="params `lsHasReturn` refuse!")
		parser.add_argument('OperatorLend', type=str, required=False, help="params `OperatorLend` refuse!")
		parser.add_argument('OperatorRet', type=str, required=False, help="params `OperatorRet` refuse!")

		args = parser.parse_args(strict=True)
		putData = {}
		for item in args:
			if args[item] is not None and args[item] != '':
				putData[item] = args[item]

		try:
			borrow = TbBorrow.query.filter_by(borrowID=borrowID).first()
			if borrow is None:
				return ERROR_NUM['borrowSegmentNotExist']
			execute = TbBorrow.query.filter_by(borrowID=borrowID).update(putData)
			if execute is 0:
				return ERROR_NUM['failToUpdateBorrowSegment']
			return {'error': 0, 'msg': '更新成功！', 'borrowID': borrowID, 'updateData': putData}
		except:
			return ERROR_NUM['SQLOperate']

	def delete(self, borrowID=None):  # 还书功能。 借书元组不用删除，永久保存.
		parser = reqparse.RequestParser(trim=True)
		parser.add_argument('OperatorRet', type=str, required=True, help="params `OperatorRet` refuse!")
		args = parser.parse_args(strict=True)

		if borrowID is None:
			return ERROR_NUM['paramsErr']

		try:
			borrow = TbBorrow.query.filter_by(BorrowID=borrowID).first()
			if borrow is None:
				return ERROR_NUM['borrowSegmentNotExist']
			elif borrow.lsHasReturn is True:
				return ERROR_NUM['bookHasBeenReturned']
			reader = TbReader.query.filter_by(rdID=borrow.rdID).first()
			if reader is None:
				return ERROR_NUM['userNotExist']
			book = TbBook.query.filter_by(bkID=borrow.bkID).first()
			if book is None:
				return ERROR_NUM['bookNotExist']

			bkRet = TbBorrow.query.filter_by(BorrowID=borrowID).update({
				'ldDateRetAct': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
				'OperatorRet': args['OperatorRet'],
				'lsHasReturn': 1
			})
			if bkRet is 0:
				db.session.rollback()
				return ERROR_NUM['failToUpdateBorrowSegment']
			bkStatusChange = TbBook.query.filter_by(bkID=borrow.bkID).update({'bkStatus': bookStatusTable[1]})
			if bkStatusChange is 0:
				db.session.rollback()
				return ERROR_NUM['failToBorrowBook']
			rdBrQty = TbReader.query.filter_by(rdID=borrow.rdID).update({'rdBorrowQty': reader.rdBorrowQty - 1})
			if rdBrQty is 0:
				db.session.rollback()
				return ERROR_NUM['failToUpdateUser']
			db.session.commit()
			return {
				'error': 0,
				'msg': '还书成功',
				'borrowInfo': {
					'borrowID': borrowID,
					'rdID': reader.rdID,
					'rdName': reader.rdName,
					'bkID': book.bkID,
					'bkName': book.bkName,
					'OperatorRet': args['OperatorRet']
				},
			}
		except:
			db.session.rollback()
			return ERROR_NUM['failToReturnBook']


class BookContinue(Resource):
	def put(self, borrowID=None):
		if borrowID is None:
			return ERROR_NUM['borrowSegmentNotExist']
		try:
			borrow = TbBorrow.query.filter_by(BorrowID=borrowID).first()
			if borrow is None:
				return ERROR_NUM['borrowSegmentNotExist']
			reader = TbReader.query.filter_by(rdID=borrow.rdID).first()
			if reader is None:
				return ERROR_NUM['userNotExist']
			readerType = TbReaderType.query.filter_by(rdType=reader.rdType).first()

			if borrow.ldContinueTimes >= readerType.CanContinueTimes:
				return ERROR_NUM['limitOfArrival']
			if reader.rdStatus != userStatusTable[1]:
				return ERROR_NUM['forbiddenOperation']

			continueDate = dateParser.parse(borrow.ldDateRetPlan) + datetime.timedelta(days=readerType.CanLendDay)
			execute = TbBorrow.query.filter_by(BorrowID=borrowID).update({
				'ldContinueTimes':borrow.ldContinueTimes+1,
				'ldDateRetPlan':continueDate.strftime('%Y-%m-%d %H:%M:%S')
			})
			if execute is 0:
				db.session.rollback()
				return ERROR_NUM['failToContinue']
			execute = TbBorrow.query(BorrowID=borrowID).update({'ldContinueTimes':borrow.ldContinueTimes+1})
			if execute is 0:
				db.session.rollback()
				return ERROR_NUM['failToContinue']
		except:
			db.session.rollback()
			return ERROR_NUM['failToContinue']
