# Dockerfile

FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

# Collect static files if you use them
# RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "credit_system.wsgi:application", "--bind", "0.0.0.0:8000"]
