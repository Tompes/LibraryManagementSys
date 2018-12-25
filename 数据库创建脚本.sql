drop database BooksDatabase
go
create database BooksDatabase 
go
use BooksDatabase
go

create table Tb_ReaderType (
	typeID int primary key  identity(1,1),
	rdType SmallInt unique not null ,
	rdTypeName Nvarchar(20) unique not null,
	CanLendQty Int ,
	CanLendDay Int ,
	CanContinueTimes Int ,
	PunishRate Float,
	DateValid SmallInt not null,
)
go

create table Tb_Reader (
	rdID		Int identity(1800001,1) primary key,
	rdName		nvarchar(20),
	rdSex		nchar(1),
	rdType		SmallInt ,
	rdDept		nvarchar (20),
	rdPhone		nvarchar(25),
	rdEmail		nvarchar(25),
	rdDateReg	datetime,
	rdPhoto		TEXT,
	rdStatus	nchar(2),
	rdBorrowQty	Int default 0,
	rdPwd		nvarchar (36) default '123',
	rdAdminRoles	SmallInt default 0
	foreign key (rdType) references Tb_ReaderType(rdType)
)
go

create table Tb_Book (
	bkID		Int  identity(10001,1) primary key,
	bkCode		Nvarchar (20),
	bkName		Nvarchar(50),
	bkAuthor	Nvarchar(30),
	bkPress		Nvarchar(50),
	bkDatePress	datetime,
	bkISBN		Nvarchar (15),
	bkCatalog	Nvarchar(30),
	bkLanguage	SmallInt,
	bkPages		Int,
	bkPrice		Money,
	bkDateIn	DateTime,
	bkBrief		Text,
	bkCover		Text,
	bkStatus	NChar(2),
)
go

create table Tb_Borrow(
	BorrowID		Numeric(12,0) identity(1,1) primary key,
	rdID			Int,
	bkID			Int,
	ldContinueTimes	Int default 0,
	ldDateOut		DateTime,
	ldDateRetPlan	DateTime,
	ldDateRetAct	DateTime,
	ldOverDay		Int,
	ldOverMoney		Money,
	ldPunishMoney	Money,
	lsHasReturn		Bit default 0,
	OperatorLend	Nvarchar(20),
	OperatorRet		Nvarchar(20),
	foreign key(rdID) references Tb_Reader(rdID),
	foreign key(bkID) references Tb_Book(bkID)
)
go

--插入ReaderType
insert into [TB_ReaderType]	values(10,'教师',12,60,2,0.05,0);
insert into [TB_ReaderType]	values(20,'本科生',8,30,1,0.05,4);
insert into [TB_ReaderType]	values(21,'专科生',8,30,1,0.05,3);
insert into [TB_ReaderType]	values(30,'硕士研究生',8,30,1,0.05,3);
insert into [TB_ReaderType]	values(31,'博士研究生',8,30,1,0.05,4);

--
select * from Tb_Book
