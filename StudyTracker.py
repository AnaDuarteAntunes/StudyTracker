import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import csv
import os

# CONFIGURACIÓN Y CONSTANTES GLOBALES
CSV_FILENAME = "registo_estudo.csv"
CSV_HEADERS = [
    "Data", "HoraInicio", "HoraFim", "Tarefa", 
    "Horas", "Minutos", "Segundos", "TotalSegundos", "HorasDecimais"
]

# Lista de asignaturas o tareas predefinidas
DISCIPLINAS = [
    "Python", 
    "PROJECT", 
    "Cybersecurity", 
    "Data Access", 
    "Interface Development", 
    "English", 
    "Business Management Systems", 
    "Services and Processes Programming", 
    "Multimedia Programming and Mobile Devices", 
    "Employability", 
    "Digitalization", 
    "Sustainability Applied to Production Systems", 
    "Intermediate DAM Project"
]

# Paleta de colores para la interfaz
COLOR_BG = "#f0f0f0"
COLOR_DISPLAY = "#505C69"
COLOR_TEXT = "#ecf0f1"
COLOR_START = "#04c675"
COLOR_PAUSE = "#e4f80a"
COLOR_RESET = "#d34434"
COLOR_SAVE = "#25e0e7"


class ContadorEstudo:
    """Aplicación de seguimiento de tiempo de estudio con interfaz gráfica."""
    
    def __init__(self, master):
        self.master = master
        master.title("Tracker de Estudo Profissional")
        master.configure(bg=COLOR_BG)
        master.resizable(False, False)
        
        # Variables de control
        self.tempo = 0
        self.running = False
        self.inicio_sesion = None
        
        # Inicialización de componentes
        self._inicializar_csv()
        self._crear_interfaz()
        self._actualizar_estado_botones()
        self.update_clock()

    # MÉTODOS DE INICIALIZACIÓN
    def _inicializar_csv(self):
        """Inicializa el archivo CSV con encabezados si no existe."""
        if not os.path.exists(CSV_FILENAME):
            with open(CSV_FILENAME, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(CSV_HEADERS)

    def _crear_interfaz(self):
        """Crea todos los elementos de la interfaz de usuario."""
        # Frame principal con padding
        main_frame = tk.Frame(self.master, bg=COLOR_BG)
        main_frame.pack(padx=30, pady=20)
        
        # Display del cronómetro
        display_frame = tk.Frame(main_frame, bg=COLOR_DISPLAY, relief=tk.RIDGE, bd=2)
        display_frame.pack(pady=(0, 20))
        
        self.label = tk.Label(
            display_frame, 
            text="00:00:00", 
            font=("Helvetica", 56, "bold"),
            bg=COLOR_DISPLAY,
            fg=COLOR_TEXT,
            padx=40,
            pady=20
        )
        self.label.pack()
        
        # Estado del cronómetro (Parado / En progreso / Pausado)
        self.estado_label = tk.Label(
            main_frame,
            text="● Parado",
            font=("Helvetica", 11),
            bg=COLOR_BG,
            fg="#95a5a6"
        )
        self.estado_label.pack(pady=(0, 15))
        
        # Sección de selección de asignatura
        disciplina_frame = tk.Frame(main_frame, bg=COLOR_BG)
        disciplina_frame.pack(pady=(0, 20))
        
        tk.Label(
            disciplina_frame, 
            text="Disciplina / Tarefa:", 
            font=("Helvetica", 12, "bold"),
            bg=COLOR_BG
        ).pack()
        
        self.tarefa_var = tk.StringVar(self.master)
        self.tarefa_var.set(DISCIPLINAS[0])
        
        self.dropdown = tk.OptionMenu(disciplina_frame, self.tarefa_var, *DISCIPLINAS)
        self.dropdown.config(
            font=("Helvetica", 11),
            width=35,
            bg="white",
            relief=tk.GROOVE
        )
        self.dropdown.pack(pady=5)
        
        # Frame de botones
        botones_frame = tk.Frame(main_frame, bg=COLOR_BG)
        botones_frame.pack(pady=(10, 0))
        
        # Estilo común para botones
        btn_config = {
            "font": ("Helvetica", 11, "bold"),
            "width": 12,
            "height": 2,
            "relief": tk.RAISED,
            "bd": 2,
            "cursor": "hand2"
        }

        # Botón de inicio
        self.start_button = tk.Button(
            botones_frame,
            text="▶ Iniciar",
            command=self.start,
            bg=COLOR_START,
            fg="white",
            activebackground="#229954",
            **btn_config
        )
        self.start_button.grid(row=0, column=0, padx=5, pady=5)
        
        # Botón de pausa
        self.pause_button = tk.Button(
            botones_frame,
            text="⏸ Pausar",
            command=self.pause,
            bg=COLOR_PAUSE,
            fg="white",
            activebackground="#d68910",
            **btn_config
        )
        self.pause_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Botón de reinicio
        self.reset_button = tk.Button(
            botones_frame,
            text="🔄 Reiniciar",
            command=self.reset,
            bg=COLOR_RESET,
            fg="white",
            activebackground="#c0392b",
            **btn_config
        )
        self.reset_button.grid(row=1, column=0, padx=5, pady=5)
        
        # Botón de guardado
        self.save_button = tk.Button(
            botones_frame,
            text="💾 Guardar",
            command=self.save_progress,
            bg=COLOR_SAVE,
            fg="white",
            activebackground="#2980b9",
            **btn_config
        )
        self.save_button.grid(row=1, column=1, padx=5, pady=5)

    # MÉTODOS DE LÓGICA Y FUNCIONAMIENTO
    def _actualizar_estado_botones(self):
        """Actualiza el estado habilitado/deshabilitado de los botones según el contexto."""
        if self.running:
            self.start_button.config(state="disabled")
            self.pause_button.config(state="normal")
            self.dropdown.config(state="disabled")
            self.estado_label.config(text="● Em progresso", fg=COLOR_START)
        else:
            self.start_button.config(state="normal" if self.tempo >= 0 else "disabled")
            self.pause_button.config(state="disabled")
            
            if self.tempo > 0:
                self.dropdown.config(state="disabled")
                self.estado_label.config(text="● Pausado", fg=COLOR_PAUSE)
            else:
                self.dropdown.config(state="normal")
                self.estado_label.config(text="● Parado", fg="#95a5a6")

    def update_clock(self):
        """Actualiza el display del cronómetro cada segundo."""
        if self.running:
            self.tempo += 1
        
        # Cálculo de formato HH:MM:SS
        horas = self.tempo // 3600
        minutos = (self.tempo % 3600) // 60
        segundos = self.tempo % 60
        tiempo_str = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        
        self.label.config(text=tiempo_str)
        self.master.after(1000, self.update_clock)

    def start(self):
        """Inicia o reanuda el cronómetro."""
        if not self.running:
            if self.tempo == 0:
                self.inicio_sesion = datetime.now()
            self.running = True
            self._actualizar_estado_botones()

    def pause(self):
        """Pausa el cronómetro."""
        if self.running:
            self.running = False
            self._actualizar_estado_botones()

    def reset(self):
        """Reinicia el cronómetro, guardando primero si hay tiempo acumulado."""
        if self.tempo > 0:
            respuesta = messagebox.askyesno(
                "Confirmar Reinício",
                f"Tens {self.tempo // 60} minuto(s) registado(s).\n\n"
                "Desejas guardar antes de reiniciar?"
            )
            if respuesta:
                self.save_progress()
        
        self.running = False
        self.tempo = 0
        self.inicio_sesion = None
        self.label.config(text="00:00:00")
        self._actualizar_estado_botones()

    def save_progress(self):
        """Guarda el progreso actual en el archivo CSV."""
        if self.tempo == 0:
            messagebox.showinfo("Informação", "Não há tempo para guardar.")
            return
        
        try:
            data = datetime.now().strftime("%Y-%m-%d")
            hora_fim = datetime.now().strftime("%H:%M:%S")
            
            # Usar el tiempo real de inicio si está disponible
            if self.inicio_sesion:
                hora_inicio = self.inicio_sesion.strftime("%H:%M:%S")
            else:
                hora_inicio = (datetime.now() - timedelta(seconds=self.tempo)).strftime("%H:%M:%S")
            
            horas = self.tempo // 3600
            minutos = (self.tempo % 3600) // 60
            segundos = self.tempo % 60
            horas_decimais = round(self.tempo / 3600, 2)
            tarefa = self.tarefa_var.get()
            
            # Guardar los datos en el CSV
            with open(CSV_FILENAME, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow([
                    data, hora_inicio, hora_fim, tarefa,
                    horas, minutos, segundos, self.tempo, horas_decimais
                ])
            
            messagebox.showinfo(
                "Sucesso",
                f"Progresso guardado com sucesso!\n\n"
                f"Tarefa: {tarefa}\n"
                f"Duração: {horas}h {minutos}m {segundos}s"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao guardar o progresso:\n{str(e)}"
            )

# FUNCIÓN PRINCIPAL
def main():
    """Función principal para iniciar la aplicación."""
    root = tk.Tk()
    app = ContadorEstudo(root)
    
    # Centrar ventana en la pantalla
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()