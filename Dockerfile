FROM python:3.6 as build
RUN apt-get update && apt-get install -y \
    pandoc \
 && rm -rf /var/lib/apt/lists/*

COPY /requirements_dev.txt /requirements_dev.txt
RUN pip install -r requirements_dev.txt

COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY Makefile /cfgcaddy/Makefile

COPY ./cfgcaddy /cfgcaddy/cfgcaddy
COPY ./setup.py /cfgcaddy/setup.py

FROM build as dist
WORKDIR /cfgcaddy
COPY README.md /cfgcaddy/README.md
RUN make local-build-dist

FROM build as check
RUN pip install --editable /cfgcaddy
