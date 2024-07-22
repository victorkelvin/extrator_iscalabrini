from PyPDF2 import PdfReader
import re
import os
from celery import shared_task
from app import db
from app.models.models import TbEstados, TbDiarios, TbLeads, TbPublicacoes


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


def extrator_default(pattern, text, matchgroup) -> str:
    match = re.search(pattern, text)
    if match:
        return match.group(matchgroup).strip()
    return None  # type: ignore


# Extrator BAHIA ---------------


def extrair_publicaoes(texto):
    nome_pattern = r"(?<=discriminado\(s\):)([^,]+)"
    matricula_pattern = r"matrícula +(\d+)"
    proventos_pattern = r"proventos (proporcionais|integrais) - R\$(([\d.]+),([\d]+))"

    nome = extrator_default(nome_pattern, texto, 1)
    nome = re.sub(r"^I ", "", nome)
    matricula = extrator_default(matricula_pattern, texto, 1)
    valor = extrator_default(proventos_pattern, texto, 2)
    valor = valor.replace(".", "").replace(",", ".")
    return {"nome": nome, "matricula": matricula, "valor": valor}


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


@shared_task()
def start_bahia(filepath):
    matchstring = "conceder Aposentadoria"
    fim_pagina = "CÓPIA - Consulte informação oficial em www.dool.egba.ba.gov.br"
    estado_db_id = 1
    print(f"INICIANDO EXTRATOR: {filepath}")
    try:
        with open(filepath, "rb") as file:
            reader = PdfReader(file)
            # publicacoes.append(extrair_data(reader.pages[0].extract_text()))
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
            for p, page in enumerate(reader.pages):
                texto = page.extract_text()
                lines = texto.split("\n")
                for i, line in enumerate(lines):
                    if matchstring in line:
                        end = min(len(lines), i + 10)
                        context = lines[i:end]
                        if (
                            context[-1] == fim_pagina
                        ):  ### irá verificar se o texto esta no fim da página e irá realizar a leitura da proxima pagina para extrair o restante do texto
                            maxline = 10 - len(context)
                            prox_pagina = (
                                reader.pages[p + 1]
                                .extract_text()
                                .split("\n")[2:maxline]
                            )
                            context.extend(prox_pagina)

                        context = " ".join(context)
                        context = context.replace("\n", "")
                        publicacao = extrair_publicaoes(context)
                        novo_lead = TbLeads(nome=publicacao["nome"])  # type: ignore
                        db.session.add(novo_lead)
                        db.session.flush()
                        nova_publicacao = TbPublicacoes(diario_id=doe_id, lead_id=novo_lead.id, matricula=publicacao["matricula"], valor=publicacao["valor"])  # type: ignore
                        db.session.add(nova_publicacao)

    except Exception as e:
        print(f"Error processing file: {e}")
        return False
    db.session.commit()
    os.remove(filepath)
    return True
