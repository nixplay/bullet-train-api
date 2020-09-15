FROM python:3.7

RUN rm /var/lib/dpkg/info/format
RUN printf "1\n" > /var/lib/dpkg/info/format
RUN dpkg --configure -a
RUN  apt-get clean && apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pipenv

WORKDIR /usr/src
COPY src/ ./
COPY Pipfile* ./
RUN pipenv install --deploy
RUN pipenv run sfx-py-trace-bootstrap

EXPOSE 8000
