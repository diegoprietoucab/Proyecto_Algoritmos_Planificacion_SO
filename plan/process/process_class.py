from typing import Optional
from plan.process.process_state import ProcessState
from dataclasses import dataclass, field

@dataclass
class Process:
    pid: int
    llegada: float
    rafaga: float
    prioridad: int = 0

    estado: ProcessState = field(default = ProcessState.NEW, init = False)
    tiempo_restante: float = field(init = False)
    inicio: Optional[float] = field(default = None, init = False)
    fin: Optional[float] = field(default = None, init = False)
    tiempo_espera: float = field(default = 0, init = False)
    tiempo_retorno: float = field(default = 0, init = False)
    tiempo_respuesta: float = field(default = 0, init = False)

    def __post_init__(self) -> None:
        self.tiempo_restante = self.rafaga

    def reiniciar(self) -> None:
        self.estado = ProcessState.NEW
        self.tiempo_restante = self.rafaga
        self.inicio = None
        self.fin = None
        self.tiempo_espera = 0
        self.tiempo_retorno = 0
        self.tiempo_respuesta = 0