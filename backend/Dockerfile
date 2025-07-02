FROM python:3.12

WORKDIR /app

COPY requirements.txt .

COPY ingredients.csv .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .
CMD ["python", "manage.py", "collectstatic"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.asgi:application"]