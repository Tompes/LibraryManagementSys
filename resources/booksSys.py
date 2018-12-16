from flask_restful import Resource, reqparse
from common.models import TbReaderType
from common.models import TbBook
from common.models import TbReader
from common.models import TbBorrow
from hashlib import md5
from common.errorTable import ERROR_NUM
from common.common import defaultBookCover, bookStatusTable,addslashes
import sqlalchemy as SQL
import time
import re
from config.dbconfig import db

class BookList(Resource):
	def get(self,search=None):
		parser = reqparse.RequestParser(trim=True)
		parser.add_argument('bkID', type=str, required=False, help="params `bkID` refuse!")
		parser.add_argument('bkCode', type=str, required=False, help="params `bkCode` refuse!")
		parser.add_argument('bkName', type=str, required=False, help="params `bkName` refuse!")
		parser.add_argument('bkAuthor', type=str, required=False, help="params `bkAuthor` refuse!")
		parser.add_argument('bkDatePress', type=str, required=False, help="params `bkDatePress` refuse!")
		parser.add_argument('bkBrief', type=str, required=False, help="params `bkBrief` refuse!")
		parser.add_argument('bkPress', type=str, required=False, help="params `bkPress` refuse!")
		parser.add_argument('bkCatalog', type=str, required=False, help="params `bkCatalog` refuse!")

		args = parser.parse_args(strict=True)

		filterArgs = {}
		for item in args:
			if args[item] is not None and args[item] != '':
				filterArgs[item] = args[item]
		t = ''
		i = 0
		for k in filterArgs.keys():
			if i == 0:
				t += k + " like '%" + addslashes(filterArgs[k]) + "%' "
			else:
				t += " and " + k + " like '%" + addslashes(filterArgs[k]) + "%' "
			i += 1
		try:
			books = []
			if search is None:
				books = TbBook.query.all()
			if search == 'search':
				print('select * from Tb_Book where {0}'.format(t))
				books = db.session.execute('select * from Tb_Book where {0}'.format(t))
			bookList = []
			for item in books:
				verb = {
					'bkID': item.bkID,
					'bkCode': item.bkCode,
					'bkName': item.bkName,
					'bkAuthor': item.bkAuthor,
					'bkPress': item.bkPress,
					'bkDatePress': str(item.bkDatePress),
					'bkISBN': item.bkISBN,
					'bkCatalog': item.bkCatalog,
					'bkLanguage': item.bkLanguage,
					'bkPages': item.bkPages,
					'bkPrice': float(item.bkPrice),
					'bkDateIn': str(item.bkDateIn),
					'bkBrief': item.bkBrief,
					'bkCover': item.bkCover,
					'bkStatus': item.bkStatus
				}
				bookList.append(verb)
			return {'error': 0, 'bookList': bookList}
		except:
			return ERROR_NUM['queryFail']


class Book(Resource):
	def get(self, bkID=None):
		if bkID is None:
			return ERROR_NUM['paramsErr'], 400
		try:
			book = TbBook.query.filter_by(bkID=bkID).first()
			if book is None:
				return ERROR_NUM['bookNotExist']
			bookInfo = {
				'bkID': book.bkID,
				'bkCode': book.bkCode,
				'bkName': book.bkName,
				'bkAuthor': book.bkAuthor,
				'bkPress': book.bkPress,
				'bkDatePress': str(book.bkDatePress),
				'bkISBN': book.bkISBN,
				'bkCatalog': book.bkCatalog,
				'bkLanguage': book.bkLanguage,
				'bkPages': book.bkPages,
				'bkPrice': float(book.bkPrice),
				'bkDateIn': str(book.bkDateIn),
				'bkBrief': book.bkBrief,
				'bkCover': book.bkCover,
				'bkStatus': book.bkStatus,
			}
			return {'error': 0, 'bookInfo': bookInfo}
		except:
			return ERROR_NUM['SQLOperate']

	def post(self, bkID=None):
		if bkID is not None:
			return ERROR_NUM['paramsErr']

		parser = reqparse.RequestParser(trim=True)
		parser.add_argument('bkCode', type=str, required=True, help="params `bkCode` refuse!")
		parser.add_argument('bkName', type=str, required=True, help="params `bkName` refuse!")
		parser.add_argument('bkAuthor', type=str, required=True, help="params `bkAuthor` refuse!")
		parser.add_argument('bkPress', type=str, required=True, help="params `bkPress` refuse!")
		parser.add_argument('bkDatePress', type=str, required=True, help="params `bkDatePress` refuse!")
		parser.add_argument('bkISBN', type=str, required=True, help="params `bkISBN` refuse!")
		parser.add_argument('bkCatalog', type=str, required=True, help="params `bkCatalog` refuse!")
		parser.add_argument('bkLanguage', type=int, required=True, help="params `bkLanguage` refuse!")
		parser.add_argument('bkPages', type=int, required=True, help="params `bkPages` refuse!")
		parser.add_argument('bkPrice', type=float, required=True, help="params `bkPrice` refuse!")
		# parser.add_argument('bkDateIn', type=str, required=True, help="params `bkDateIn` refuse!")
		parser.add_argument('bkBrief', type=str, required=True, help="params `bkBrief` refuse!")
		parser.add_argument('bkCover', type=str, required=False, help="params `bkCover` refuse!")
		parser.add_argument('bkStatus', type=int, required=True, help="params `bkStatus` refuse!")

		args = parser.parse_args(strict=True)
		if args['bkCover'] is None:
			args['bkCover'] = defaultBookCover
		if args['bkStatus'] > len(bookStatusTable):
			return ERROR_NUM['paramsErr']

		segment = TbBook(
			bkCode=args['bkCode'],
			bkName=args['bkName'],
			bkAuthor=args['bkAuthor'],
			bkPress=args['bkPress'],
			bkDatePress=args['bkDatePress'],
			bkISBN=args['bkISBN'],
			bkCatalog=args['bkCatalog'],
			bkLanguage=args['bkLanguage'],
			bkPages=args['bkPages'],
			bkPrice=args['bkPrice'],
			bkDateIn=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
			bkCover=args['bkCover'],
			bkBrief=args['bkBrief'],
			bkStatus=bookStatusTable[args['bkStatus']]
		)

		try:
			db.session.add(segment)
			db.session.flush()
			db.session.commit()
			return {
				'error': 0, 'msg': '新书上架成功！',
				'bkID': segment.bkID,
				'bkCode': segment.bkCode,
				'bkName': segment.bkName
			}
		except:
			db.session.rollback()
			return ERROR_NUM['failToAddBooks']

	def put(self, bkID=None):
		if bkID is None:
			return ERROR_NUM['paramsErr']

		parser = reqparse.RequestParser(trim=True)
		parser.add_argument('bkCode', type=str, required=False, help="params `bkCode` refuse!")
		parser.add_argument('bkName', type=str, required=False, help="params `bkName` refuse!")
		parser.add_argument('bkAuthor', type=str, required=False, help="params `bkAuthor` refuse!")
		parser.add_argument('bkPress', type=str, required=False, help="params `bkPress` refuse!")
		parser.add_argument('bkDatePress', type=str, required=False, help="params `bkDatePress` refuse!")
		parser.add_argument('bkISBN', type=str, required=False, help="params `bkISBN` refuse!")
		parser.add_argument('bkCatalog', type=str, required=False, help="params `bkCatalog` refuse!")
		parser.add_argument('bkLanguage', type=int, required=False, help="params `bkLanguage` refuse!")
		parser.add_argument('bkPages', type=int, required=False, help="params `bkPages` refuse!")
		parser.add_argument('bkPrice', type=float, required=False, help="params `bkPrice` refuse!")
		# parser.add_argument('bkDateIn', type=str, required=False, help="params `bkDateIn` refuse!")
		parser.add_argument('bkBrief', type=str, required=False, help="params `bkBrief` refuse!")
		parser.add_argument('bkCover', type=str, required=False, help="params `bkCover` refuse!")
		parser.add_argument('bkStatus', type=int, required=False, help="params `bkStatus` refuse!")

		args = parser.parse_args(strict=True)

		if 'bkID' in args or len(args) < 1:
			return ERROR_NUM['paramsErr'], 400

		putData = {}

		for item in args:
			if args[item] is not None:
				if item == 'bkStatus':
					if args['bkStatus'] > len(bookStatusTable):
						return ERROR_NUM['paramsErr'], 400
					args[item] = bookStatusTable[args[item]]
				putData[item] = args[item]

		try:
			book = TbBook.query.filter_by(bkID=bkID).first()
			if book is None:
				return ERROR_NUM['bookNotExist']

			execute = TbBook.query.filter_by(bkID=bkID).update(putData)
			if execute is 0:
				return ERROR_NUM['failToUpdateBook'], 400
			db.session.flush()
			db.session.commit()
			return {'error': 0, 'msg': '更新书籍信息成功！', 'bkID':bkID ,'updateData': putData}
		except:
			db.session.rollback()
			return ERROR_NUM['SQLOperate'], 500

	def delete(self, bkID=None):
		if bkID is None:
			return ERROR_NUM['paramsErr']
		try:
			book = TbBook.query.filter_by(bkID=bkID).first()
			if book is None:
				return ERROR_NUM['bookNotExist']
			execute = TbBook.query.filter_by(bkID=bkID).delete()
			if execute is 0:
				db.session.rollback()
				return ERROR_NUM['failToDeleteBook']
			db.session.flush()
			db.session.commit()
			return {'error': 0, 'msg': '删除书籍成功！', 'bkID': bkID, 'bkName': book.bkName}
		except:
			db.session.rollback()
			return ERROR_NUM['SQLOperate']
