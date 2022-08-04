FROM python:3.9 as pull-base

ENV SCRIPT_DIR=/script
RUN mkdir -p ${SCRIPT_DIR}}/config
WORKDIR ${SCRIPT_DIR}}

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./rcpull .

RUN mkdir /wd
WORKDIR /wd

ENTRYPOINT [ "python3", "/script/redcap_pull.py"]

# NOTE: to run a shell in the container, override the entrypoint at the commandline:
# docker run -it --entrypoint /bin/bash naccdata/rcpull