FROM python:3.9-bullseye

WORKDIR /src

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src .
COPY ./res ../res

CMD bash -c "python -m main"
