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


# # Extrator BAHIA ---------------
def extrair_data(page):
    lines = page.split("\n")
    head_text = "\n".join(lines[:10])
    pattern = r"(\d+) DE ([A-Z]+) DE (\d+)"
    match = re.search(pattern, head_text)
    if match:
        dia = match.group(1)
        month = match.group(2)
        ano = match.group(3)

    mes = mes_map[month]
    data = f"{ano}-{mes}-{dia}"
    return data


@shared_task
def bahia(filepath):
    pattern = r"([\w\s\u0080-\uFFFF]+), proc. (\d+\.\d+\.\d+\.\d+-\d+),.*?(\d{8}),.*?\$?(\d+\.?\d+,\d+)" # Quase 24h pra fazer 1 linha de código --', pqp!
    regex = re.compile(pattern, re.DOTALL)
    estado_db_id = 5
    print(f"INICIANDO EXTRATOR: {filepath}")
    try:
        with open(filepath, "rb") as file:
            reader = PdfReader(filepath)
            data_doe = extrair_data(reader.pages[0].extract_text())
            doe_exist = TbDiarios.query.filter_by(
                data_diario=data_doe, estado_diario=estado_db_id
            ).first()

            if doe_exist:
                file.close()
                os.remove(filepath)
                return "DOE já processado"

            novo_doe = TbDiarios(data_diario=data_doe, estado_diario=estado_db_id)  # type: ignore
            db.session.add(novo_doe)
            db.session.flush()
            doe_id = novo_doe.id
            db.session.commit()

            for page in reader.pages:
                for match in regex.finditer(page.extract_text()):
                    nome = match.group(1).rsplit("\n", 1)[
                        -1
                    ]  # remove leading whitespace and newline
                    nome = nome.split()
                    nome = " ".join(nome[1:])
                    processo = match.group(2)
                    matricula = match.group(3)
                    valor = match.group(4)
                    valor = valor.replace(".", "").replace(",", ".")
                    novo_lead = TbLeads(nome=nome)  # type: ignore
                    db.session.add(novo_lead)
                    db.session.flush()
                    nova_publicacao = TbPublicacoes(diario_id=doe_id, lead_id=novo_lead.id, processo=processo, matricula=matricula, valor=valor)  # type: ignore
                    db.session.add(nova_publicacao)

    except Exception as e:
        print(f"ERRO: {e}")
        return
    db.session.commit()
    os.remove(filepath)
    return True
