FROM ctfd/ctfd:3.6.1

USER root
# Instalar ping y curl (útil en diagnóstico)
RUN apt-get update && apt-get install -y curl iputils-ping

# Instalamos el plugin CTFd-Whale
RUN cd /opt/CTFd/CTFd/plugins \
    && git clone -b master https://github.com/frankli0324/ctfd-whale.git whale

# Instalar dependencias requeridas del plugin
RUN pip install -r /opt/CTFd/CTFd/plugins/whale/requirements.txt

# Limpieza
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

USER 1001
