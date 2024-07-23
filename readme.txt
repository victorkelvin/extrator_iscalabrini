Install .venv
pip -m venv .venv

#Install requirements
pip install -r requirements.txt

#install postgresql
criar db e usuario
create database iscalabrini_db
create user <usuario> with encrypted password '<senha>';
grant all privileges on database iscalabrini_db to <usuario>;
inserir dados na tb_estados


#run rabbitmq in docker
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.13-management

enable wfastcgi:
wfastcgi-enable





('71', 'bahia', 'BA','bahia
')


# Instalar dependencias necessários:
 - github
 - PostgreSQL
 - Docker
 - RabbitMQ


#Instalar PostgreSQL, criar database e usuário

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


#executar scripts

1_atualizar_db.bat
2_atualizar.bat
3_iniciar_worker.bat
4_iniciar_webserver.bat


