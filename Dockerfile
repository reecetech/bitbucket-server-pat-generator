FROM python:3.10-slim

ARG PIP_NO_CACHE_DIR=1
RUN pip install -U pip pipenv

WORKDIR /tmp
COPY Pipfile* /tmp/
RUN pipenv install --system --ignore-pipfile

WORKDIR /app
COPY pat_helper.py entrypoint_*.sh /app/

ENTRYPOINT ["/app/entrypoint_main.sh"]
