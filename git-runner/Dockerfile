FROM python

COPY install-and-run.sh /
COPY setup.sh /

RUN bash /setup.sh

ENTRYPOINT /install-and-run.sh