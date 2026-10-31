FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements .
RUN pip install --no-cache-dir -r requirements
COPY . .
RUN useradd --create-home appuser
USER appuser
EXPOSE 8001
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "--workers", "1", "wsgi:app"]