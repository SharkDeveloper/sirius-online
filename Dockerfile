# Development stage (легковесный образ)
FROM python:3.11-slim-bullseye as development

# Рабочая директория
WORKDIR /sirius

# Установка зависимостей Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY app /sirius/app
COPY root /sirius/root
COPY manage.py /sirius/manage.py
COPY docker-entrypoint.sh /sirius/docker-entrypoint.sh

# Настройки окружения
ENV PYTHONUNBUFFERED 1
RUN chmod +x /sirius/docker-entrypoint.sh

# Точка входа
ENTRYPOINT ["/sirius/docker-entrypoint.sh"]

# Запуск приложения
CMD ["gunicorn", "-w", "4", "-k", "root.gunicorn_conf.UvicornWorker", "--bind", "0.0.0.0:8021", "root.asgi:application", "--log-level", "debug"]
################################################################
# Этап отладки (полноценный образ для диагностики)
FROM ubuntu:22.04 as debug

# Установка базовых инструментов и Python
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    nano \
    vim \
    curl \
    net-tools \
    iputils-ping \
    dnsutils \
    tcpdump \
    strace \
    lsof \
    gdb \
    && rm -rf /var/lib/apt/lists/*

# Создание симлинка для python
RUN ln -s /usr/bin/python3.11 /usr/local/bin/python

# Рабочая директория
WORKDIR /sirius

COPY . .

# Установка зависимостей Python
RUN python -m pip install --no-cache-dir -r /sirius/requirements.txt 
RUN python -m pip install debugpy
# Настройка переменных окружения
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/sirius"

# Команда запуска приложения
CMD [ "python" , "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "root.asgi:application", "--host", "0.0.0.0", "--port", "8021", "--ws-ping-interval", "3600", "--ws-ping-timeout", "3600", "--log-level", "debug"]
