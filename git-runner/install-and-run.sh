#!/bin/bash

info() {
  tput setaf 3
  echo "[INFO] $1"
  tput sgr0
}
success() {
  tput setaf 2
  echo $1
  tput sgr0
}
error() {
  tput setaf 1
  echo "[ERROR] $1"
  tput sgr0
}
warn() {
  tput setaf 208
  echo "[WARN] $1"
  tput sgr0
}

ensure_conda() {
  if ! command -v conda &> /dev/null
  then
      info "Conda not found, attempting to install"
      wget https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh
      bash Anaconda3-2021.11-Linux-x86_64.sh -b
      success "Anaconda installation finished"
  fi
}

if [ -v GIT_REPO_URL ]; then
  git clone $GIT_REPO_URL /app
else
  error "GIT_REPO_URL env variable must be set"
  exit 1
fi

cd /app || eval 'error "/app not found in container"; exit'

if [ -e setup.sh ]; then
  /bin/bash setup.sh
else
  if [ -e requirements.txt ]; then
    pip install -e .
  elif [ -e environment.yml ]; then
    ensure_conda
    eval "$(conda shell.bash hook)"
    conda activate base
    conda env create -f environment.yml
    conda activate "$(grep '^name: ' environment.yml | cut -c 7-)"
  fi
fi

info "Starting main script execution"
if [ ! -v PY_ENTRYPOINT ]; then
  info "Didn't find PY_ENTRYPOINT, executing main.py"
  PY_ENTRYPOINT='main.py'
fi
python "$PY_ENTRYPOINT"
info "Executed main script, exiting"
