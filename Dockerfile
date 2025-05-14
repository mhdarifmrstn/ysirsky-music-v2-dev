FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    file \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync

COPY . .

CMD ["uv", "run", "src/main.py"]
