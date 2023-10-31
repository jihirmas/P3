import os
import time
import ujson
import machine
import esp32
import random
import usocket as socket
from machine import Pin, PWM  

class Servo:
    # these defaults work for the standard TowerPro SG90
    __servo_pwm_freq = 50
    __min_u10_duty = 26 - 0 # offset for correction
    __max_u10_duty = 123- 0  # offset for correction
    min_angle = 0
    max_angle = 180
    current_angle = 0.001


    def __init__(self, pin):
        self.__initialise(pin)


    def update_settings(self, servo_pwm_freq, min_u10_duty, max_u10_duty, min_angle, max_angle, pin):
        self.__servo_pwm_freq = servo_pwm_freq
        self.__min_u10_duty = min_u10_duty
        self.__max_u10_duty = max_u10_duty
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.__initialise(pin)


    def move(self, angle):
        # round to 2 decimal places, so we have a chance of reducing unwanted servo adjustments
        angle = round(angle, 2)
        # do we need to move?
        if angle == self.current_angle:
            return
        self.current_angle = angle
        # calculate the new duty cycle and move the motor
        duty_u10 = self.__angle_to_u10_duty(angle)
        self.__motor.duty(duty_u10)

    def __angle_to_u10_duty(self, angle):
        return int((angle - self.min_angle) * self.__angle_conversion_factor) + self.__min_u10_duty


    def __initialise(self, pin):
        self.current_angle = -0.001
        self.__angle_conversion_factor = (self.__max_u10_duty - self.__min_u10_duty) / (self.max_angle - self.min_angle)
        self.__motor = PWM(Pin(pin))
        self.__motor.freq(self.__servo_pwm_freq)
        
#Asignando pines a los servos
motor1 = Servo(pin=14)
motor2 = Servo(pin=12)
motor3 = Servo(pin=27)

#Asignadno pines a los sensores infrarrojos
pin_sensor_IR_1 = machine.Pin(25, machine.Pin.IN)
pin_sensor_IR_2 = machine.Pin(32, machine.Pin.IN)
pin_sensor_IR_3 = machine.Pin(33, machine.Pin.IN)

#Asignando pines a magneticos (solo 1 para la EP2)
pin_sensor_magnetico_1 = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
pin_sensor_magnetico_2 = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)
pin_sensor_magnetico_3 = machine.Pin(17, machine.Pin.IN, machine.Pin.PULL_UP)

#Ponindo los servos en 180 grados (posicion cerrado)
# motor1.move(0)
# time.sleep(0.25)
# motor2.move(0)
# time.sleep(0.25)
# motor3.move(0)
# time.sleep(0.25)
# time.sleep(3)
time.sleep(0.25)
motor1.move(120)
time.sleep(0.25)
motor2.move(120)
time.sleep(0.25)
motor3.move(120)
time.sleep(0.25)


def leer_sensor_IR(locker_id):
    time.sleep(0.25)
    if locker_id == 1:
        estado = pin_sensor_IR_1.value()
    elif locker_id == 2:
        estado = pin_sensor_IR_2.value()
    elif locker_id == 3:
        estado = pin_sensor_IR_3.value()
    time.sleep(0.25)
    print(f"Locker {locker_id} - IR: {estado}")
    if estado == 0:
        return True
    else:
        return False
    
def mover_servo(locker_id, angulo):
    time.sleep(0.25)
    if locker_id == 1:
        motor1.move(angulo)
    elif locker_id == 2:
        motor2.move(angulo)
    elif locker_id == 3:
        motor3.move(angulo)
    else:
        print("ERRROR")
    time.sleep(0.25)

def verificacion_fisica():
    dict_lockers = {}
    for i in range(1,4):
        lleno = leer_sensor_IR(i)
        if lleno:
            dict_lockers[i] = True
        else:
            dict_lockers[i] = False
    estados = ujson.dumps(dict_lockers)
    response = f"HTTP/1.1 200 OK\r\n"
    response += f"Content-Type: application/json\r\n\r\n"
    response += "Acces-Control-Allow-Origin: *\r\n\r\n"
    response += "{"
    response += f"'message': {estados}"
    response += "}"
    return response

def leer_sensor_magentico(locker_id):
    time.sleep(0.25)
    if locker_id == 1:
        estado = pin_sensor_magnetico_1.value()
    elif locker_id == 2:
        estado = pin_sensor_magnetico_2.value()
    elif locker_id == 3:
        estado = pin_sensor_magnetico_3.value()
    print(f"Locker {locker_id} - Magnetico: {estado}")
    time.sleep(0.25) 
    if estado == 0:
        return True
    else:
        return False

def esperar_cierre(locker_id):
    time.sleep(0.25)
    while True:
        lectura = leer_sensor_magentico(locker_id)
        print(f"Locker {locker_id} - Magnetico: {lectura}")
        if lectura:
            print("Puerta cerrada")
            break
        else:
            print(f"Puerta abierta")
            pass
        time.sleep(0.25)
    time.sleep(0.25)
    
def esperar_infrarrojo(locker_id, modo):
    time.sleep(0.25)
    while True:
        lectura = leer_sensor_IR(locker_id)
        print(f"Locker {locker_id} - IR: {lectura}")
        if modo == "cargar":
            if lectura:
                print("Paquete Cargado")
                print("")
                break
            else:
                print(f"No hay nada en el locker")
                pass
        elif modo == "retirar":
            if not lectura:
                print("Paquete Retirado")
                print("")
                break
            else:
                print(f"Hay algo en el locker")
        time.sleep(0.25)
    time.sleep(0.25)
    
def abrir_locker(locker_id, modo):
    print(f"Abriendo locker {locker_id} para {modo}")
    mover_servo(locker_id, 0)
    esperar_infrarrojo(locker_id, modo)
    esperar_cierre(locker_id)
    mover_servo(locker_id, 120)
    print(f"Locker {locker_id} cerrado")
    response = f"HTTP/1.1 200 OK\r\n"
    response += f"Content-Type: application/json\r\n\r\n"
    response += "Acces-Control-Allow-Origin: *\r\n\r\n"
    response += "{'message': 'Abierto en mode l}"
    return response    

def handle_post_request(client, content):
    print(content)
    json_data = ujson.loads(content)
    print(json_data)
    try:
        json_data = ujson.loads(content)
        accion = json_data.get("accion")
        casillero = int(json_data.get("casillero"))
        if str(accion) == "verificacion":
            response = verificacion_fisica()
        elif str(accion) == "cargar":
            response = abrir_locker(casillero, "cargar")
        elif str(accion) == "retirar":
            response = abrir_locker(casillero, "retirar")
        else: 
            response = "HTTP/1.1 400 Bad Request\r\n\r\nAccion no reconocida"
    except ValueError as e:
        response = f"HTTP/1.1 400 Bad Request\r\n\r\nError al analizar JSON. se recibió {content}"
        print(e)
    client.send(response)
    client.close()

# MAIN

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 80))
s.listen(5)

print("Esperando solicitudes...")

while True:
    time.sleep(1)
    hora_actual = time.localtime()
    print(f"Esperando solicitud a las")
    try:
        client, addr = s.accept()
    except Exception as error:
        print(error)
        continue
    try:
        request = client.recv(1024)
        end_of_headers = request.find(b'\r\n\r\n') + 4
        content = request[end_of_headers:].decode('utf-8')
        if b"POST" in request and b"Content-Length" in request:
            handle_post_request(client, content)
        else: # GET
            response = "HTTP/1.1 200 OK\r\n\r\nHola desde ESP32"
            client.send(response)
            client.close()
    except Exception as e:
        print(e)
        print("Cliente desconectado por error")
        pass
    finally:
        client.close()


