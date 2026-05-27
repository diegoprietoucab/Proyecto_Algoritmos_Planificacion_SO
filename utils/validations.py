def leerFloat(mensaje:str, variable: str, excluir_cero: bool = False) -> float:
    while True:
        try:
            print(mensaje, end=" ")
            valor = float(input())
            if not excluir_cero:
                if valor < 0:
                    print(f"\nERROR. {variable} no debe ser negativa\n")
                    continue
            else:
                if valor <= 0:
                    print(f"\nERROR. {variable} debe ser positiva\n")
                    continue
            return valor
        except ValueError:
            print(f"\nERROR. {variable} debe ser un número\n")

def leerInt(mensaje:str, variable: str, excluir_cero: bool = False) -> int:
    while True:
        try:
            print(mensaje, end=" ")
            valor = int(input())
            if not excluir_cero:
                if valor < 0:
                    print(f"\nERROR. {variable} no debe ser negativa\n")
                    continue
            else:
                if valor <= 0:
                    print(f"\nERROR. {variable} debe ser positiva\n")
                    continue
            return valor
        except ValueError:
            print(f"\nERROR. {variable} debe ser un número entero\n")

def leerPIDUnico(mensaje: str, pids_existentes: set[int]) -> int:
    while True:
        pid = leerInt(mensaje, "El ID del proceso", True)
        if pid in pids_existentes:
            print("\nERROR. Ya existe un proceso con ese PID\n")
        else:
            break
    return pid