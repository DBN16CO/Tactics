FROM python:2.7.15-alpine

RUN mkdir -p /opt/dbn/tactics
WORKDIR /opt/dbn/tactics

RUN apk update && \
    apk add --virtual build-deps gcc python-dev musl-dev && \
    apk add postgresql-dev libffi-dev

COPY ./Server/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY ./Server/Admin ./Admin
COPY ./Server/Communication ./Communication
COPY ./Server/Game ./Game
COPY ./Server/Maps ./Maps
COPY ./Server/Server ./Server
COPY ./Server/Static ./Static
COPY ./Server/User ./User
COPY ./Server/manage.py ./manage.py

EXPOSE 8000
ENV PYTHONPATH "${PYTHONPATH}:/opt/dbn/tactics"
CMD ["python", "manage.py", "runserver"]
