FROM python:3.9.2

RUN mkdir -p /app
COPY ./src /app
COPY requirements.txt /app

# RUN python3 -m pip install --upgrade pip
RUN cd /app \
    && python3 -m pip install -r requirements.txt

# Local MQTT Server (Used by HomeAssistant)
#EXPOSE 1883
# YoLink MQTT Server (Consume YoLink Messages)
#EXPOSE 8003
# Influx DB (Send data to InfluxDB)
#EXPOSE 8086

WORKDIR /app
CMD ["python3", "main.py", "--config", "yolink_config.json", "--debug"]
