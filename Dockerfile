FROM python:3.8-slim-bookworm

ARG PORT=8501

ENV PYTHONUNBUFFERED=1 \
    PORT=$PORT

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE $PORT

CMD ["sh", "-c", "python -m streamlit run Home.py --server.port=$PORT --server.address=0.0.0.0"]
