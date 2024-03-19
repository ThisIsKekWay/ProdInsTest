FROM python:3.11

RUN mkdir /Advs

WORKDIR /Advs

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["gunicorn", "app.main:app", "workers","4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8000"]

COPY . .

