FROM python:3.12-slim
WORKDIR /repo
RUN pip install --no-cache-dir openai
COPY . .
