import tkinter as tk
from tkinter import ttk

COLORS = {
    'base':     '#1e1e2e',
    'mantle':   '#181825',
    'crust':    '#11111b',
    'surface0': '#313244',
    'surface1': '#45475a',
    'surface2': '#585b70',
    'overlay0': '#6c7086',
    'text':     '#cdd6f4',
    'subtext1': '#bac2de',
    'subtext0': '#a6adc8',
    'blue':     '#89b4fa',
    'lavender': '#b4befe',
    'sapphire': '#74c7ec',
    'green':    '#a6e3a1',
    'yellow':   '#f9e2af',
    'red':      '#f38ba8',
    'purple':   '#cba6f7',
    'teal':     '#94e2d5',
    'peach':    '#fab387',
    'pink':     '#f5c2e7',
}

FONTS = {
    'title':   ('Segoe UI', 18, 'bold'),
    'heading': ('Segoe UI', 12, 'bold'),
    'body':    ('Segoe UI', 10),
    'small':   ('Segoe UI', 9),
    'mono':    ('Consolas', 10),
    'mono_sm': ('Consolas', 9),
}

PROCESS_COLORS = [
    '#89b4fa', '#a6e3a1', '#f9e2af', '#cba6f7',
    '#fab387', '#94e2d5', '#f5c2e7', '#f38ba8',
]


def apply_theme(root: tk.Tk) -> None:
    style = ttk.Style(root)
    style.theme_use('clam')

    bg      = COLORS['base']
    fg      = COLORS['text']
    card    = COLORS['surface0']
    border  = COLORS['surface1']
    sel_bg  = COLORS['surface1']

    style.configure('.', background=bg, foreground=fg, font=FONTS['body'], borderwidth=0)

    style.configure('TFrame',       background=bg)
    style.configure('Card.TFrame',  background=card)
    style.configure('Side.TFrame',  background=COLORS['mantle'])

    style.configure('TLabel',         background=bg,   foreground=fg)
    style.configure('Title.TLabel',   background=bg,   foreground=fg,             font=FONTS['title'])
    style.configure('Heading.TLabel', background=bg,   foreground=COLORS['blue'], font=FONTS['heading'])
    style.configure('Sub.TLabel',     background=bg,   foreground=COLORS['subtext0'], font=FONTS['small'])
    style.configure('Card.TLabel',    background=card, foreground=fg)
    style.configure('Side.TLabel',    background=COLORS['mantle'], foreground=fg)

    style.configure('TButton',
        background=card, foreground=fg,
        padding=(10, 6), relief='flat', focusthickness=0,
    )
    style.map('TButton',
        background=[('active', border), ('pressed', COLORS['surface2'])],
    )

    style.configure('Accent.TButton',
        background=COLORS['blue'], foreground=COLORS['base'],
        font=('Segoe UI', 10, 'bold'), padding=(12, 7),
    )
    style.map('Accent.TButton',
        background=[('active', COLORS['lavender']), ('pressed', COLORS['sapphire'])],
        foreground=[('active', COLORS['base'])],
    )

    style.configure('Danger.TButton',
        background=COLORS['red'], foreground=COLORS['base'],
        font=('Segoe UI', 10, 'bold'), padding=(10, 6),
    )
    style.map('Danger.TButton',
        background=[('active', '#eba0ac')],
        foreground=[('active', COLORS['base'])],
    )

    style.configure('Stop.TButton',
        background=COLORS['yellow'], foreground=COLORS['base'],
        font=('Segoe UI', 10, 'bold'), padding=(10, 6),
    )

    style.configure('Nav.TButton',
        background=COLORS['mantle'], foreground=COLORS['subtext1'],
        padding=(18, 12), anchor='w', font=FONTS['body'],
    )
    style.map('Nav.TButton',
        background=[('active', card)],
        foreground=[('active', fg)],
    )
    style.configure('NavOn.TButton',
        background=card, foreground=COLORS['blue'],
        padding=(18, 12), anchor='w', font=('Segoe UI', 10, 'bold'),
    )
    style.map('NavOn.TButton',
        background=[('active', card)],
        foreground=[('active', COLORS['blue'])],
    )

    style.configure('TEntry',
        fieldbackground=card, foreground=fg,
        insertcolor=fg, padding=6,
    )
    style.configure('TCombobox',
        fieldbackground=card, foreground=fg,
        selectbackground=sel_bg, arrowcolor=COLORS['blue'],
        padding=5,
    )
    style.map('TCombobox',
        fieldbackground=[('readonly', card)],
        foreground=[('readonly', fg)],
    )

    style.configure('Treeview',
        background=card, foreground=fg,
        fieldbackground=card, rowheight=26,
    )
    style.configure('Treeview.Heading',
        background=COLORS['mantle'], foreground=COLORS['blue'],
        font=FONTS['heading'], padding=(6, 5),
    )
    style.map('Treeview',
        background=[('selected', border)],
        foreground=[('selected', COLORS['blue'])],
    )
    style.map('Treeview.Heading',
        background=[('active', card)],
    )

    style.configure('TScrollbar',
        background=card, troughcolor=COLORS['mantle'],
        arrowcolor=COLORS['subtext0'], width=8,
    )

    style.configure('TSeparator', background=border)

    style.configure('TNotebook',       background=bg,   borderwidth=0)
    style.configure('TNotebook.Tab',
        background=card, foreground=COLORS['subtext0'],
        padding=(12, 6),
    )
    style.map('TNotebook.Tab',
        background=[('selected', COLORS['blue'])],
        foreground=[('selected', COLORS['base'])],
    )