from flask import Flask ,jsonify
import flask_restful as restful
from common.models import TbReaderType
# parser = restful.reqparse.RequestParser()
Resources = restful.Resource
class Login(Resources):
	def post(self):
		return {'hello':'flask'}
	def get(self):
		output = []
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