Install .venv
pip -m venv .venv

#Install requirements
pip install -r requirements.txt

#install postgresql
criar db e usuario
create database iscalabrini_db
create user <usuario> with encrypted password '<senha>';
grant all privileges on database iscalabrini_db to <usuario>;



#run rabbitmq in docker
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.13-management

enable wfastcgi:
wfastcgi-enable

