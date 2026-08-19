import os
import json
import threading
import customtkinter as ctk
from datetime import datetime
from base import PluginBase
from dotenv import load_dotenv

load_dotenv()

modelo_ollama = os.getenv("OLLAMA_MODEL", "gemma:2b")  # Modelo por defecto si no está en .env

# Intento de importación segura de TkCalendar
try:
    from tkcalendar import Calendar
    TKCALENDAR_DISPONIBLE = True
except ImportError:
    TKCALENDAR_DISPONIBLE = False

# Intento de importación segura de Ollama
try:
    import ollama
    OLLAMA_DISPONIBLE = True
except ImportError:
    OLLAMA_DISPONIBLE = False


class PluginAgendaCalendario(PluginBase):
    def __init__(self):
        super().__init__()
        self.ventana_agenda = None
        self.ruta_json = os.path.join(os.path.dirname(__file__), "agenda.json")
        self.datos_agenda = self._cargar_datos()
        self.modelo_ollama = modelo_ollama

    @property
    def nombre(self) -> str:
        return "Calendario y Agenda"

    @property
    def descripcion(self) -> str:
        return "Permite gestionar eventos y citas mediante un calendario visual y añadirlas mediante expresiones comunes como 'mañana', 'el próximo lunes', etc. También permite consultar la agenda y revisar eventos pasados o futuros."

    @property
    def acepta_comandos_directos(self) -> bool:
        return True

    def cargar_ui(self, frame_espacio, funcion_chat, app=None):
        self.frame_espacio = frame_espacio
        self.funcion_chat = funcion_chat
        self.app = app

    def al_activar(self):
        self.btn_abrir = ctk.CTkButton(
            self.frame_espacio,
            text="Abrir Agenda",
            font=("Consolas", 12, "bold"),
            fg_color="#1E293B",
            hover_color="#334155",
            border_color="#00F0FF",
            border_width=1,
            command=self.abrir_ventana_agenda
        )
        self.btn_abrir.pack(side="left", padx=10, pady=5)

    def al_desactivar(self):
        if hasattr(self, 'btn_abrir') and self.btn_abrir:
            self.btn_abrir.destroy()
        if self.ventana_agenda and self.ventana_agenda.winfo_exists():
            self.ventana_agenda.destroy()

    # Gestión de datos de la agenda
    def _cargar_datos(self) -> dict:
        if os.path.exists(self.ruta_json):
            try:
                with open(self.ruta_json, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _guardar_datos(self):
        try:
            with open(self.ruta_json, "w", encoding="utf-8") as f:
                json.dump(self.datos_agenda, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.funcion_chat(self.nombre, f"Error al guardar datos: {e}")

    # Ventana de la agenda y calendario
    def abrir_ventana_agenda(self):
        if self.ventana_agenda and self.ventana_agenda.winfo_exists():
            self.ventana_agenda.focus()
            return

        self.ventana_agenda = ctk.CTkToplevel(self.app)
        self.ventana_agenda.title("P.A.C.A. - Agenda y Eventos")
        self.ventana_agenda.geometry("600x500")
        self.ventana_agenda.attributes("-topmost", True)

        # Panel Izquierdo: Calendario
        frame_izq = ctk.CTkFrame(self.ventana_agenda, width=280)
        frame_izq.pack(side="left", fill="both", padx=10, pady=10)

        hoy_str = datetime.now().strftime("%Y-%m-%d")

        if TKCALENDAR_DISPONIBLE:
            self.cal = Calendar(
                frame_izq, 
                selectmode='day', 
                date_pattern='yyyy-mm-dd',
                background="#0A0E17",
                foreground="#00F0FF",
                headersbackground="#111827",
                normalbackground="#050811",
                normalforeground="#E2E8F0"
            )
            self.cal.pack(padx=10, pady=10, fill="both", expand=True)
            self.cal.bind("<<CalendarSelected>>", self._al_seleccionar_fecha)
        else:
            lbl_no_cal = ctk.CTkLabel(
                frame_izq, 
                text="Fecha (AAAA-MM-DD):\n(instala 'tkcalendar' para vista visual)",
                font=("Consolas", 11)
            )
            lbl_no_cal.pack(pady=(10, 5))
            self.entry_fecha = ctk.CTkEntry(frame_izq, font=("Consolas", 12))
            self.entry_fecha.insert(0, hoy_str)
            self.entry_fecha.pack(padx=10, pady=5, fill="x")

            btn_ver = ctk.CTkButton(
                frame_izq, 
                text="Cargar Fecha", 
                command=lambda: self.cargar_tareas_fecha(self.entry_fecha.get())
            )
            btn_ver.pack(pady=5)

        # Panel Derecho: Tareas de la fecha seleccionada
        frame_der = ctk.CTkFrame(self.ventana_agenda)
        frame_der.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)

        self.lbl_fecha_titulo = ctk.CTkLabel(
            frame_der, 
            text=f"Eventos: {hoy_str}", 
            font=("Consolas", 14, "bold"),
            text_color="#00FF9D"
        )
        self.lbl_fecha_titulo.pack(pady=10)

        # Entrada manual para nueva tarea
        frame_nueva = ctk.CTkFrame(frame_der, fg_color="transparent")
        frame_nueva.pack(fill="x", padx=10, pady=(0, 10))

        self.entry_nueva_tarea = ctk.CTkEntry(
            frame_nueva, 
            placeholder_text="Nueva tarea o nota...", 
            font=("Consolas", 12)
        )
        self.entry_nueva_tarea.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_nueva_tarea.bind("<Return>", lambda e: self.agregar_tarea())

        btn_add = ctk.CTkButton(
            frame_nueva, 
            text="+", 
            width=35, 
            font=("Consolas", 14, "bold"),
            command=self.agregar_tarea
        )
        btn_add.pack(side="right")

        # Lista scrolleable de tareas
        self.scroll_tareas = ctk.CTkScrollableFrame(frame_der, label_text="Lista de Citas")
        self.scroll_tareas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.fecha_seleccionada = hoy_str
        self.cargar_tareas_fecha(hoy_str)

    def _al_seleccionar_fecha(self, event=None):
        fecha = self.cal.get_date()
        self.cargar_tareas_fecha(fecha)

    def cargar_tareas_fecha(self, fecha_str: str):
        self.fecha_seleccionada = fecha_str
        self.lbl_fecha_titulo.configure(text=f"Eventos: {fecha_str}")

        for widget in self.scroll_tareas.winfo_children():
            widget.destroy()

        tareas = self.datos_agenda.get(fecha_str, [])

        if not tareas:
            lbl_vacio = ctk.CTkLabel(self.scroll_tareas, text="Sin eventos agendados", text_color="#64748B")
            lbl_vacio.pack(pady=10)
            return

        for idx, item in enumerate(tareas):
            frame_item = ctk.CTkFrame(self.scroll_tareas, fg_color="#1E293B")
            frame_item.pack(fill="x", pady=2, padx=2)

            lbl_t = ctk.CTkLabel(frame_item, text=f"• {item}", anchor="w", font=("Consolas", 12), text_color="#E2E8F0")
            lbl_t.pack(side="left", fill="x", expand=True, padx=8, pady=4)

            btn_del = ctk.CTkButton(
                frame_item, 
                text="X", 
                width=25, 
                height=20, 
                fg_color="#EF4444", 
                hover_color="#DC2626",
                command=lambda i=idx: self.borrar_tarea(i)
            )
            btn_del.pack(side="right", padx=5)

    def agregar_tarea(self, fecha: str = None, texto: str = None):
        fecha_target = fecha if fecha else self.fecha_seleccionada
        texto_target = texto if texto else self.entry_nueva_tarea.get().strip()

        if not texto_target:
            return

        if fecha_target not in self.datos_agenda:
            self.datos_agenda[fecha_target] = []

        self.datos_agenda[fecha_target].append(texto_target)
        
        if not fecha and not texto:
            self.entry_nueva_tarea.delete(0, "end")

        self._guardar_datos()
        
        # Si la ventana del GUI está abierta, actualiza la vista
        if self.ventana_agenda and self.ventana_agenda.winfo_exists():
            self.cargar_tareas_fecha(self.fecha_seleccionada)

    def borrar_tarea(self, indice: int):
        if self.fecha_seleccionada in self.datos_agenda:
            del self.datos_agenda[self.fecha_seleccionada][indice]
            if not self.datos_agenda[self.fecha_seleccionada]:
                del self.datos_agenda[self.fecha_seleccionada]
            self._guardar_datos()
            self.cargar_tareas_fecha(self.fecha_seleccionada)

    # Procesamiento de comandos de texto
    def procesar_comando_directo(self, texto: str):
        """Se ejecuta cuando seleccionas 'Calendario y Agenda' en el menú desplegable del chat"""
        if not OLLAMA_DISPONIBLE:
            self.funcion_chat(self.nombre, "La librería 'ollama' no está instalada.")
            return

        # Ejecutamos la consulta en un hilo secundario para no congelar la interfaz
        threading.Thread(target=self._procesar_con_ia, args=(texto,), daemon=True).start()

    def procesar_comando(self, texto: str):
        """Se ejecuta desde el canal 'General (Todos)' si se detectan palabras clave"""
        palabras_clave = ["agenda", "calendario", "evento", "cita", "agendar", "recordar", "revisa hoy", "tengo algo"]
        if any(p in texto.lower() for p in palabras_clave):
            if OLLAMA_DISPONIBLE:
                threading.Thread(target=self._procesar_con_ia, args=(texto,), daemon=True).start()

    def _procesar_con_ia(self, prompt_usuario: str):
        hoy_str = datetime.now().strftime("%Y-%m-%d")
        
        system_prompt = f"""
Eres la IA gestora de la agenda de JARVIS. La fecha de hoy es {hoy_str}.
Tu objetivo es analizar la petición del usuario y responder ÚNICAMENTE en formato JSON válido.

ESTRUCTURA DEL JSON:
1. Para añadir un evento:
{{"accion": "AGREGAR", "fecha": "YYYY-MM-DD", "evento": "Texto del evento"}}

2. Para consultar o revisar eventos:
{{"accion": "CONSULTAR", "fecha": "YYYY-MM-DD" (o "TODAS")}}

3. Si la orden no tiene relación con la agenda:
{{"accion": "IGNORAR"}}

Reglas:
- Si el usuario dice "mañana", calcula la fecha sumando 1 día a {hoy_str}.
- Devuelve SOLO el código JSON, sin textos explicativos ni bloques markdown extra.
"""

        try:
            respuesta = ollama.chat(
                model=self.modelo_ollama,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt_usuario}
                ]
            )

            contenido = respuesta['message']['content'].strip()
            
            # Limpiamos posibles formatos markdown tipo ```json
            if contenido.startswith("```"):
                contenido = contenido.split("\n", 1)[1].rsplit("\n", 1)[0]
            if contenido.startswith("json"):
                contenido = contenido[4:].strip()

            datos_ia = json.loads(contenido)
            accion = datos_ia.get("accion")

            if accion == "AGREGAR":
                fecha = datos_ia.get("fecha", hoy_str)
                evento = datos_ia.get("evento", "Cita agendada")
                self.agregar_tarea(fecha=fecha, texto=evento)
                self.funcion_chat(self.nombre, f"Agendado para [{fecha}]: '{evento}'")

            elif accion == "CONSULTAR":
                fecha = datos_ia.get("fecha", hoy_str)
                if fecha == "TODAS":
                    if not self.datos_agenda:
                        self.funcion_chat(self.nombre, "La agenda está totalmente vacía.")
                    else:
                        res = "Todos tus eventos agendados:\n"
                        for f, evs in self.datos_agenda.items():
                            res += f"\n [{f}]:\n" + "\n".join([f"  • {e}" for e in evs])
                        self.funcion_chat(self.nombre, res)
                else:
                    eventos = self.datos_agenda.get(fecha, [])
                    if eventos:
                        res = f"Eventos para {fecha}:\n" + "\n".join([f"• {e}" for e in eventos])
                    else:
                        res = f"No tienes eventos registrados para {fecha}."
                    self.funcion_chat(self.nombre, res)

        except json.JSONDecodeError:
            self.funcion_chat(self.nombre, "La IA no pudo interpretar la acción en formato JSON.")
        except Exception as e:
            self.funcion_chat(self.nombre, f"Error de Ollama: {str(e)}")