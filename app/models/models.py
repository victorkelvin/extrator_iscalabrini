from app import db
from sqlalchemy import inspect

class TbEstados(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ddd = db.Column(db.String(2), nullable=False, unique=True)
    nome_estado = db.Column(db.String(250), nullable=False, unique=True)
    uf = db.Column(db.String(2), nullable=False, unique=True)
    matchstring = db.Column(db.String(100), nullable=False, unique=True)
    
    def __repr__(self):
        return f"TbEstados('{self.ddd}', '{self.nome_estado}', '{self.uf}','{self.matchstring}')"
    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs } # type: ignore
    



class TbDiarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_diario = db.Column(db.DATE, nullable=False)
    estado_diario =  db.Column(db.Integer, db.ForeignKey('tb_estados.id'), nullable=False)
    estado = db.relationship('TbEstados', backref='diarios', lazy=True)

    def __repr__(self):
        return f"TbDiarios('{self.data_diario}', '{self.estado}')"
    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs } # type: ignore
    
    
    
    
class TbLeads(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(250), nullable=False)
    cpf = db.Column(db.String(11))

    def __repr__(self):
        return f"TbLeads('{self.nome}', '{self.cpf}')"
    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }  # type: ignore


class TbPublicacoes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    diario_id = db.Column(db.Integer, db.ForeignKey('tb_diarios.id'))
    lead_id = db.Column(db.Integer, db.ForeignKey('tb_leads.id'))
    matricula = db.Column(db.String(20))
    orgao = db.Column(db.String(100))
    cargo = db.Column(db.String(100))
    valor = db.Column(db.Float)
    diario = db.relationship('TbDiarios', foreign_keys=[diario_id])
    lead = db.relationship('TbLeads', foreign_keys=[lead_id])

    def __repr__(self):
        return f"TbPublicacoes('{self.lead_id}','{self.valor}')"
    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }  # type: ignore
    
