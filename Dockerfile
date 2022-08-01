FROM python:3.9-buster
RUN mkdir /app
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8089

CMD ["python3", "main.py"]