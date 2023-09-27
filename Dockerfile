# Set base image (this loads the Debian Linux operating system)
FROM python:3.10.4-buster
ENV PYTHONUNBUFFERED True

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV APP_HOME /root
WORKDIR $APP_HOME
COPY /app $APP_HOME/app
COPY scratch/deaths_data.parquet scratch/deaths_data.parquet

EXPOSE 8080
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8080"]
