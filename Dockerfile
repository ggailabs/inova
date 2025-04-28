FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install mcp[cli] pandas

COPY server.py /app/server.py

EXPOSE 8000

CMD ["mcp", "dev", "server.py"]
