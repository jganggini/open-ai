FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y nginx openssl \
 && rm -rf /var/lib/apt/lists/*

# Crear directorio SSL
RUN mkdir -p /etc/nginx/ssl

# Copiar configuración
COPY default.conf /etc/nginx/sites-available/default

# Generar certificado autofirmado (válido 365 días)
RUN openssl req -x509 -nodes -days 365 \
    -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key \
    -out /etc/nginx/ssl/nginx.crt \
    -subj "/C=ES/ST=Madrid/L=Madrid/O=MiEmpresa/CN=localhost"

CMD ["nginx", "-g", "daemon off;"]
