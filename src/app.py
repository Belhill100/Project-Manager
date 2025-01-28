# app.py
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
#from .utils import validar_fecha, cargar_datos

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
JSON_PATH = os.path.join(DATA_DIR, "project_data.json")

# Configuración de estilos
COLOR_PRIMARIO = "#2c3e50"
COLOR_SECUNDARIO = "#3498db"
COLOR_FONDO = "#ecf0f1"
COLOR_TEXTO = "#2c3e50"

class Task:
    def __init__(self, name, description, assignee, due_date, status="Pending"):
        self.name = name
        self.description = description
        self.assignee = assignee
        self.due_date = due_date
        self.status = status

class ProjectManagerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Proyectos")
        self.geometry("1000x600")
        self.configure(bg=COLOR_FONDO)
        
        # Crear directorio data si no existe
        os.makedirs(DATA_DIR, exist_ok=True)
        
        self.tasks = []
        self.load_from_json()
        self.configurar_estilos()
        self.crear_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("TFrame", background=COLOR_FONDO)
        style.configure("TLabel", background=COLOR_FONDO, foreground=COLOR_TEXTO, font=('Arial', 10))
        style.configure("TButton", font=('Arial', 10), padding=6)
        style.map("TButton", background=[('active', COLOR_SECUNDARIO)])
        style.configure("Treeview", rowheight=25, font=('Arial', 10))
        style.configure("Treeview.Heading", font=('Arial', 11, 'bold'))
        
    def crear_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Formulario para nuevas tareas
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        campos = [
            ("Nombre:", "entry_name"),
            ("Descripción:", "entry_desc"),
            ("Asignado a:", "entry_assignee"),
            ("Fecha límite (YYYY-MM-DD):", "entry_date")
        ]
        
        for i, (texto, var) in enumerate(campos):
            ttk.Label(form_frame, text=texto).grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            setattr(self, var, entry)
        
        ttk.Button(form_frame, text="➕ Agregar Tarea", command=self.agregar_tarea,
                 style="Accent.TButton").grid(row=4, columnspan=2, pady=10)
        
        # Tabla de tareas
        columns = ("Nombre", "Descripción", "Asignado", "Fecha", "Estado")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", selectmode="browse")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor=tk.W)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Controles de estado
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.status_var = tk.StringVar()
        ttk.Combobox(control_frame, textvariable=self.status_var, 
                   values=["Pending", "In Progress", "Completed"], state="readonly").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="🔄 Actualizar Estado", command=self.actualizar_estado).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="🗑️ Eliminar Tarea", command=self.eliminar_tarea).pack(side=tk.LEFT, padx=10)
        
        self.actualizar_tabla()
    
    def agregar_tarea(self):
        try:
            nueva_tarea = Task(
                name=self.entry_name.get(),
                description=self.entry_desc.get(),
                assignee=self.entry_assignee.get(),
                due_date=self.entry_date.get(),
                status="Pending"
            )
            self.tasks.append(nueva_tarea)
            self.actualizar_tabla()
            self.limpiar_formulario()
        except Exception as e:
            messagebox.showerror("Error", f"Datos inválidos: {str(e)}")
    
    def actualizar_estado(self):
        seleccionado = self.tree.selection()
        if seleccionado:
            nuevo_estado = self.status_var.get()
            index = int(self.tree.index(seleccionado))
            self.tasks[index].status = nuevo_estado
            self.actualizar_tabla()
    
    def eliminar_tarea(self):
        seleccionado = self.tree.selection()
        if seleccionado:
            index = int(self.tree.index(seleccionado))
            del self.tasks[index]
            self.actualizar_tabla()
    
    def limpiar_formulario(self):
        for entry in [self.entry_name, self.entry_desc, self.entry_assignee, self.entry_date]:
            entry.delete(0, tk.END)
    
    def actualizar_tabla(self):
        self.tree.delete(*self.tree.get_children())
        for task in self.tasks:
            self.tree.insert("", tk.END, values=(
                task.name,
                task.description,
                task.assignee,
                task.due_date,
                task.status
            ), tags=(task.status,))
        
        # Colorear por estado
        self.tree.tag_configure("Pending", foreground="#e74c3c")
        self.tree.tag_configure("In Progress", foreground="#f39c12")
        self.tree.tag_configure("Completed", foreground="#2ecc71")
    
    def save_to_json(self, filename="project_data.json"):
        data = [vars(task) for task in self.tasks]
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
    
    def load_from_json(self, filename="project_data.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                self.tasks = [Task(**item) for item in data]
        except FileNotFoundError:
            pass
    
    def on_close(self):
        self.save_to_json()
        self.destroy()


    # Persistencia de datos
    def save_to_json(self):
        data = [vars(task) for task in self.tasks]
        try:
            with open(JSON_PATH, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")

    def load_from_json(self):
        try:
            with open(JSON_PATH, "r") as f:
                data = json.load(f)
                self.tasks = [Task(**item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.tasks = []

    def on_close(self):
        self.save_to_json()
        self.destroy()

if __name__ == "__main__":
    app = ProjectManagerGUI()
    app.mainloop()