FROM python:3

LABEL Name=ClemBot Version=0.1.0

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./bot/__main__.py" ]