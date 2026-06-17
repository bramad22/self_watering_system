import json
import network
import time

class SustainBase:
        
    def __init__(self, config_file : str):
        with open(config_file) as file:
            self.config = json.load(file)
        self.connect_wifi()            
        pass
    
    def get_config(self):
        return self.config

    def connect_wifi(self):
        ssid, password = self.config.get("WIFI_SSID"), self.config.get("WIFI_PASSWD")
        if not ssid or not password:
            return False

        

        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)  # WLAN explizit aktivieren

        # Verbindung zurücksetzen, falls bereits aktiv
        if sta_if.isconnected():
            return True

        print(f"Verbinde mit {ssid}...")
        sta_if.connect(ssid, password)

        for _ in range(20):
            if sta_if.isconnected():
                print("Verbunden! IP:", sta_if.ifconfig()[0])
                return True
            time.sleep(1)

        return False
