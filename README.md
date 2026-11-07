# Mini RAG

this is a minimal implementation of the RAG model for Question Answering

## Requirements

- Python 3.8 or later


#### Install Python Using Miniconda

1) Download and install Miniconda from [here](https://docs.anaconda.com/free/miniconda/#quick-command-line-install).
2) create an new environment using the following command:
```bash
$ conda create -n mini-rag python=3.8
```
3) activate the environment
```bash
$ conda activate mini-rag
```


## Installation

### install the required package

```bash
$ pip install -r requirements.txt
```

### Setup the Environment Variables
```bash
$ cp .env.example .env
```

## Run Docker Compose Services

```bash
$ cd docker
$ cp .env.example .env
```
- update your `.env` with your credential

```bash
$ docker compose up -d
```

## Run the FastAPI Server
```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```