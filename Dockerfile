FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip --index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install alembic --index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir \
    --default-timeout=100 \
    -r requirements.txt \
    --index-url https://pypi.tuna.tsinghua.edu.cn/simple
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]