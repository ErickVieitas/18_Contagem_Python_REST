from flask import Flask
from flask_restful import reqparse, Api, Resource, fields

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:adm@localhost/postgres?options=-csearch_path=atividade2'

db = SQLAlchemy(app)
marshmallow = Marshmallow(app)


class FolhaPagamentoDataBase(db.Model):
    __tablename__ = "Folha de pagamento"
    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    nome = db.Column(db.String(256), unique=True, nullable=False)
    horastrabalhadas = db.Column(db.Integer, nullable=False)
    valordahora = db.Column(db.Numeric(precision=10, scale=2), nullable=False)

    def __init__(self, cpf, nome, horastrabalhadas, valordahora):
        self.cpf = cpf
        self.nome = nome
        self.horastrabalhadas = horastrabalhadas
        self.valordahora = valordahora

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return f"{self.id, self.cpf, self.nome, self.horastrabalhadas, self.valordahora}"


class FolhaPagamentoseSchema(marshmallow.SQLAlchemyAutoSchema):
    class Meta:
        model = FolhaPagamentoDataBase

    sqla_session = db.session
    id = fields.Number()  # dump_only=True)
    cpf = fields.Integer(required=True)
    nome = fields.String(required=True)
    horastrabalhadas = fields.Integer(required=True)
    valordahora = fields.Float(required=True)


api = Api(app)

# Parse dos dados enviados na requisição no formato JSON:
parser = reqparse.RequestParser()
parser.add_argument('id', type=int, help='identificador do produto')
parser.add_argument('cpf', type=int, help='cpf')
parser.add_argument('nome', type=str, help='nome do produto')
parser.add_argument('horastrabalhadas', type=int, help='horastrabalhadas')
parser.add_argument('valordahora', type=float, help='preço do produto')

# Produto:
# 1) Apresenta um único produto.
# 2) Remove um único produto.
# 3) Atualiza (substitui) um produto.


class Pagamento(Resource):
    def get(self, id):
        folhapagamento = FolhaPagamentoDataBase.query.get(id)
        folhapagamento_schema = FolhaPagamentoseSchema()
        resp = folhapagamento_schema.dump(folhapagamento)
        return {"Folha de pagamento": resp}, 200  # 200: Ok

    def delete(self, id):
        folhapagamento = FolhaPagamentoDataBase.query.get(id)
        db.session.delete(folhapagamento)
        db.session.commit()
        return '', 204  # 204: No Content

    def put(self, id):
        folhapagamento_json = parser.parse_args()
        folhapagamento = FolhaPagamentoDataBase.query.get(id)

        if folhapagamento_json.get('cpf'):
            folhapagamento.cpf = folhapagamento_json.cpf

        if folhapagamento_json.get('nome'):
            folhapagamento.nome = folhapagamento_json.nome

        if folhapagamento_json.get('horastrabalhadas'):
            folhapagamento.horastrabalhadas = folhapagamento_json.horastrabalhadas

        if folhapagamento_json.get('valordahora'):
            folhapagamento.valordahora = folhapagamento_json.valordahora

        db.session.add(folhapagamento)
        db.session.commit()

        folhapagamento_schema = FolhaPagamentoseSchema(
            only=['id', 'nome', 'cpf', 'horastrabalhadas', 'valordahora'])
        resp = folhapagamento_schema.dump(folhapagamento)
        return {"Folha de pagamento": resp}, 200  # 200: OK

# ListaProduto:
# 1) Apresenta a lista de produtos.
# 2) Insere um novo produto.


class ListaPagamento(Resource):
    def get(self):
        folhapagamento = FolhaPagamentoDataBase.query.all()
        # Converter objto Python para JSON.
        folhapagamento_schema = FolhaPagamentoseSchema(many=True)
        resp = folhapagamento_schema.dump(folhapagamento)
        return {"Folha de pagamento": resp}, 200  # 200: Ok

    def post(self):
        folhapagamento_json = parser.parse_args()
        folhapagamento_schema = FolhaPagamentoseSchema()
        folhapagamento = folhapagamento_schema.load(folhapagamento_json)
        folhaPagamentoDataBase = FolhaPagamentoDataBase(
            folhapagamento['cpf'], folhapagamento['nome'], folhapagamento['horastrabalhadas'], folhapagamento['valordahora'])
        resp = folhapagamento_schema.dump(folhaPagamentoDataBase.create())
        return {"Folha de pagamento": resp}, 201  # 201: Created


# Roteamento de recursos:
api.add_resource(Pagamento, '/folhapagamento/<id>')
api.add_resource(ListaPagamento, '/folhapagamento')
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
