FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

ENV PYTHONBUFFERED=1

COPY . /api
WORKDIR /api

RUN pip install -r requirements.txt
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]