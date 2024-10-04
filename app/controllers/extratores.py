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


def extrair_data(page):
    pattern = r"(\d+|1º) DE ([A-ZÇ]+) DE (\d{4})"
    match = re.search(pattern, page.upper())
    if match:
        dia = match.group(1)
        month = match.group(2)
        ano = match.group(3)
        if dia == '1º':
            dia = '01'
    mes = mes_map[month]
    data = f"{ano}-{mes}-{dia}"
    return data


# # Extrator BAHIA ---------------
@shared_task
def ba(filepath):
    pattern = r"([a-zA-Z\s\u0080-\uFFFF]+), proc. (\d+\.\d+\.\d+\.?\d+-\d+|\d+).*?(\d{8}|\d{2}\.?\d{3}\.?\d{3}-?\d{1}),.*?\$?(\d+\.?\d+,\d+)" # Quase 24h pra fazer 1 linha de código --', pqp!
    regex = re.compile(pattern, re.DOTALL)
    retificacoes = ('RETIRATIFICAR', 'RETIFICAÇÃO', 'RETIFICAR')

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
            blocks = text.split('/>')
            for block in blocks:
                if not any(cond in block for cond in retificacoes):    
                    for match in regex.finditer(block):
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
@shared_task
def mt(filepath):
    estado_db_id = 13
    print(f"INICIANDO EXTRATOR MATO GROSSO: {filepath}")

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

        for page in reader.pages:
            lines = page.extract_text().split('\n')
            for j, line in enumerate(lines):
                if 'Aposentar' in line:
                    context = ''.join(lines[j-2:j+8]).replace('\n', '')
                    pattern =  r'Processo.*?(\d{4}.\d{1}.\d{5}|\d{10}).*?Sr.*?\.(.*?),.*?CPF.*?º (.*?),.*?cargo de (.*?),.*?contando com (\d+)'
                elif 'mediante Reserva Remunerada' in line:
                    context = ''.join(lines[j-2:j+8]).replace('\n', '')
                    pattern =  r'Processo.*?(\d{4}.\d{1}.\d{5}|\d{10}).*?Sr.*?\.(.*?),.*?CPF.*?º (.*?), (.*?),.*?total de (\d+)'
                else:
                    continue
                regex = re.compile(pattern, re.DOTALL)
                for match in regex.finditer(context):
                    # print(f'{context}\n\n')
                    print(f'{match.group(1)} | {match.group(2)} | {match.group(3)} | {match.group(4)} | {match.group(5)}') # type
                    processo = match.group(1)
                    nome = match.group(2)
                    cpf = match.group(3)
                    cargo = match.group(4)
                    tempo_servico = match.group(5)
                    publicao = TbPublicacoes.query.filter_by(diario_id=doe_id, processo = processo).first()
                    if not publicao:
                        novo_lead = TbLeads(nome=nome, cpf=cpf)  # type: ignore
                        db.session.add(novo_lead)
                        db.session.flush()
                        nova_publicacao = TbPublicacoes(diario_id=doe_id, lead_id=novo_lead.id, processo=processo, cargo=cargo, tempo_servico=tempo_servico)  # type: ignore
                        db.session.add(nova_publicacao)

    except Exception as e:
        print(f'ERRO: {e}')
        return False
    
    db.session.commit()
    os.remove(filepath)
    return True