from flask import session
from flask_restful import Resource, reqparse
from common.models import TbReaderType
from common.models import TbBook
from common.models import TbReader
from common.models import TbBorrow
from hashlib import md5
from common.errorTable import ERROR_NUM
from common.common import defaultBookCover, bookStatusTable, userStatusTable, addslashes
import sqlalchemy as SQL
import time
from dateutil import parser as dateParser
import datetime
import re
from config.dbconfig import db


class BackUp(Resource):
	def get(self, Table=None):
		if Table is None:
			return ERROR_NUM['paramsErr']
		sql = 'select * from ' + addslashes(Table) + 'where 1'
		print(sql)
		try:
			if Table == 'Tb_Book':
				data = db.session.execute(sql)
				return
			elif Table == 'Tb_Borrow':
				data = db.session.execute(sql)
				return
			elif Table == 'Tb_Reader':
				data = db.session.execute(sql)
				return
			elif Table == 'Tb_ReaderType':
				data = db.session.execute(sql)
				return
			else:
				return ERROR_NUM['paramsErr']
		except:
			return ERROR_NUM['failToBackUp']
