FROM python:3.10-slim

ARG PIP_NO_CACHE_DIR=1

RUN pip install -U pip pipenv

RUN useradd -m -U -u 500 -r -s /usr/sbin/nologin appuser \
 && mkdir /app \
 && chown -R appuser:appuser /app

COPY Pipfile* /tmp/
WORKDIR /tmp
RUN pipenv install --system --ignore-pipfile

USER appuser
WORKDIR /app

COPY pat_helper.py /app/

ENTRYPOINT ["python", "/app/pat_helper.py"]
