# coding: utf-8
# DataBase Course Design for CSZ2018001 of Yangtze University
# Design and Coding by Tompes
# Github: https://Github.com/Tompes/LibraryManagementSys

# This part codes are generate by using flask-sqlacodegen plugin (Awesome Tool!!!)
from config.dbconfig import db
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, LargeBinary, Numeric, SmallInteger, Text, Unicode
from sqlalchemy.dialects.mssql.base import BIT, MONEY
from sqlalchemy.dialects.mssql.base import BIT, MONEY
from sqlalchemy.schema import FetchedValue
from sqlalchemy.orm import relationship


class TbBook(db.Model):
    __tablename__ = 'Tb_Book'

    bkID = db.Column(db.Integer, primary_key=True)
    bkCode = db.Column(db.Unicode(20))
    bkName = db.Column(db.Unicode(50))
    bkAuthor = db.Column(db.Unicode(30))
    bkPress = db.Column(db.Unicode(50))
    bkDatePress = db.Column(db.DateTime)
    bkISBN = db.Column(db.Unicode(15))
    bkCatalog = db.Column(db.Unicode(30))
    bkLanguage = db.Column(db.SmallInteger)
    bkPages = db.Column(db.Integer)
    bkPrice = db.Column(MONEY)
    bkDateIn = db.Column(db.DateTime)
    bkBrief = db.Column(db.Text(2147483647, 'Chinese_PRC_CI_AS'))
    bkCover = db.Column(db.String(100))
    bkStatus = db.Column(db.Unicode(2))


class TbBorrow(db.Model):
    __tablename__ = 'Tb_Borrow'

    BorrowID = db.Column(db.Integer, primary_key=True)
    rdID = db.Column(db.ForeignKey('Tb_Reader.rdID'))
    bkID = db.Column(db.ForeignKey('Tb_Book.bkID'))
    ldContinueTimes = db.Column(db.Integer, server_default=db.FetchedValue())
    ldDateOut = db.Column(db.DateTime)
    ldDateRetPlan = db.Column(db.DateTime)
    ldDateRetAct = db.Column(db.DateTime)
    ldOverDay = db.Column(db.Integer)
    ldOverMoney = db.Column(MONEY)
    ldPunishMoney = db.Column(MONEY)
    lsHasReturn = db.Column(BIT, server_default=db.FetchedValue())
    OperatorLend = db.Column(db.Unicode(20))
    OperatorRet = db.Column(db.Unicode(20))

    Tb_Book = db.relationship('TbBook', primaryjoin='TbBorrow.bkID == TbBook.bkID', backref='tb_borrows')
    Tb_Reader = db.relationship('TbReader', primaryjoin='TbBorrow.rdID == TbReader.rdID', backref='tb_borrows')


class TbReader(db.Model):
    __tablename__ = 'Tb_Reader'

    rdID = db.Column(db.Integer, primary_key=True)
    rdName = db.Column(db.Unicode(20))
    rdSex = db.Column(db.Unicode(1))
    rdType = db.Column(db.ForeignKey('Tb_ReaderType.rdType'))
    rdDept = db.Column(db.Unicode(20))
    rdPhone = db.Column(db.Unicode(25))
    rdEmail = db.Column(db.Unicode(25))
    rdDateReg = db.Column(db.DateTime)
    rdPhoto = db.Column(db.String(100, 'Chinese_PRC_CI_AS'))
    rdStatus = db.Column(db.Unicode(2))
    rdBorrowQty = db.Column(db.Integer, server_default=db.FetchedValue())
    rdPwd = db.Column(db.Unicode(36), server_default=db.FetchedValue())
    rdAdminRoles = db.Column(db.SmallInteger, server_default=db.FetchedValue())

    Tb_ReaderType = db.relationship('TbReaderType', primaryjoin='TbReader.rdType == TbReaderType.rdType', backref='tb_readers')


class TbReaderType(db.Model):
    __tablename__ = 'Tb_ReaderType'

    rdType = db.Column(db.SmallInteger, primary_key=True)
    rdTypeName = db.Column(db.Unicode(20), nullable=False, unique=True)
    CanLendQty = db.Column(db.Integer)
    CanLendDay = db.Column(db.Integer)
    CanContinueTimes = db.Column(db.Integer)
    PunishRate = db.Column(db.Float(53))
    DateValid = db.Column(db.SmallInteger, nullable=False)