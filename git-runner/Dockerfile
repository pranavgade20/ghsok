FROM pytorchlightning/pytorch_lightning:base-cuda-py3.9-torch1.10

COPY install-and-run.sh /
COPY setup.sh /

RUN bash /setup.sh

ENTRYPOINT bash /install-and-run.sh