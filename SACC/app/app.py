from fastapi import FastAPI, HTTPException, Depends
import requests
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Annotated
import json
from itertools import permutations
from enum import Enum
import random
import string
from datetime import datetime


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def load_initial_data(db: Session):
    # Verificar si la tabla Station está vacía
    if not db.query(models.Station).count():
        # Si está vacía, cargar datos
        db_station = models.Station(address="G1", id=1)
        db.add(db_station)
        db_station = models.Station(address="G3", id=2)
        db.add(db_station)
        db_station = models.Station(address="G5", id=3)
        db.add(db_station)
        db.commit()

    # Verificar si la tabla Locker está vacía
    if not db.query(models.Locker).count():
        # Si está vacía, cargar datos
        db_locker = models.Locker(state=0, height=20, width=40, depth=20, station_id=1, id=1, personal_id=1)
        db.add(db_locker)
        db_locker = models.Locker(state=0, height=30, width=40, depth=20, station_id=1, id=2, personal_id=2)
        db.add(db_locker)
        db_locker = models.Locker(state=0, height=40, width=40, depth=20, station_id=1, id=3, personal_id=3)
        db.add(db_locker)
        db.commit()
        
        db_locker = models.Locker(state=0, height=20, width=50, depth=25, station_id=2, id=4, personal_id=1)
        db.add(db_locker)
        db_locker = models.Locker(state=0, height=20, width=60, depth=25, station_id=2, id=5, personal_id=2)
        db.add(db_locker)
        db_locker = models.Locker(state=0, height=20, width=30, depth=25, station_id=2, id=6, personal_id=3)
        db.add(db_locker)
        db.commit()
        db_locker = models.Locker(state=0, height=30, width=30, depth=30, station_id=3, id=7, personal_id=1)
        db.add(db_locker)
        db_locker = models.Locker(state=0, height=30, width=40, depth=30, station_id=3, id=8, personal_id=2)
        db.add(db_locker)
        db_locker = models.Locker(state=0, height=20, width=50, depth=30, station_id=3, id=9, personal_id=3)
        db.add(db_locker)
        db.commit()
        
    if not db.query(models.User).count():
        db_user = models.User(name="operario1", email="oper1@example.com", typeUser="operario")
        db.add(db_user)
        db_user = models.User(name="operario2", email="oper2@example.com", typeUser="operario")
        db.add(db_user)
        db_user = models.User(name="cliente1", email="client1@example.com", typeUser="cliente")
        db.add(db_user)
        db_user = models.User(name="cliente2", email="client2@example.com", typeUser="cliente")
        db.add(db_user)
        db.commit()
    
    
dp_dependecy = Annotated[Session, Depends(get_db)]
rellenar = True
if rellenar:
    load_initial_data(db=SessionLocal())

timeout_seconds = 10

def get_all_locker_from_station(db: Session, station_id: int):
    sql_query = text(f"SELECT * FROM locker WHERE station_id = {station_id}")
    result = db.execute(sql_query)
    return result.fetchall()

def all_stations(db: Session):
    sql_query = text(f"SELECT * FROM station")
    result = db.execute(sql_query)
    return result.fetchall()

def all_lockers(db: Session):
    sql_query = text(f"SELECT * FROM locker")
    result = db.execute(sql_query)
    return result.fetchall()

def get_locker_by_station_and_personal_id(db: Session, station_id: int, personal_id: int):
    sql_query = text(f"SELECT * FROM locker WHERE station_id = {station_id} AND personal_id = {personal_id}")
    result = db.execute(sql_query)
    return result.fetchone()[0]

def all_users(db: Session):
    sql_query = text(f"SELECT * FROM user")
    result = db.execute(sql_query)
    return result.fetchall()

def get_locker_personal_id(db: Session, locker_id: int):
    sql_query = text(f"SELECT * FROM locker WHERE id = {locker_id}")
    result = db.execute(sql_query)
    return result.fetchone()[1]

def locker_and_station_by_reservation_id(db: Session, reservation_id: int):
    sql_query = text(f"SELECT * FROM locker WHERE id = (SELECT locker_id FROM 'order' WHERE id = (SELECT order_id FROM reservation WHERE id = {reservation_id}))")
    result = db.execute(sql_query)
    return result.fetchone()

def station_by_locker_id(db: Session, locker_id: int):
    sql_query = text(f"SELECT * FROM station WHERE id = (SELECT station_id FROM locker WHERE id = {locker_id})")
    result = db.execute(sql_query)
    return result.fetchone()

def encontrar_locker_mas_pequeno(alto_paquete, ancho_paquete, profundidad_paquete, lockers):
    """
    Encuentra la caja más pequeña posible que puede acomodar un paquete dado.

    Args:
    - alto_paquete (float): Alto del paquete.
    - ancho_paquete (float): Largo del paquete.
    - profundidad_paquete (float): Profundidad del paquete.
    - lockers (list): lista de lockers, formato (locker_id, station_id): (alto, largo, profundidad).

    Returns:
    - locker or None: id del locker más pequeño posible. Si no hay ninguna caja que pueda acomodar el paquete, retorna None.
    """
    mejor_locker = None
    mejor_volumen = float(1000*1000*1000)
    dimensiones_permutadas = permutations([alto_paquete, ancho_paquete, profundidad_paquete])

    for locker in lockers:
        for dimensiones_paquete in dimensiones_permutadas:
            alto_paquete, ancho_paquete, profundidad_paquete = locker[3], locker[4], locker[5]
            if (
                dimensiones_paquete[0] <= alto_paquete and
                dimensiones_paquete[1] <= ancho_paquete and
                dimensiones_paquete[2] <= profundidad_paquete
            ):
                volumen_locker = alto_paquete * ancho_paquete * profundidad_paquete
                if volumen_locker < mejor_volumen:
                    mejor_locker = locker[0]
                    mejor_volumen = volumen_locker

    return mejor_locker

def generar_clave_alfanumerica(longitud=12):
    """
    Genera una clave alfanumérica aleatoria.

    Args:
    - longitud (int): Longitud de la clave. Por defecto, 12.

    Returns:
    - str: Clave alfanumérica generada.
    """
    caracteres = string.ascii_letters + string.digits  # Letras (mayúsculas y minúsculas) y dígitos
    clave_generada = ''.join(random.choice(caracteres) for _ in range(longitud))
    return clave_generada

app = FastAPI()

estados_generales = {
    0: "available",
    1: "reserved",
    2: "loading",
    3: "used",
    4: "unloading"
}

# del pdf es la 1
@app.get("/stations",tags=['GET STATIONS'])
async def get_available_lockers(db: dp_dependecy):
    try:
        try:
            lockers = all_lockers(db)
            data = {}
            for i in lockers:
                if i[2] == 0:
                    if i[7] not in data:
                        data[i[7]] = {i[1]: ("available", f"{i[3]}x{i[4]}x{i[5]}")}
                    else:
                        data[i[7]][i[1]] = ("available", f"{i[3]}x{i[4]}x{i[5]}")
            for i in all_stations(SessionLocal()):
                if i[0] not in data:
                    data[i[1]] = "No hay casilleros disponibles"
                else:
                    data[i[1]] = data.pop(i[0])
            return {"content": data}
        except Exception as e:
            return {"message": f"Error: {e}"}
    except requests.exceptions.Timeout:
        return {"message": "Timeout error"}

# del pdf es la 2
@app.post('/reserve', tags=['RESERVAR'])
async def reservar(alto_paquete: int, ancho_paquete: int, profundidad_paquete: int, user_id: int, db: dp_dependecy):
    try:
        try:
            sql_query = text(f"SELECT * FROM locker WHERE state = 0")
            result = db.execute(sql_query)
            lockers = result.fetchall()
            if len(lockers) == 0:
                return {"message": "Failed to reserve, no available lockers"}
            sql_query = text(f'SELECT * FROM "user" WHERE id = {user_id}')
            result = db.execute(sql_query)
            user = result.fetchone()
            if user is None:
                return {"message": "Failed to reserve, user does not exist"}
            locker = encontrar_locker_mas_pequeno(alto_paquete, ancho_paquete, profundidad_paquete, lockers)
            if locker is None:
                return {"message": "Failed to reserve, package is too big for available lockers"}
            else:
                # Creo una orden ficticia, porque debería exisitr una orden de antes
                db_order = models.Order(name="order ficitica", width=ancho_paquete, height=alto_paquete, depth=profundidad_paquete)
                db.add(db_order)
                db.commit()
                # Reservo el locker cambiando el estado
                sql_query = text(f"UPDATE locker SET state = 1 WHERE id = {locker}")
                db.execute(sql_query)
                db.commit()
                # Creo la reserva
                db_reservation = models.Reservation(user_id=user_id, order_id=db_order.id, locker_id=locker, locker_personal_id=get_locker_personal_id(db, locker), station_id=station_by_locker_id(db, locker)[0], fecha=datetime.now(), estado="activa")
                db.add(db_reservation)
                db.commit()
                # asigno un codigo al locker
                clave = generar_clave_alfanumerica()
                sql_query = text(f"UPDATE locker SET code = '{clave}' WHERE locker.id = {locker}")
                db.execute(sql_query)
                db.commit()
                return {"message": "Reservation successful", "locker_id": locker, "station_id": station_by_locker_id(db, locker)[0], "code": clave}
        except Exception as e:
            return {"message": f"Error: {e}"}
    except requests.exceptions.Timeout:
        return {"message": "Timeout error"}
    
    
# del pdf es la 4
@app.post('/cancel_reservation', tags=['CANCEL RESERVATION'])
async def cancel_reservation(reservation: int, db: dp_dependecy): #TODO NUMERO DE CAJON
    try:
        try:
            sql_query = text(f"SELECT * FROM reservation WHERE id = {reservation}")
            result = db.execute(sql_query)
            reserva = result.fetchone()
            if reserva is None:
                return {"message": "Failed to cancel reservation, reservation does not exist"}
            else:
                sql_query = text(f"SELECT * FROM locker WHERE id = {reserva[2]}")
                result = db.execute(sql_query)
                locker_obtenido = result.fetchone()
                if locker_obtenido[2] == 1:
                    sql_query = text(f"UPDATE locker SET state = 0 WHERE id = {locker_obtenido[0]}")
                    db.execute(sql_query)
                    db.commit()
                    sql_query = text(f"UPDATE reservation SET estado = 'cancelada' WHERE reservation.id = {reservation}")
                    db.execute(sql_query)
                    db.commit()
                    return {"message": "Reservation canceled successfully"}
                else:
                    return {"message": f"Failed to cancel reservation, locker is not reserved, it is {estados_generales[locker_obtenido[2]]} "}
        except Exception as e:
            return {"message": f"Error: {e}"}
    except requests.exceptions.Timeout:
        return {"message": "Timeout error"}




# @app.get('/verification', tags=['VERIFICATION'])
# async def hardware_verification():
#     data_to_send = {"accion":"verificacion","casillero":"1"}
#     url = f"http://{esp32_ip}:{esp32_port}"
#     response = requests.post(url,json=data_to_send)
#     print(response.text)

#     if response.status_code == 200:
#         return {"content": response.text}
#     else:
#         return {"message": "Failed to send POST request to ESP32", "status_code": response.status_code,"estados":state}
    

# @app.post('/cargar', tags=['CARGAR'])
# async def cargar(cajon:str): #TODO NUMERO DE CAJON

#     #VERIFICAR QUE EL CASILLERO ESTE RESERVADOR
#     if state[cajon]["estado"] !=2:
#         return {"message": "Failed to Cargar, no esta Reservado"}

#     data_to_send = {"accion":"cargar","casillero":cajon}
#     url = f"http://{esp32_ip}:{esp32_port}"
#     response = requests.post(url,json=data_to_send)


#     if response.status_code == 200:
#         state[cajon]["estado"] = 1
#         return {"content": response.text}
#     else:
#         return {"message": "Failed to send POST request to ESP32", "status_code": response.status_code}

# @app.post('/retirar', tags=['RETIRAR'])
# async def cargar(cajon:str): #TODO NUMERO DE CAJON

#     #VERIFICAR QUE EL CASILLERO ESTE RESERVADOR
#     if state[cajon]["estado"] != 1:
#         return {"message": "Failed to Retirar"}


#     data_to_send = {"accion":"retirar","casillero":cajon}
#     url = f"http://{esp32_ip}:{esp32_port}"
#     response = requests.post(url,json=data_to_send)
#     # print("papi que ta pasando")
#     # return {"content": "RETIRADO "}

#     if response.status_code == 200:
#         state[cajon]["estado"] = 0

#         return {"content": response.text}
#     else:
#         return {"message": "Failed to send POST request to ESP32", "status_code": response.status_code}

# @app.post('/reservar', tags=['RESERVAR'])
# async def cargar(cajon:str): #TODO NUMERO DE CAJON

#     #VERIFICAR QUE EL CASILLERO ESTE RESERVADOR
#     if state[cajon]["estado"] != 0:
#         return {"message": "Failed to Reservar, No esta disponible"}
        
#     data_to_send = {"accion":"retirar","casillero":cajon}
#     url = f"http://{esp32_ip}:{esp32_port}"
#     #TODO DINAMICO
#     state["1"]["estado"] = 2
#     return {"content":"Exito!"}