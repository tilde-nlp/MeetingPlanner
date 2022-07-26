FROM python:3.8-buster

WORKDIR /app
RUN apt-get update && \
    apt-get install -y apt-transport-https && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install msodbcsql17 unixodbc-dev -y

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app

RUN chmod +x ./runmp.sh

EXPOSE 5000
ENTRYPOINT ["./runmp.sh"]
