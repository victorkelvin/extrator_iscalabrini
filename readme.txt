Install .venv
pip -m venv .venv

#Install requirements
pip install -r requirements.txt

#install postgresql

#run rabbitmq in docker
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.13-management

enable wfastcgi:
wfastcgi-enable

