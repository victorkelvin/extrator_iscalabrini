# Instalar dependencias necessários:
 - github
 - PostgreSQL
 - Docker
 - RabbitMQ


#Instalar PostgreSQL, criar database e usuário
##Adicionar váriável de ambiente para psql
create database iscalabrini_db
create user <usuario> with encrypted password '<senha>';
grant all privileges on database iscalabrini_db to <usuario>;


# Executar rabbitmq no docker:
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.13-management

# Criar pasta para sistema

# Baixar repositorio do github na pasta
git clone https://github.com/victorkelvin/extrator_iscalabrini .

#Criar venv na pasta
python -m venv .venv

colar arquivo config.txt e variaveis.py no diretorio

#executar scripts

1_atualizar_server.bat
2_atualizar_db.bat
3_iniciar_worker.bat
4_iniciar_webserver.bat


