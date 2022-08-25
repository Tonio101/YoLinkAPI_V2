FROM python:3.9.2

RUN mkdir -p /usr/src/app
COPY ./src /usr/src/app
COPY requirements.txt /usr/src/app
WORKDIR /usr/src/app

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

# Local MQTT Server (Used by HomeAssistant)
#EXPOSE 1883
# YoLink MQTT Server (Consume YoLink Messages)
#EXPOSE 8003
# Influx DB (Send data to InfluxDB)
#EXPOSE 8086

CMD ["python3", "./yolinkv2homeassistant.py", "--config", "yolink_data.local.json", "--debug"]
