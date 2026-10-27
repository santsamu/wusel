FROM python:3.12-slim
ARG BUILD_VERSION=0.14.2
ARG BUILD_ARCH
LABEL io.hass.version="${BUILD_VERSION}" io.hass.type="app" io.hass.arch="aarch64|amd64"
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 WUSEL_DATA=/data
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py weather.py server.py ./
COPY static ./static
EXPOSE 8099
CMD ["python", "app.py"]
