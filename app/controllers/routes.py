from flask import render_template, request, send_file
import os
from .doe_controller import save_pdf, exportar_excel, pesquisar
from app import flask_app
from app.models.models import TbEstados

UPLOAD_FOLDER = os.path.join(flask_app.root_path, "uploads")


@flask_app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if request.form["button"] == "search":
            return search()
        elif request.form["button"] == "upload":
            return render_template("upload.html")
    return render_template("index.html")



@flask_app.route("/search")
def search():
    lista_estados = TbEstados.query.all()

    return render_template("search.html", estados=lista_estados)


@flask_app.route("/search_result", methods=["post"])  # type: ignore
def search_result():
    if request.method == "POST":

        lista_estados = TbEstados.query.all()

        form = request.form
        publicacoes = pesquisar(form)
        return render_template('search.html', publicacoes=publicacoes, estados=lista_estados)



@flask_app.route("/upload", methods=["post"])  # type: ignore
def upload_doe():
    results = save_pdf()
    
    return render_template('upload_result.html', results=results)


@flask_app.route('/export_to_xlsx', methods=["post"])
def export_to_xlsx():
    publicacoes = exportar_excel(request.form)
    return send_file(publicacoes, as_attachment=True, download_name='publicacoes.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
