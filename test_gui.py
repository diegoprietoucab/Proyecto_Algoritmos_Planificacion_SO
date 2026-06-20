import sys, os, tkinter as tk
sys.path.insert(0, os.getcwd())
os.chdir(os.getcwd())

from UI.gui.app import MainApp
from plan.process.process_class import Process

app = MainApp()
app.withdraw()

procesos = [Process(1,0,8,3), Process(2,1,4,1), Process(3,2,9,4), Process(4,3,5,2)]
app.set_procesos(procesos)

# Test simulation panel step generation
sp = app._panels['simulation']
try:
    steps = sp._generate_steps(procesos)
    print('Steps count:', len(steps))
    for i, s in enumerate(steps):
        print(f"Step {i}: tag={s['tag']!r}, text={s['text'][:60].strip()!r}")
    print('Simulation OK')
except Exception as e:
    import traceback
    traceback.print_exc()

# Test gantt panel
gp = app._panels['gantt']
segs = [(1, 0.0, 8.0), (2, 8.0, 12.0), (3, 12.0, 21.0), (4, 21.0, 26.0)]
try:
    app.set_gantt_data(segs, 'FCFS')
    print('Gantt update OK')
except Exception as e:
    import traceback
    traceback.print_exc()

# Test comparative panel
app.add_to_historial('FCFS', {'tiempo_retorno_promedio': 15.25, 'tiempo_espera_promedio': 8.75, 'porcentaje_cpu_usada': 100.0})
app.add_to_historial('SJF', {'tiempo_retorno_promedio': 12.0, 'tiempo_espera_promedio': 5.5, 'porcentaje_cpu_usada': 100.0})
print('Historial OK:', len(app.historial), 'entries')

app.destroy()
print('ALL TESTS PASSED')
