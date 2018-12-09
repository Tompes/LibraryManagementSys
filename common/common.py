defaultPhoto = {
	'woman': '/static/assets/images/woman.png',
	'man': '/static/assets/images/man.png'
}
defaultBookCover = '/static/assets/images/books/default.jpg'
userStatusTable = [
	'注销',
	'有效',
	'挂失',
]
bookStatusTable = [
	'借出',
	'在馆',
	'遗失',
	'变卖',
	'销毁'
]
emailReg = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'  # 邮箱验证


def addslashes(s):
	d = {'"': '\\"', "'": "\\'", "\0": "\\\0", "\\": "\\\\","-":"\\-"}
	return ''.join(d.get(c, c) for c in s)
