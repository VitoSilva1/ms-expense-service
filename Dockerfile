# Imagen base ligera de Python
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Instalamos dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código
COPY app ./app

# Puerto expuesto (opcional, para documentación)
EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

