import flask_restful as restful
parser = restful.reqparse.RequestParser()
class Login(restful.Resourses):
	def post(self):
		return {'hello':'flask'}