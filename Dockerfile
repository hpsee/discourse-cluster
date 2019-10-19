FROM ubuntu:18.04

# docker build -t vanessa/askci-cluster-gensim .

# Create user so we dont run with root (use standard joyvan)
ARG NB_USER=jovyan
ARG NB_UID=1000
ARG NB_GID=100

LABEL Maintainer @vsoch

ENV SHELL=/bin/bash \
    NB_USER=$NB_USER \
    NB_UID=$NB_UID \
    NB_GID=$NB_GID \
    NOTEBOOKS_DIR=/home/$NB_USER \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8 \
    HOME=${NOTEBOOKS_DIR} \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    cython3 \
    gcc \
    ipython3 \
    mc \
    nano \
    python3 \
    python3-dev \
    python3-numpy \
    python3-pip \
    python3-setuptools \
    python3-scipy \
    vim

WORKDIR ${NOTEBOOKS_DIR}

# From jupyter/docker-stacks/master/base-notebook/fix-permissions
ADD fix-permissions /usr/local/bin/fix-permissions

COPY cluster-analysis-gensim.ipynb /home/jovyan
COPY data/ /home/jovyan/

RUN pip3 install gensim && \
    pip3 install jupyter && \
    pip3 install prompt-toolkit==1.0.15 && \
    fix-permissions ${NOTEBOOKS_DIR} && \
    useradd -m -s /bin/bash -N -u $NB_UID $NB_USER && \
    chown $NB_USER:$NB_GID $NOTEBOOKS_DIR && \
    chmod g+w /etc/passwd && \
    fix-permissions $HOME && \
    fix-permissions "$(dirname $NOTEBOOKS_DIR)"

EXPOSE 8888

# Now change to the user to run the notebook
USER $NB_UID

CMD ["jupyter", "notebook", "--ip", "0.0.0.0", "--port", "8888"]
