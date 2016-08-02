FROM            python:2.7-alpine

ENV             LANG=en_US.UTF-8
ENV             PYTHONUNBUFFERED=True
ENV             PYTHONIOENCODING=utf-8
ENV             FLASK_APP=tinkrbell.wsgi
ENV             FLASK_DEBUG=1

RUN             mkdir -p /usr/src/app
WORKDIR         /usr/src/app

COPY            requirements.txt /usr/src/app/
# RUN             apk --no-cache add --virtual .builddeps
RUN             pip install --no-cache-dir -r requirements.txt
# RUN             apk del .builddeps
COPY            . /usr/src/app

CMD             ["python", "-m", "flask", "run", "-h", "0.0.0.0", "-p", "8000"]
