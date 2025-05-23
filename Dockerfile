FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para Pillow y navegadores headless
RUN apt-get update && apt-get install -y \
    python3-dev \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    wget \
    gnupg \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Instalar Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Instalar ChromeDriver utilizando el método de Chrome for Testing
RUN apt-get update && apt-get install -y jq \
    && LATEST_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | jq -r '.channels.Stable.version') \
    && CHROMEDRIVER_URL=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | jq -r '.channels.Stable.downloads.chromedriver[] | select(.platform=="linux64").url') \
    && wget -q $CHROMEDRIVER_URL -O /tmp/chromedriver.zip \
    && mkdir -p /tmp/chromedriver \
    && unzip /tmp/chromedriver.zip -d /tmp/chromedriver \
    && mv /tmp/chromedriver/*/chromedriver /usr/local/bin/ \
    && rm -rf /tmp/chromedriver /tmp/chromedriver.zip \
    && chmod +x /usr/local/bin/chromedriver

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