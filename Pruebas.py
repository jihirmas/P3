import requests

# URL a la que realizarás la solicitud POST
url = "http://192.168.0.66:80"


while True:
    opcion = int(input("""
              1) Presionar 1 para cargar
              2) Presionar 2 para retirar
              3) Presionar 3 para verificacion
              4) salir
              """))
    casillero = int(input("Ingrese el casillero: "))
    if opcion == 1:
        datos = {"accion": "cargar", "casillero": casillero}
    elif opcion == 2:
        datos = {"accion": "retirar", "casillero": casillero}
    elif opcion == 3:
        datos = {"accion": "verificacion", "casillero": casillero}
    elif opcion == 4:
        break
    else:
        continue
    respuesta = requests.post(url, data=datos)
    print(respuesta.text)
