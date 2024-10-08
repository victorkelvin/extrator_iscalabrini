import os
from flask import request
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from .extratores import ba, mt
from io import BytesIO
import xlsxwriter
from app.models.models import TbEstados, TbDiarios, TbLeads, TbPublicacoes
from sqlalchemy import func
from app import db

UPLOAD_FOLDER = "uploads/"  # adjust the upload folder path as needed

def save_pdf():
    files = request.files.getlist("file")
    result_list = []
    if files:
        for file in files:
            filename = secure_filename(file.filename)  # type: ignore
            file_ext = os.path.splitext(filename)[1]
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if file_ext.lower() == ".pdf":
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)
                file.save(filepath)
                if not verify_pdf(filepath):
                    result_list.append({"filename": filename, "valido": False})
                    os.remove(filepath)
                else:
                    result_list.append({"filename": filename, "valido": True})
        return result_list
    else:
        return "No file uploaded!"


def verify_pdf(filepath: str):
    estados = TbEstados.query.all()
    try:
        with open(filepath, "rb") as pdf_file:
            reader = PdfReader(pdf_file)
            page = reader.pages[0].extract_text()
            lines = page.split("\n")
            pdf_text = "\n".join(lines[:10])
            for estado in estados:
                estado_dict = estado.toDict()
                if estado_dict['matchstring'].upper() in pdf_text.upper():  # case-insensitive match
                    if estado_dict['id'] == 5:
                        if not "SUPLEMENTO" in pdf_text:
                            ba.delay(str(filepath)) 
                            return True
                        else:
                            return False
                    
                    elif estado_dict['id'] == 13:
                        mt.delay(str(filepath))
                        return True
                    else:
                        return False
    

    except Exception as e:
        print(f"Error verifying PDF: {e}")
        return False
    


pesquisa_pub = None

def pesquisar(formValues):
    global pesquisa_pub
    """ Pesquisar as publicações no db de acordo com os filtros fornecidos  """
    estado_id = formValues['estado']
    nome = formValues['nome']
    cpf = formValues['cpf']
    data_publicacao_de = formValues['data-publicacao-de']
    data_publicacao_ate = formValues['data-publicacao-ate']
    valor_minimo = formValues['valor-minimo']
    valor_maximo = formValues['valor-maximo']

    query = db.session.query(
        func.to_char(TbDiarios.data_diario, 'DD/MM/YYYY').label('data_diario'),
        TbEstados.uf.label('uf'),
        TbLeads.nome.label('nome'),
        TbPublicacoes.processo.label('processo'),
        TbLeads.cpf.label('cpf'),
        TbPublicacoes.matricula.label('matricula'),
        TbPublicacoes.valor.label('valor'),
        TbPublicacoes.cargo.label('cargo'),
        TbPublicacoes.tempo_servico.label('tempo_servico')
    ).select_from(TbPublicacoes).join(
        TbDiarios, TbPublicacoes.diario_id == TbDiarios.id
    ).join(
        TbEstados, TbDiarios.estado_diario == TbEstados.id
    ).join(
        TbLeads, TbPublicacoes.lead_id == TbLeads.id
    )
    if estado_id:
        query = query.filter(TbEstados.id == estado_id)
    if nome:
        query = query.filter(TbLeads.nome.like('%' + nome + '%'))
    if cpf:
        query = query.filter(TbLeads.cpf == cpf)
    if data_publicacao_de:
        query = query.filter(TbDiarios.data_diario >= data_publicacao_de)
    if data_publicacao_ate:
        query = query.filter(TbDiarios.data_diario <= data_publicacao_ate)
    if valor_minimo:
        query = query.filter(TbPublicacoes.valor >= valor_minimo)
    if valor_maximo:
        query = query.filter(TbPublicacoes.valor <= valor_maximo)

    publicacoes = query.order_by(TbDiarios.data_diario.asc())
    pesquisa_pub = publicacoes
    return publicacoes

def send_publicacoes(form):
    return pesquisar(form)






def exportar_excel():
    # Assuming you have a function to retrieve the data from the database

    # Create an in-memory Excel file
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    # Write the data to the Excel file
    header = ['Data Diário', 'Estado', 'Nome', 'Processo', 'CPF', 'Matrícula', 'Valor']
    worksheet.write_row(0, 0, header)
    for i, publicacao in enumerate(pesquisa_pub): # type: ignore
        row = [
            publicacao.data_diario,
            publicacao.uf,
            publicacao.nome,
            publicacao.processo,
            publicacao.cpf,
            publicacao.matricula,
            publicacao.valor,
            publicacao.cargo,
            publicacao.tempo_servico
        ]
        worksheet.write_row(i + 1, 0, row)

    # Close the workbook and return the Excel file as a response
    workbook.close()
    output.seek(0)
    return output