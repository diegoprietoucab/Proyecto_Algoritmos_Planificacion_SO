import tkinter as tk
from tkinter import ttk

from UI.gui.theme import COLORS, FONTS


class ComparativePanel(tk.Frame):
    def __init__(self, parent: tk.Widget, app) -> None:
        super().__init__(parent, bg=COLORS['base'])
        self.app = app
        self._build()

    #  Layout

    def _build(self) -> None:
        tk.Label(self, text="📈  Tabla Comparativa",
                 bg=COLORS['base'], fg=COLORS['text'], font=FONTS['title']
                 ).pack(anchor='w', padx=30, pady=(24, 0))
        tk.Frame(self, bg=COLORS['surface1'], height=1).pack(fill='x', padx=30, pady=(8, 16))

        # Action row
        row = tk.Frame(self, bg=COLORS['base'])
        row.pack(fill='x', padx=30, pady=(0, 10))
        self._note = tk.Label(row, text="Ejecute al menos 2 algoritmos para comparar.",
                               bg=COLORS['base'], fg=COLORS['subtext0'], font=FONTS['body'])
        self._note.pack(side='left')
        ttk.Button(row, text="🗑  Limpiar historial", style='Danger.TButton',
                   command=self._clear).pack(side='right')

        # Table
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

        # Highlight tags
        self._tree.tag_configure('best', foreground=COLORS['green'],
                                  font=('Segoe UI', 10, 'bold'))
        self._tree.tag_configure('normal', foreground=COLORS['text'])

        # Conclusion label
        self._conclusion = tk.Label(self, text='', bg=COLORS['base'],
                                     fg=COLORS['green'], font=FONTS['heading'])
        self._conclusion.pack(anchor='w', padx=30, pady=(0, 12))

    #  Public

    def on_update(self) -> None:
        self._refresh()

    #  Internal

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

        best_name = ''
        best_espera = float('inf')

        for reg in hist:
            name     = reg['algoritmo']
            m        = reg['metricas']
            retorno  = m['tiempo_retorno_promedio']
            espera   = m['tiempo_espera_promedio']
            cpu      = m['porcentaje_cpu_usada']

            if espera < best_espera:
                best_espera = espera
                best_name   = name

            self._tree.insert('', 'end',
                              values=(name, f"{retorno:.2f}", f"{espera:.2f}", f"{cpu:.1f}%"),
                              tags=('pending',))

        # Re-tag best row
        for iid in self._tree.get_children():
            vals = self._tree.item(iid, 'values')
            tag  = 'best' if vals[0] == best_name else 'normal'
            self._tree.item(iid, tags=(tag,))

        self._conclusion.configure(
            text=f"🏆  Algoritmo más eficiente: {best_name}  "
                 f"(menor T. Espera Prom. = {best_espera:.2f})"
        )

    def _clear(self) -> None:
        self.app.historial.clear()
        self._refresh()
