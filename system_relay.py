from machine import ADC, Pin
import time
import json
from sustain_base import SustainBase
from umqtt.simple import MQTTClient

# Sustain_base
base = SustainBase('config/config.json')
config = base.get_config()

# Feuchtigkeitssensor
adc = ADC(Pin(32))
adc.atten(ADC.ATTN_11DB)
adc.width(ADC.WIDTH_12BIT)

# Config
RAW_DRY = int(config['HUMIDITY_MAX'])
RAW_WET = int(config['HUMIDITY_MIN'])
MQTT_THRESHOLD = 2000  # Schwellenwert für RAW
MAX_PERCENTAGE = 100
MIN_PERCENTAGE = 0

relay = Pin(19, Pin.OUT)

relay.off()  

# MQTT
mqtt = MQTTClient(
    'esp32_client',
    config['MQTT_HOST'],
    config['MQTT_PORT']
)

# Methode für eingehende MQTT-Nachrichten
def mqtt_callback(topic, msg):
    print(f"Nachricht empfangen auf {topic}: {msg}")
    # Relay für 1 Sekunde einschalten
    relay.on()  # oder relay.off() - je nach Modul-Logik
    time.sleep(1)
    relay.off()  # oder relay.on()

# MQTT connected
mqtt.set_callback(mqtt_callback)
mqtt.connect()
print('MQTT Connected')

# Topic abonnieren
mqtt.subscribe(config['MQTT_MAIN_TOPIC'] + 'moisture_alert')
print(f"Abonniert: {config['MQTT_MAIN_TOPIC'] + 'moisture_alert'}")

def get_moisture():
    raw = adc.read()
    moisture = int((RAW_DRY - raw) * 100 / (RAW_DRY - RAW_WET))

    if moisture < MIN_PERCENTAGE:
        moisture = MIN_PERCENTAGE
    if moisture > MAX_PERCENTAGE:
        moisture = MAX_PERCENTAGE

    return raw, moisture

# Nachricht senden
def send_mqtt_alert(raw_value):
    topic = config['MQTT_MAIN_TOPIC'] + 'moisture_alert'
    message = json.dumps({"raw": raw_value, "message": "Feuchtigkeits-Schwellenwert erreicht!"})
    mqtt.publish(topic, message, True)
    print(f"MQTT-Nachricht gesendet: {message}")

# Hauptschleife
while True:
    # MQTT-Nachrichten checken
    mqtt.check_msg()

    # Feuchtigkeit messen und senden
    raw, percent = get_moisture()
    print("RAW:", raw, "| Feuchtigkeit:", percent, "%")

    if raw <= MQTT_THRESHOLD:
        send_mqtt_alert(raw)
        
        relay.on()  
        time.sleep(1)
        relay.off()  

    time.sleep(1)