import network
import machine


# WIFI_SSID = 'Familia Ferrari PISO 1'
# WIFI_PASSWORD = 'Familiaferrari11'
# WIFI_SSID = 'Casa Pablo 2,4G'
# WIFI_PASSWORD = '12345678'
# WIFI_SSID = 'wifi-campus'
# WIFI_PASSWORD = 'uandes2200'
# WIFI_SSID = 'Time Capsule CCN'
# WIFI_PASSWORD = 'cctmcctm6'
# WIFI_SSID = 'Segundo Piso'
# WIFI_PASSWORD = 'pv7Rkxczr6vg'
WIFI_SSID = 'elbug'
WIFI_PASSWORD = 'pds20231'



# Connect to wifi
led = machine.Pin(2, machine.Pin.OUT)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('Connecting to network...')
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        led.off()
        pass
    led.on()
    print('Connection successful')
    print('Network config:', wlan.ifconfig())

