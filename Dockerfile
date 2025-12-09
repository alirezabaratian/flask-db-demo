FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["sh", "-c", "flask db upgrade && flask --debug run"]