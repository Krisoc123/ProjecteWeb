FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para Pillow
RUN apt-get update && apt-get install -y \
    python3-dev \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Verificar que Pillow se instala correctamente
RUN pip install --no-cache-dir Pillow && \
    python -c "from PIL import Image; print('Pillow instalado correctamente')"

# Luego instalar Poetry
RUN pip install poetry

# Copiar los archivos de configuración
COPY pyproject.toml poetry.lock ./

# Configurar Poetry sin entornos virtuales
RUN poetry config virtualenvs.create false

# Instalar dependencias del proyecto
RUN poetry install --no-interaction --no-ansi --no-root

# Copiar el resto del código
COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]