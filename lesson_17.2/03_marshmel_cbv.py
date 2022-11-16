from flask import request, jsonify, Flask
from flask_restx import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # настраиваем работу с бд
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # настраиваем работу с бд
db = SQLAlchemy(app)  # создаем соединение с бд

class Book(db.Model):
	__tablename__ = 'book'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	author = db.Column(db.String)
	year = db.Column(db.Integer)

class BookShema(Schema):
	id = fields.Int()
	name = fields.Str()
	author = fields.Str()
	year = fields.Int()

book_schema = BookShema
books_schema = BookShema(many=True)

api = Api(app)
book_ns = api.namespace('books')  # регистрируем наймспейс чере соответсвующий метод

b1 = Book(
		id = 1,
		name = "Harry Pottter",
		year = 2000,
		author = "Joan R"
		)
b2 = Book(
		id = 2,
		name = "La Comte",
		year = 1844,
		author = "Alexander D"
		)

app.app_context().push()  # создаем контекст приложения, иначе возникает ошибка
with db.session.begin():
	db.create_all()
	db.session.add_all([b1, b2])

# вьюшка для наймспеса со всеми книгами
@book_ns.route('/')
class BooksView(Resource):
	""" наследуемся от класса Resourse"""
	def get(self):
		all_books = db.session.query(Book).all()
		return books_schema.dump(all_books), 200

	def post(self):
		req_json = request.json  #получаем инфо из request в json формате
		new_book = Book(**req_json)
		with db.session.begin():
			db.session.add(new_book)
		return "", 201

# вьюшка для наймспеса с книгой по id
@book_ns.route('/<int:bid>')
class BookView(Resource):
	def get(self, bid:int):
		book = db.session.query(Book).filter(Book.id == bid).one()
		return book_schema.dump(book), 200


	def put(self, bid):
		book = db.session.query(Book).get(bid)
		req_json = request.json

		book.name = req_json.get("name")
		book.author = req_json.get("author")
		book.year = req_json.get("year")

		db.session.add(book)
		db.session.commit()
		return "", 204

	def delete(self, bid):
		book = db.session.query(Book).get(bid)
		db.session.delete(book)
		db.session.commit()
		return "", 204

app.run()