import tkinter as tk
from tkinter import ttk

from UI.gui.theme import COLORS, FONTS


class ComparativePanel(tk.Frame):
    def __init__(self, parent: tk.Widget, app) -> None:
        super().__init__(parent, bg=COLORS['base'])
        self.app = app
        self._build()

    def _build(self) -> None:
        tk.Label(self, text="📈  Tabla Comparativa",
                 bg=COLORS['base'], fg=COLORS['text'], font=FONTS['title']
                 ).pack(anchor='w', padx=30, pady=(24, 0))
        tk.Frame(self, bg=COLORS['surface1'], height=1).pack(fill='x', padx=30, pady=(8, 16))

        row = tk.Frame(self, bg=COLORS['base'])
        row.pack(fill='x', padx=30, pady=(0, 10))
        self._note = tk.Label(row, text="Ejecute al menos 2 algoritmos para comparar.",
                               bg=COLORS['base'], fg=COLORS['subtext0'], font=FONTS['body'])
        self._note.pack(side='left')
        ttk.Button(row, text="🗑  Limpiar historial", style='Danger.TButton',
                   command=self._clear).pack(side='right')

        cols = ('Algoritmo', 'T.Retorno Prom.', 'T.Espera Prom.', 'Uso CPU (%)')
        frame = tk.Frame(self, bg=COLORS['surface0'])
        frame.pack(fill='both', expand=True, padx=30, pady=(0, 12))
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self._tree = ttk.Treeview(frame, columns=cols, show='headings')
        widths = [220, 140, 140, 120]
        for c, w in zip(cols, widths):
            self._tree.heading(c, text=c)
            self._tree.column(c, anchor='center', width=w)
        self._tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        sb = ttk.Scrollbar(frame, orient='vertical', command=self._tree.yview)
        sb.grid(row=0, column=1, sticky='ns', pady=10)
        self._tree.configure(yscrollcommand=sb.set)

        self._tree.tag_configure('best',
                                  foreground=COLORS['green'],
                                  font=('Segoe UI', 10, 'bold'))
        self._tree.tag_configure('normal', foreground=COLORS['text'])
        self._tree.tag_configure('separator',
                                  foreground=COLORS['blue'],
                                  font=('Segoe UI', 10, 'bold'),
                                  background=COLORS['surface1'])

        self._conclusion = tk.Label(self, text='', bg=COLORS['base'],
                                     fg=COLORS['green'], font=FONTS['heading'])
        self._conclusion.pack(anchor='w', padx=30, pady=(0, 12))

    def on_update(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        self._tree.delete(*self._tree.get_children())
        hist = self.app.historial

        if len(hist) < 2:
            self._note.configure(
                text="Ejecute al menos 2 algoritmos para comparar.",
                fg=COLORS['subtext0'],
            )
            self._conclusion.configure(text='')
            return

        self._note.configure(
            text=f"{len(hist)} algoritmo(s) comparados:",
            fg=COLORS['subtext1'],
        )

        best_espera = min(r['metricas']['tiempo_espera_promedio'] for r in hist)

        groups: dict[str, list[dict]] = {}
        for reg in hist:
            ds = reg.get('dataset', 'Manual')
            groups.setdefault(ds, []).append(reg)

        first_group = True
        for dataset_name, records in groups.items():
            sep_text = f"─── {dataset_name} ───"
            self._tree.insert('', 'end',
                              values=(sep_text, '', '', ''),
                              tags=('separator',))

            for reg in records:
                name    = reg['algoritmo']
                m       = reg['metricas']
                retorno = m['tiempo_retorno_promedio']
                espera  = m['tiempo_espera_promedio']
                cpu     = m['porcentaje_cpu_usada']

                is_best = (espera == best_espera)
                tag = 'best' if is_best else 'normal'

                self._tree.insert('', 'end',
                                  values=(name,
                                          f"{retorno:.2f}",
                                          f"{espera:.2f}",
                                          f"{cpu:.1f}%"),
                                  tags=(tag,))

            first_group = False

        best_reg = min(hist, key=lambda r: r['metricas']['tiempo_espera_promedio'])
        best_name = best_reg['algoritmo']

        self._conclusion.configure(
            text=f"🏆  Algoritmo más eficiente: {best_name}  "
                 f"(menor T. Espera Prom. = {best_espera:.2f})"
        )

    def _clear(self) -> None:
        self.app.historial.clear()
        self._refresh()
