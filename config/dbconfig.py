from flask import Flask
from flask_sqlalchemy import SQLAlchemy

dbConf = {
	'userName':'sa',
	'password':'12345677',
	'Server'  :'.',
	'dbName'  :'BooksDatabase'
}

dbURI = 'mssql+pymssql://{0}:{1}@{2}/{3}'.format(
	dbConf['userName'],
	dbConf['password'],
	dbConf['Server'],
	dbConf['dbName']
)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = dbURI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def db_init():
    db.create_all()