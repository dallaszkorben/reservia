FROM armdocker.rnd.ericsson.se/dockerhub-ericsson-remote/python:3.8-bullseye

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

EXPOSE 5000

CMD ["python", "app.py"]