from PyPDF2 import PdfReader
import re
import os
from celery import shared_task
from app import db
from app.models.models import TbDiarios, TbLeads, TbPublicacoes


mes_map = {
    "JANEIRO": "01",
    "FEVEREIRO": "02",
    "MARÇO": "03",
    "ABRIL": "04",
    "MAIO": "05",
    "JUNHO": "06",
    "JULHO": "07",
    "AGOSTO": "08",
    "SETEMBRO": "09",
    "OUTUBRO": "10",
    "NOVEMBRO": "11",
    "DEZEMBRO": "12",
}


# def extrator_default(pattern, text, matchgroup) -> str:
#     match = re.search(pattern, text)
#     if match:
#         return match.group(matchgroup).strip()
#     return None  # type: ignore

def extrair_data(page):
    pattern = r"(\d{1,2}) DE ([A-ZÇ]+) DE (\d{4})"
    match = re.search(pattern, page.upper())
    if match:
        dia = match.group(1)
        month = match.group(2)
        ano = match.group(3)

    mes = mes_map[month]
    data = f"{ano}-{mes}-{dia}"
    return data

# # Extrator BAHIA ---------------


@shared_task
def ba(filepath):
    pattern = r"([a-zA-Z\s\u0080-\uFFFF]+), proc. (\d+\.\d+\.\d+\.?\d+-\d+|\d+).*?(\d{8}|\d{2}\.?\d{3}\.?\d{3}-?\d{1}),.*?\$?(\d+\.?\d+,\d+)" # Quase 24h pra fazer 1 linha de código --', pqp!
    regex = re.compile(pattern, re.DOTALL)
    estado_db_id = 5
    print(f"INICIANDO EXTRATOR BAHIA: {filepath}")
    try:
        reader = PdfReader(filepath)
        data_page = reader.pages[0].extract_text().split("\n")
        data_doe = extrair_data('\n'.join(data_page[:3]))
        print(f"DATA DOE: {data_doe}")
        diarios = TbDiarios.query.filter_by(
            data_diario=data_doe, estado_diario=estado_db_id
        ).first()

        if diarios:
            doe_id = diarios.toDict()['id']
        else:
            novo_doe = TbDiarios(data_diario=data_doe, estado_diario=estado_db_id)  # type: ignore
            db.session.add(novo_doe)
            db.session.flush()
            doe_id = novo_doe.id
            db.session.commit()
        for i, page in enumerate(reader.pages):
            if i + 1 == len(reader.pages):
                text = page.extract_text()
            else:
                text = page.extract_text() + reader.pages[i+1].extract_text()

            for match in regex.finditer(text):
                nome = match.group(1).rsplit("\n", 1)[-1]  # remove leading whitespace and newline
                nome = re.sub(r'^\s?[IVX]*\s', '', nome)
                processo = match.group(2)
                matricula = match.group(3)
                valor = match.group(4)
                valor = valor.replace(".", "").replace(",", ".")
                publicao = TbPublicacoes.query.filter_by(diario_id=doe_id, processo = processo).first()
                if not publicao:
                    novo_lead = TbLeads(nome=nome)  # type: ignore
                    db.session.add(novo_lead)
                    db.session.flush()
                    nova_publicacao = TbPublicacoes(diario_id=doe_id, lead_id=novo_lead.id, processo=processo, matricula=matricula, valor=valor)  # type: ignore
                    db.session.add(nova_publicacao)

    except Exception as e:
        print(f"ERRO: {e}")
        return False
    db.session.commit()
    os.remove(filepath)
    return True


# # Extrator MATO GROSSO ---------------

# def mt(filepath):
#     pattern  = r'Processo.*(\d{4}\.?\d{1}\.?\d+),.*Aposenta'
#     regex = re.compile(pattern, re.DOTALL)
#     estado_db_id = 13
#     print(f"INICIANDO EXTRATOR BAHIA: {filepath}")
#     try:
#         reader = PdfReader(filepath)
#         data_doe = extrair_data(reader.pages[0].extract_text())
#         diarios = TbDiarios.query.filter_by(
#             data_diario=data_doe, estado_diario=estado_db_id
#         ).first()
        
#         if diarios:
#             doe_id = diarios.toDict()['id']
#         else:
#             novo_doe = TbDiarios(data_diario=data_doe, estado_diario=estado_db_id)  # type: ignore
#             db.session.add(novo_doe)
#             db.session.flush()
#             doe_id = novo_doe.id
#             db.session.commit()
#         for page in reader.pages:
#             for match in regex.finditer(page.extract_text()):
#                 print(match.group(0))
#     except Exception as e:
#         print(f"ERRO: {e}")
#         return False
    