FROM python:3.9

RUN mkdir /Advs

WORKDIR /Advs

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

