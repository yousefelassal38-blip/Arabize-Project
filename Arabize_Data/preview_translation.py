import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk

BASE = Path(__file__).resolve().parent
DATA = BASE / 'plugins' / 'cotw' / 'data' / 'ar_full.json'
translations = json.loads(DATA.read_text(encoding='utf-8'))['translations']
rows = sorted(translations.items(), key=lambda item: item[0].casefold())

root = tk.Tk()
root.title('Arabize - معاينة الترجمة')
root.geometry('980x660')
root.minsize(760, 500)
root.configure(bg='#0e1621')

style = ttk.Style(root)
style.theme_use('clam')
style.configure('Treeview', background='#162231', fieldbackground='#162231', foreground='#f2f5f8', rowheight=31, borderwidth=0)
style.configure('Treeview.Heading', background='#25364a', foreground='#ffffff', font=('Segoe UI', 10, 'bold'))
style.map('Treeview', background=[('selected', '#d97920')], foreground=[('selected', '#ffffff')])

header = tk.Frame(root, bg='#0e1621')
header.pack(fill='x', padx=22, pady=(18, 10))
tk.Label(header, text='معاينة الترجمة العربية', bg='#0e1621', fg='#ffffff', font=('Segoe UI', 20, 'bold')).pack(anchor='e')
tk.Label(header, text=f'{len(rows)} نصًا متاحًا للمعاينة فقط. لا يتم تعديل ملفات اللعبة.', bg='#0e1621', fg='#9fb0c4', font=('Segoe UI', 11)).pack(anchor='e', pady=(4,0))

search_var = tk.StringVar()
entry = tk.Entry(root, textvariable=search_var, bg='#162231', fg='white', insertbackground='white', relief='flat', font=('Segoe UI', 12), justify='right')
entry.pack(fill='x', padx=22, ipady=9)
entry.insert(0, '')

frame = tk.Frame(root, bg='#0e1621')
frame.pack(fill='both', expand=True, padx=22, pady=14)
columns=('key','arabic')
tree=ttk.Treeview(frame, columns=columns, show='headings')
tree.heading('key', text='المفتاح الإنجليزي')
tree.heading('arabic', text='النص العربي داخل اللعبة')
tree.column('key', width=350, anchor='w')
tree.column('arabic', width=560, anchor='e')
scroll=ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
tree.configure(yscrollcommand=scroll.set)
tree.pack(side='left', fill='both', expand=True)
scroll.pack(side='right', fill='y')

def redraw(*_):
    query=search_var.get().strip().casefold()
    tree.delete(*tree.get_children())
    for key,value in rows:
        if not query or query in key.casefold() or query in value.casefold():
            tree.insert('', 'end', values=(key,value))

search_var.trace_add('write', redraw)
redraw()
entry.focus_set()
root.mainloop()
