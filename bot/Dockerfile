FROM python:3.7

ENV PYTHONBUFFERED=1

COPY . /bot
WORKDIR /bot

RUN pip install -r requirements.txt
CMD ["python", "./main.py"]




