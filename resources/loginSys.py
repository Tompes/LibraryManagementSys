from flask import Flask ,jsonify
from flask_restful import Resource,reqparse
from common.models import TbReaderType
from common.models import TbBook
from common.models import TbReader
from common.models import TbBorrow

from common.errorTable import ERROR_NUM
import sqlalchemy as SQL
from hashlib import md5
# parser = restful.reqparse
# Resources = restful.Resource
class Login(Resource):
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('username', type=str, required=True,help="`username` can't be blank!")
		parser.add_argument('passwd', type=str, required=True,help="`passwd` can't be blank!")

		args = parser.parse_args()
		if 'username' and 'passwd' in args:
			uInfo = TbReader.query.filter_by(rdID=args['username']).first()
			if uInfo == None:
				return ERROR_NUM['LoginFail'],404
			return {'user':args['username'] , 'pass' : args['passwd']}
		else:
			return ERROR_NUM['unknow'],404

	def get(self):
		output = []
		try:
			data = TbReaderType.query.all()
			for item in data:
				varb = {}
				varb['rdType'] = item.rdType
				varb['rdTypeName'] = item.rdTypeName
				varb['CanLendQty'] = item.CanLendQty
				varb['CanLendDay'] = item.CanLendDay
				varb['CanContinueTimes'] = item.CanContinueTimes
				varb['PunishRate'] = item.PunishRate
				varb['DateValid'] = item.DateValid
				output.append(varb)
			return output
		except SQL.exc.OperationalError as e:
			return ERROR_NUM['SQLOperate'],500
