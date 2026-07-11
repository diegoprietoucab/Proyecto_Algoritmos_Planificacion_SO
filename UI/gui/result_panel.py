import copy
import tkinter as tk
from tkinter import ttk, messagebox

from plan.algorithms.fcfs import fcfs
from plan.algorithms.sjf import sjf
from plan.algorithms.round_robin import round_robin
from plan.algorithms.priority import prioridad_apropiativa
from plan.methrics import calcular_metricas_procesos, calcular_metricas_sistema
from UI.gui.theme import COLORS, FONTS
from UI.gui.runner import AlgorithmRunner
from UI.gui.gantt_builder import build_segments

ALGORITHMS = ['FCFS', 'SJF', 'Round Robin', 'Prioridad Apropiativa']


class ResultPanel(tk.Frame):
    def __init__(self, parent: tk.Widget, app) -> None:
        super().__init__(parent, bg=COLORS['base'])
        self.app = app
        self._runner = AlgorithmRunner(app)
        self._build()

    # Layout

    def _build(self) -> None:
        # Title
        tk.Label(self, text="⚙️  Ejecutar Algoritmo",
                 bg=COLORS['base'], fg=COLORS['text'], font=FONTS['title']
                 ).pack(anchor='w', padx=30, pady=(24, 0))
        tk.Frame(self, bg=COLORS['surface1'], height=1).pack(fill='x', padx=30, pady=(8, 16))

        # Controls bar
        ctrl = tk.Frame(self, bg=COLORS['surface0'])
        ctrl.pack(fill='x', padx=30, pady=(0, 12))

        tk.Label(ctrl, text="Algoritmo:", bg=COLORS['surface0'],
                 fg=COLORS['subtext1'], font=FONTS['body']).pack(side='left', padx=(12, 4))
        self._algo_var = tk.StringVar(value='FCFS')
        algo_cb = ttk.Combobox(ctrl, textvariable=self._algo_var,
                                values=ALGORITHMS, state='readonly', width=22)
        algo_cb.pack(side='left')
        algo_cb.bind('<<ComboboxSelected>>', self._on_algo_change)

        # Quantum (shown only for Round Robin)
        self._q_label = tk.Label(ctrl, text="Quantum:", bg=COLORS['surface0'],
                                  fg=COLORS['subtext1'], font=FONTS['body'])
        self._q_var = tk.StringVar(value='2')
        self._q_entry = tk.Entry(ctrl, textvariable=self._q_var, width=6,
                                  bg=COLORS['surface1'], fg=COLORS['text'],
                                  insertbackground=COLORS['text'], relief='flat',
                                  font=FONTS['body'])

        self._run_btn = ttk.Button(ctrl, text="▶  Ejecutar", style='Accent.TButton',
                                    command=self._run)
        self._run_btn.pack(side='right', padx=12)

        # Main split: log (left) | metrics (right)
        body = tk.Frame(self, bg=COLORS['base'])
        body.pack(fill='both', expand=True, padx=30, pady=(0, 12))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        self._build_log(body)
        self._build_metrics(body)

        # Status bar
        self._status_var = tk.StringVar(value="Seleccione un algoritmo y presione Ejecutar")
        tk.Label(self, textvariable=self._status_var,
                 bg=COLORS['base'], fg=COLORS['subtext0'], font=FONTS['small']
                 ).pack(anchor='w', padx=30, pady=(0, 8))

    def _build_log(self, parent: tk.Frame) -> None:
        frame = tk.Frame(parent, bg=COLORS['surface0'])
        frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        tk.Label(frame, text="Log de ejecución",
                 bg=COLORS['surface0'], fg=COLORS['blue'], font=FONTS['heading']
                 ).grid(row=0, column=0, sticky='w', padx=12, pady=(10, 6))

        self._log = tk.Text(frame, state='disabled', wrap='word',
                             bg=COLORS['mantle'], fg=COLORS['text'],
                             font=FONTS['mono'], relief='flat',
                             selectbackground=COLORS['surface1'])
        self._log.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 10))

        sb = ttk.Scrollbar(frame, orient='vertical', command=self._log.yview)
        sb.grid(row=1, column=1, sticky='ns', pady=(0, 10))
        self._log.configure(yscrollcommand=sb.set)

    def _build_metrics(self, parent: tk.Frame) -> None:
        frame = tk.Frame(parent, bg=COLORS['surface0'])
        frame.grid(row=0, column=1, sticky='nsew')
        frame.rowconfigure(2, weight=1)
        frame.columnconfigure(0, weight=1)

        tk.Label(frame, text="Métricas por proceso",
                 bg=COLORS['surface0'], fg=COLORS['blue'], font=FONTS['heading']
                 ).grid(row=0, column=0, sticky='w', padx=12, pady=(10, 6))

        # Process metrics table
        cols = ('PID', 'Ráfaga', 'T.Retorno', 'T.Espera', 'T.Respuesta')
        self._metrics_tree = ttk.Treeview(frame, columns=cols, show='headings', height=10)
        widths = [60, 80, 90, 90, 100]
        for c, w in zip(cols, widths):
            self._metrics_tree.heading(c, text=c)
            self._metrics_tree.column(c, anchor='center', width=w)
        self._metrics_tree.grid(row=2, column=0, sticky='nsew', padx=10, pady=(0, 8))

        sb2 = ttk.Scrollbar(frame, orient='vertical', command=self._metrics_tree.yview)
        sb2.grid(row=2, column=1, sticky='ns', pady=(0, 8))
        self._metrics_tree.configure(yscrollcommand=sb2.set)

        # System metrics summary card
        summ = tk.Frame(frame, bg=COLORS['surface1'])
        summ.grid(row=3, column=0, columnspan=2, sticky='ew', padx=10, pady=(0, 10))

        self._sys_labels: dict[str, tk.StringVar] = {}
        for row_idx, (key, label) in enumerate([
            ('retorno', 'T. Retorno Prom.'),
            ('espera',  'T. Espera Prom.'),
            ('cpu',     'Uso CPU'),
        ]):
            tk.Label(summ, text=f"{label}:", bg=COLORS['surface1'],
                     fg=COLORS['subtext1'], font=FONTS['small']
                     ).grid(row=row_idx, column=0, sticky='w', padx=10, pady=2)
            sv = tk.StringVar(value='—')
            self._sys_labels[key] = sv
            tk.Label(summ, textvariable=sv, bg=COLORS['surface1'],
                     fg=COLORS['text'], font=('Segoe UI', 10, 'bold')
                     ).grid(row=row_idx, column=1, sticky='w', padx=4)

    # Logic

    def _on_algo_change(self, _event=None) -> None:
        algo = self._algo_var.get()
        if algo == 'Round Robin':
            self._q_label.pack(side='left', padx=(16, 4))
            self._q_entry.pack(side='left')
        else:
            try:
                self._q_label.pack_forget()
                self._q_entry.pack_forget()
            except Exception:
                pass

    def _run(self) -> None:
        if not self.app.procesos:
            messagebox.showwarning("Sin procesos",
                                   "Primero cargue procesos desde el panel de Gestión.")
            return

        # Deep-copy so we don't mutate the master list between algorithm runs
        procesos = copy.deepcopy(self.app.procesos)
        algo = self._algo_var.get()

        try:
            fn, args = self._resolve(algo, procesos)
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))
            return

        self._run_btn.configure(state='disabled')
        self._status_var.set(f"⏳ Ejecutando {algo}…")

        self._runner.run(fn, args, self._log, self._on_done)

    def _resolve(self, algo: str, procesos) -> tuple:
        if algo == 'FCFS':
            return fcfs, (procesos,)
        if algo == 'SJF':
            return sjf, (procesos,)
        if algo == 'Round Robin':
            try:
                q = float(self._q_var.get())
                if q <= 0:
                    raise ValueError
            except ValueError:
                raise ValueError("El quantum debe ser un número positivo.")
            return round_robin, (procesos, q)
        if algo == 'Prioridad Apropiativa':
            return prioridad_apropiativa, (procesos,)
        raise ValueError(f"Algoritmo desconocido: {algo}")

    def _on_done(self, success: bool, _result, log_text: str) -> None:
        self._run_btn.configure(state='normal')

        if not success:
            self._status_var.set("❌ Error durante la ejecución")
            return

        algo = self._algo_var.get()
        procesos = copy.deepcopy(self.app.procesos)

        # Re-run silently to get process objects with inicio/fin set
        # We parse the captured log instead of re-running.
        segments = build_segments(log_text, procesos)
        self.app.set_gantt_data(segments, algo)

        # Calculate metrics from captured times embedded in the log
        # Build timing from segments per process
        pid_times: dict[int, tuple] = {}
        for pid, start, end in segments:
            if pid not in pid_times:
                pid_times[pid] = (start, end)
            else:
                pid_times[pid] = (pid_times[pid][0], max(pid_times[pid][1], end))

        for p in procesos:
            if p.pid in pid_times:
                p.inicio, p.fin = pid_times[p.pid]

        # Calculate and display metrics
        self._metrics_tree.delete(*self._metrics_tree.get_children())
        tiempo_total = max((end for _, _, end in segments), default=0.0)

        for p in procesos:
            if p.inicio is not None and p.fin is not None:
                calcular_metricas_procesos(p)
                self._metrics_tree.insert('', 'end', values=(
                    p.pid,
                    f"{p.rafaga:.2f}",
                    f"{p.tiempo_retorno:.2f}",
                    f"{p.tiempo_espera:.2f}",
                    f"{p.tiempo_respuesta:.2f}",
                ))

        if tiempo_total > 0:
            metricas = calcular_metricas_sistema(
                [p for p in procesos if p.fin is not None], tiempo_total
            )
            self._sys_labels['retorno'].set(f"{metricas['tiempo_retorno_promedio']:.2f}")
            self._sys_labels['espera'].set(f"{metricas['tiempo_espera_promedio']:.2f}")
            self._sys_labels['cpu'].set(f"{metricas['porcentaje_cpu_usada']:.1f}%")

            self.app.add_to_historial(algo, metricas)

        self._status_var.set(f"✅  {algo} completado — {len(procesos)} procesos")

    def on_update(self) -> None:
        pass
