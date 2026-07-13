import os
import sys
from plan.process.process_class import Process
import utils.validations as val
from utils.file_handler import leerProcesosJSON

pids_existentes = set()

def menuCreacion() -> None:
    print("\nSeleccione una de las siguientes opciones: ")
    print("1. Leer procesos desde un archivo")
    print("2. Crear proceso personalizado\n")

def cargaProcesos() -> list[Process]:
    procesos: list[Process] = []
    while True:
        menuCreacion()
        eleccion: str = input()
        match(eleccion):
            case "1":
                procesos = crearListaPredefinida()
                break
            case "2":
                procesos = crearListaManual()
                break
            case _:
                print("\nERROR. Asegúrese de ingresar una opción válida")
                continue
    return procesos

def crearProceso() -> Process:
    pid = val.leerPIDUnico("ID del proceso (número entero positivo):", pids_existentes)
    llegada = val.leerFloat("Tiempo de llegada (número positivo o cero):", "El tiempo de llegada", False)
    rafaga = val.leerFloat("Tiempo de ráfaga o uso de CPU (número positivo):", "El tiempo de ráfaga", True)
    prioridad = val.leerInt("Prioridad (número entero positivo o cero):", "La prioridad del proceso", False)
    return Process(pid, llegada, rafaga, prioridad)

def crearListaManual() -> list[Process]:
    procesos = []
    print("\nA continuación deberá llenar todos los datos que se solicitan\n")
    numero_procesos = val.leerInt("¿Cuántos procesos quiere registrar?:", "La cantidad de procesos", True)
    for i in range(numero_procesos):
        print(f"\n----------------------- Proceso{i + 1} -----------------------\n")
        proceso = crearProceso()
        pids_existentes.add(proceso.pid)
        procesos.append(proceso)
    return procesos

def menu() -> None:
    print("\nSeleccione una de los siguientes conjuntos predefinidos:")
    print("1. Procesos básicos")
    print("2. Procesos variados")
    print("3. Procesos personales")
    print("4. Prueba de round robin\n")
    
def obtenerRutaAbsoluta(ruta_relativa):
    """
    Obtiene la ruta absoluta de los archivos Json, 
    para que el programa sepa donde ubicar dichos archivos
    en dado caso que estemos en modo desarrollo o en el ejecutable.
    
    El bloque try intenta buscar sys._MEIPASS, en dado caso de que no
    se encuentre, se asume que estamos en el modo desarrollador y salta
    al bloque except, donde se obtiene la ruta absoluta del directorio actual.
    En dado caso de que el try funcione, entonces se toma toda la ruta de sys._MEIPASS 
    y se le agrega la ruta relativa del archivo.
    """
    try:
        # _MEIPASS es el directorio temporal que crea PyInstaller para
        # almacenar la ruta de los archivos cuando se ejecuta el programa 
        # como un ejecutable.
        ruta_base = sys._MEIPASS
    except Exception:
        # Este comando le pide al sistema operativo la ruta de la carpeta 
        # actual donde se está trabajando.
        ruta_base = os.path.abspath(".")
        # Este comando unifica la ruta base con la ruta relativa del archivo, 
        # con su respectivo "\"" para obtener la ruta absoluta del archivo.
    return os.path.join(ruta_base, ruta_relativa)

def crearListaPredefinida() -> list[Process]:
    procesos = []
    while(True):
        menu()
        eleccion = input()
        match(eleccion):
            case "1":
                ruta = "data/basicos.json"
                break
            case "2":
                ruta = "data/variados.json"
                break
            case "3":
                ruta = "data/personal.json"
                break
            case "4":
                ruta = "data/prueba_rr.json"
                break
            case _:
                print("\nERROR. Asegúrese de ingresar una opción válida")
                continue
            
    ruta_relativa = obtenerRutaAbsoluta(ruta)
    try:
        procesos = leerProcesosJSON(ruta_relativa) 
    except(ValueError, TypeError, KeyError, FileNotFoundError) as error:
        print(error)

    return procesos