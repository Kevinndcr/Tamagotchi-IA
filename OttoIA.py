import tkinter as tk
import threading
import time
import os
import sys
import random
import pygame
from tkinter import ttk, messagebox

# Configurar logging para depuración
print("Iniciando aplicación de Tamagotchi Inteligente...")
print(f"Python version: {sys.version}")

# Try to import optional dependencies with helpful error messages
try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
    print("Speech recognition disponible")
except ImportError:
    SPEECH_AVAILABLE = False
    print("Speech recognition package not found. Install with: pip install SpeechRecognition")

try:
    import pyttsx3
    TTS_AVAILABLE = True
    print("Text-to-speech disponible")
except ImportError:
    TTS_AVAILABLE = False
    print("Text-to-speech package not found. Install with: pip install pyttsx3")

try:
    import google.generativeai as genai
    print(f"Google Generative AI version: {genai.__version__}")
    GEMINI_AVAILABLE = True
    print("Google Generative AI disponible")
except ImportError:
    GEMINI_AVAILABLE = False
    print("Google Generative AI package not found. Install with: pip install google-generativeai")

# API key - mejor usar variables de entorno
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCGb5T6RNt_MOQTJQVq8wQmWIRJ3Jwm9Ts")
if API_KEY:
    print(f"API Key configurada (primeros 5 caracteres): {API_KEY[:5]}...")
else:
    print("API Key no configurada. Por favor, configura la variable de entorno GEMINI_API_KEY")

# Inicializar pygame para los efectos de sonido
pygame.mixer.init()

class TamagotchiInteligente:
    def __init__(self, root):
        self.root = root
        self.root.title("Otto - Tamagotchi Inteligente")
        self.root.geometry("600x650")
        self.root.configure(bg="#f0f0f0")
        
        # Estados iniciales
        self.comida = 0
        self.sueno = 0
        self.gaming = 0
        self.divertido = 0
        self.aburrimiento = 0
        self.ultima_accion = time.time()
        self.animacion_en_progreso = False
        self.modo_automatico = True
        
        # Configurar el cliente de Google Gemini
        if GEMINI_AVAILABLE:
            try:
                if API_KEY:
                    genai.configure(api_key=API_KEY)
                    
                    # Listar modelos disponibles
                    try:
                        print("Modelos disponibles:")
                        for m in genai.list_models():
                            if 'generateContent' in m.supported_generation_methods:
                                print(f" - {m.name}")
                        
                        # Intentar con diferentes modelos en orden de preferencia
                        model_names = ["gemini-pro", "gemini-1.0-pro", "gemini-1.5-pro"]
                        self.modelo = None
                        
                        for model_name in model_names:
                            try:
                                self.modelo = genai.GenerativeModel(model_name)
                                # Prueba simple para verificar que funciona
                                test_response = self.modelo.generate_content("Hola")
                                print(f"Modelo seleccionado: {model_name}")
                                break
                            except Exception as model_error:
                                print(f"Error con modelo {model_name}: {model_error}")
                        
                        if self.modelo is None:
                            raise Exception("No se pudo encontrar un modelo compatible")
                            
                        self.gemini_error = None
                    except Exception as list_error:
                        print(f"Error al listar modelos: {list_error}")
                        # Si falla al listar, intentar directamente con gemini-pro
                        self.modelo = genai.GenerativeModel("gemini-pro")
                        self.gemini_error = None
                else:
                    self.gemini_error = "API Key no configurada"
                    self.modelo = None                        
            except Exception as e:
                self.gemini_error = str(e)
                self.modelo = None
                print(f"Error al configurar Gemini: {e}")
        
        # Configurar reconocimiento de voz
        if SPEECH_AVAILABLE:
            self.recognizer = sr.Recognizer()
        
        # Configurar síntesis de voz
        if TTS_AVAILABLE:
            self.engine = pyttsx3.init()
        
        # Variable para controlar si está escuchando
        self.escuchando = False
        
        # Crear ASCII art del tamagotchi (estado normal)
        self.ascii_normal = '''
             /\\_/\\ 
            ( o.o )
             > ^ <
        '''
        
        # Crear elementos de la interfaz
        self.crear_interfaz()
        
        # Iniciar el ciclo de vida del tamagotchi
        if self.modo_automatico:
            threading.Thread(target=self.ciclo_vida, daemon=True).start()
        
        # Mostrar advertencias si hay módulos faltantes
        self.mostrar_estado_dependencias()
    
    def crear_interfaz(self):
        """Crea todos los elementos de la interfaz gráfica"""
        # Frame principal
        self.frame_principal = tk.Frame(self.root, bg="#f0f0f0")
        self.frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Frame para el tamagotchi
        self.frame_tamagotchi = tk.Frame(self.frame_principal, bg="#f0f0f0", relief=tk.RIDGE, bd=2)
        self.frame_tamagotchi.pack(pady=10)
        
        # Label para mostrar el ASCII art
        self.tamagotchi_label = tk.Label(self.frame_tamagotchi, text=self.ascii_normal, 
                                         font=("Courier", 24), bg="#f0f0f0", padx=20, pady=20)
        self.tamagotchi_label.pack()
        
        # Frame para las estadísticas
        self.frame_stats = tk.Frame(self.frame_principal, bg="#f0f0f0")
        self.frame_stats.pack(pady=10, fill="x")
        
        # Barras de progreso para las estadísticas
        self.crear_barras_progreso()
        
        # Frame para la interacción
        self.frame_interaccion = tk.Frame(self.frame_principal, bg="#f0f0f0")
        self.frame_interaccion.pack(pady=10, fill="x")
        
        # Elementos para la interacción con IA
        self.texto_entrada = tk.StringVar()
        self.texto_entrada.set("...")
        self.entrada_label = tk.Label(self.frame_interaccion, textvariable=self.texto_entrada, 
                                     bg="#f0f0f0", font=("Arial", 10))
        self.entrada_label.pack(pady=5)
        
        self.texto_respuesta = tk.StringVar()
        self.texto_respuesta.set("...")
        self.respuesta_label = tk.Label(self.frame_interaccion, textvariable=self.texto_respuesta, 
                                       bg="#f0f0f0", font=("Arial", 10, "bold"))
        self.respuesta_label.pack(pady=5)
        
        # Entrada de texto
        self.entrada_texto = tk.Entry(self.frame_interaccion, width=50)
        self.entrada_texto.pack(pady=10)
        self.entrada_texto.bind("<Return>", self.procesar_texto_entrada)
        
        # Frame para botones de interacción
        self.frame_botones = tk.Frame(self.frame_interaccion, bg="#f0f0f0")
        self.frame_botones.pack(pady=10)
        
        # Botones principales de interacción
        self.boton_hablar = tk.Button(self.frame_botones, text="Hablar", 
                                     command=self.iniciar_escucha, width=10,
                                     bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.boton_hablar.pack(side=tk.LEFT, padx=5)
        if not SPEECH_AVAILABLE:
            self.boton_hablar.config(state=tk.DISABLED)
        
        self.boton_enviar = tk.Button(self.frame_botones, text="Enviar", 
                                     command=lambda: self.procesar_texto_entrada(None), width=10,
                                     bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
        self.boton_enviar.pack(side=tk.LEFT, padx=5)
        
        # Frame para botones de acción directa
        self.frame_acciones = tk.Frame(self.frame_interaccion, bg="#f0f0f0")
        self.frame_acciones.pack(pady=10)
        
        # Botones de acción directa
        acciones = [
            ("Alimentar", self.accion_alimentar, "#FF9800"),
            ("Jugar", self.accion_jugar, "#E91E63"),
            ("Dormir", self.accion_dormir, "#9C27B0"),
            ("Cantar", self.accion_cantar, "#3F51B5")
        ]
        
        for texto, comando, color in acciones:
            boton = tk.Button(self.frame_acciones, text=texto, command=comando, 
                             bg=color, fg="white", width=8, font=("Arial", 9, "bold"))
            boton.pack(side=tk.LEFT, padx=5)
        
        # Botón para activar/desactivar modo automático
        self.var_automatico = tk.BooleanVar(value=self.modo_automatico)
        self.check_automatico = tk.Checkbutton(self.frame_acciones, text="Modo automático", 
                                              variable=self.var_automatico, 
                                              command=self.toggle_modo_automatico,
                                              bg="#f0f0f0", font=("Arial", 9))
        self.check_automatico.pack(side=tk.LEFT, padx=15)
        
        # Estado y mensajes
        self.estado_label = tk.Label(self.frame_principal, text="Otto está listo para interactuar", 
                                    bg="#f0f0f0", font=("Arial", 9, "italic"))
        self.estado_label.pack(pady=5)
    
    def crear_barras_progreso(self):
        """Crea las barras de progreso para las estadísticas"""
        # Estadísticas a mostrar
        stats = [
            ("Hambre", "comida", "#FF9800"),
            ("Sueño", "sueno", "#9C27B0"),
            ("Diversión", "divertido", "#3F51B5"),
            ("Gaming", "gaming", "#E91E63")
        ]
        
        # Crear cada barra con su etiqueta
        for i, (nombre, atributo, color) in enumerate(stats):
            frame = tk.Frame(self.frame_stats, bg="#f0f0f0")
            frame.pack(fill="x", pady=2)
            
            label = tk.Label(frame, text=f"{nombre}:", width=10, anchor="w", bg="#f0f0f0")
            label.pack(side=tk.LEFT, padx=5)
            
            barra = ttk.Progressbar(frame, length=400, mode="determinate", 
                                   maximum=5, value=getattr(self, atributo))
            barra.pack(side=tk.LEFT, padx=5, fill="x", expand=True)
            
            # Guardar referencia a la barra
            setattr(self, f"barra_{atributo}", barra)
    
    def actualizar_barras(self):
        """Actualiza las barras de progreso con los valores actuales"""
        self.barra_comida["value"] = self.comida
        self.barra_sueno["value"] = self.sueno
        self.barra_divertido["value"] = self.divertido
        self.barra_gaming["value"] = self.gaming
        self.root.update_idletasks()
    
    def mostrar_estado_dependencias(self):
        """Muestra advertencias sobre dependencias faltantes"""
        mensajes = []
        
        if not SPEECH_AVAILABLE:
            mensajes.append("Reconocimiento de voz no disponible. Usa la entrada de texto.")
        
        if not TTS_AVAILABLE:
            mensajes.append("Síntesis de voz no disponible. Las respuestas serán solo texto.")
        
        if not GEMINI_AVAILABLE:
            mensajes.append("API de Gemini no disponible. Otto no podrá responder.")
        elif self.gemini_error:
            mensajes.append(f"Error con Gemini: {self.gemini_error}")
        elif self.modelo is None:
            mensajes.append("No se pudo inicializar el modelo de Gemini.")
        
        if mensajes:
            mensaje_final = "\n".join(mensajes)
            self.estado_label.config(text=mensaje_final)
    
    def reproducir_efecto_sonido(self, ruta_efecto_sonido):
        """Reproduce un efecto de sonido"""
        try:
            # Verifica si el archivo existe
            if not os.path.exists(ruta_efecto_sonido):
                print(f"Archivo de sonido no encontrado: {ruta_efecto_sonido}")
                return
                
            efecto_sonido = pygame.mixer.Sound(ruta_efecto_sonido)
            pygame.mixer.Sound.play(efecto_sonido)
        except Exception as e:
            print(f"Error al reproducir el efecto de sonido: {e}")
    
    def procesar_texto_entrada(self, event):
        """Procesa el texto ingresado manualmente"""
        texto = self.entrada_texto.get().strip()
        if texto:
            self.texto_entrada.set(f"Tú: {texto}")
            self.entrada_texto.delete(0, tk.END)
            threading.Thread(target=self.obtener_respuesta_ia, args=(texto,)).start()
    
    def iniciar_escucha(self):
        """Inicia el proceso de escucha por micrófono"""
        if not self.escuchando and SPEECH_AVAILABLE:
            self.escuchando = True
            self.estado_label.config(text="Escuchando...")
            threading.Thread(target=self.escuchar).start()
    
    def escuchar(self):
        """Captura audio y lo convierte a texto"""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5)
                
            texto = self.recognizer.recognize_google(audio, language="es-ES")
            self.texto_entrada.set(f"Tú: {texto}")
            
            # Llamada a la API de IA para obtener respuesta
            threading.Thread(target=self.obtener_respuesta_ia, args=(texto,)).start()
            
        except sr.WaitTimeoutError:
            self.estado_label.config(text="No se detectó audio. Intenta de nuevo o usa el texto.")
        except sr.UnknownValueError:
            self.estado_label.config(text="No se pudo entender el audio. Intenta de nuevo o usa el texto.")
        except Exception as e:
            self.estado_label.config(text=f"Error: {str(e)}")
        finally:
            self.escuchando = False
    
    def obtener_respuesta_ia(self, texto):
        """Obtiene una respuesta de la IA para el texto ingresado"""
        self.estado_label.config(text="Otto está pensando...")
        
        if not GEMINI_AVAILABLE or self.modelo is None:
            self.texto_respuesta.set("Otto: Lo siento, no puedo responder sin la API de Gemini.")
            self.estado_label.config(text="API de Gemini no disponible")
            return
        
        try:
            # Personalizar el prompt para que el modelo actúe como Otto
            prompt = """
            Eres un gato mascota virtual llamado Otto. Tienes una personalidad juguetona, 
            divertida y un poco traviesa. Tus respuestas deben ser breves (máximo 2 oraciones) y
            ocasionalmente puedes hacer referencias a la vida de un gato (maullar, lamer patas, etc).
            Actúa como si fueras un gato real que puede hablar.
            
            Responde al siguiente mensaje de tu dueño:
            """
            
            # Enviar la solicitud a Gemini
            respuesta = self.modelo.generate_content(
                prompt + texto,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=100,
                    temperature=0.7
                )
            )
            
            texto_respuesta = respuesta.text
            
            # Limpiar la respuesta si es necesario
            texto_respuesta = texto_respuesta.strip('"\'')
            
            self.texto_respuesta.set(f"Otto: {texto_respuesta}")
            
            # Animación de Otto "hablando"
            self.animar_hablando()
            
            # Leer respuesta en voz alta si está disponible
            if TTS_AVAILABLE:
                threading.Thread(target=self.hablar, args=(texto_respuesta,)).start()
            
            self.estado_label.config(text="Otto está listo para interactuar")
            
            # Restablecer el contador de aburrimiento
            self.aburrimiento = 0
            self.ultima_accion = time.time()
            
        except Exception as e:
            error_msg = str(e)
            self.texto_respuesta.set(f"Otto: Miau... (Hubo un problema)")
            self.estado_label.config(text=f"Error al obtener respuesta: {error_msg}")
            print(f"Error detallado: {error_msg}")
    
    def hablar(self, texto):
        """Reproduce el texto con síntesis de voz"""
        if TTS_AVAILABLE:
            try:
                self.engine.say(texto)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Error en síntesis de voz: {e}")
    
    def animar_hablando(self):
        """Animación simple de Otto hablando"""
        if self.animacion_en_progreso:
            return
            
        self.animacion_en_progreso = True
        
        ascii_hablando = '''
             /\\_/\\ 
            ( ^o^ )
             > ^ <
        '''
        
        ascii_normal = self.ascii_normal
        
        def animar():
            for _ in range(3):
                self.tamagotchi_label.config(text=ascii_hablando)
                time.sleep(0.3)
                self.tamagotchi_label.config(text=ascii_normal)
                time.sleep(0.3)
            self.animacion_en_progreso = False
        
        threading.Thread(target=animar).start()
    
    # Métodos para las acciones directas
    def accion_alimentar(self):
        """Acción de alimentar al tamagotchi"""
        if self.animacion_en_progreso:
            return
            
        self.animacion_en_progreso = True
        threading.Thread(target=self.tamagotchi_comiendo).start()
        self.comida = 0
        self.ultima_accion = time.time()
    
    def accion_jugar(self):
        """Acción de jugar con el tamagotchi"""
        if self.animacion_en_progreso:
            return
            
        self.animacion_en_progreso = True
        threading.Thread(target=self.tamagotchi_gaming).start()
        self.gaming = 0
        self.ultima_accion = time.time()
    
    def accion_dormir(self):
        """Acción de poner a dormir al tamagotchi"""
        if self.animacion_en_progreso:
            return
            
        self.animacion_en_progreso = True
        threading.Thread(target=self.tamagotchi_mimiendo).start()
        self.sueno = 0
        self.ultima_accion = time.time()
    
    def accion_cantar(self):
        """Acción de hacer cantar al tamagotchi"""
        if self.animacion_en_progreso:
            return
            
        self.animacion_en_progreso = True
        threading.Thread(target=self.tamagotchi_cantando).start()
        self.divertido = 0
        self.ultima_accion = time.time()
    
    def toggle_modo_automatico(self):
        """Activa o desactiva el modo automático"""
        self.modo_automatico = self.var_automatico.get()
        
        if self.modo_automatico and not any(t.name == "ciclo_vida" for t in threading.enumerate()):
            threading.Thread(target=self.ciclo_vida, daemon=True, name="ciclo_vida").start()
            self.estado_label.config(text="Modo automático activado")
        else:
            self.estado_label.config(text="Modo automático desactivado")
    
    # Animaciones del tamagotchi
    def tamagotchi_normal(self):
        """Muestra el estado normal del tamagotchi"""
        self.tamagotchi_label.config(text=self.ascii_normal)
    
    def tamagotchi_gaming(self):
        """Animación del tamagotchi jugando"""
        ascii_frames = [
            '''
             /\\_/\\ 
            ( W u W ) 
            > 🎮 < 
            ''',
            '''
             /\\_/\\ 
            ( W u W ) 
            >🎮< 
            ''',
            '''
             /\\_/\\ 
            ( W u W ) 
            >🎮< 
            ''',
            '''
             /\\_/\\ 
            ( W u W ) 
             >🎮< 
            ''',
            '''
             /\\_/\\ 
            ( o u o ) 
             >🎮< 
            '''
        ]
        
        # Ruta del efecto de sonido (usar ruta relativa o absoluta según configuración)
        # Aquí usamos una ruta genérica que puede adaptarse
        ruta_efecto = os.path.join("efectos_sonido", "playing.mp3")
        
        for _ in range(2):
            for frame in ascii_frames:
                if not self.animacion_en_progreso:
                    break
                self.tamagotchi_label.config(text=frame)
                time.sleep(0.4)
            
            # Intentar reproducir el sonido
            try:
                self.reproducir_efecto_sonido(ruta_efecto)
            except:
                pass
        
        self.tamagotchi_normal()
        self.animacion_en_progreso = False
    
    def tamagotchi_comiendo(self):
        """Animación del tamagotchi comiendo"""
        ascii_frames = [
            '''
             /\\_/\\ 
            ( o.o )
            > 🍔 <
            ''',
            '''
             /\\_/\\ 
            ( ^o^ )
            > 🍔 <
            ''',
            '''
             /\\_/\\ 
            ( u.u )
            >    <
            ''',
            '''
             /\\_/\\ 
            ( .O. ) *burp
            >    <
            '''
        ]
        
        # Rutas de efectos de sonido
        ruta_tragando = os.path.join("efectos_sonido", "tragando.mp3")
        ruta_burp = os.path.join("efectos_sonido", "burp.mp3")
        
        for _ in range(2):
            for i, frame in enumerate(ascii_frames):
                if not self.animacion_en_progreso:
                    break
                self.tamagotchi_label.config(text=frame)
                
                # Efectos de sonido específicos
                if i == 2:
                    try:
                        self.reproducir_efecto_sonido(ruta_tragando)
                    except:
                        pass
                elif i == 3:
                    try:
                        self.reproducir_efecto_sonido(ruta_burp)
                    except:
                        pass
                
                time.sleep(0.8)
        
        self.tamagotchi_normal()
        self.animacion_en_progreso = False
    
    def tamagotchi_mimiendo(self):
        """Animación del tamagotchi durmiendo"""
        ascii_frames = [
            '''
             /\\_/\\  z 
            ( -.- )
            > ^ <
            ''',
            '''
             /\\_/\\  zZ 
            ( -.- )
            > ^ <
            ''',
            '''
                      z
             /\\_/\\  zZ
            ( -.- )
            > ^ <
            ''',
            '''
                      zZ
             /\\_/\\  zZ
            ( -.- )
            > ^ <
            '''
        ]
        
        # Ruta del efecto de sonido
        ruta_ronquido = os.path.join("efectos_sonido", "roncando.mp3")
        
        for _ in range(2):
            for i, frame in enumerate(ascii_frames):
                if not self.animacion_en_progreso:
                    break
                self.tamagotchi_label.config(text=frame)
                
                # Reproducir ronquido en el segundo frame
                if i == 1:
                    try:
                        self.reproducir_efecto_sonido(ruta_ronquido)
                    except:
                        pass
                
                time.sleep(0.8)
        
        self.tamagotchi_normal()
        self.animacion_en_progreso = False
    
    def tamagotchi_cantando(self):
        """Animación del tamagotchi cantando"""
        ascii_frames = [
            '''
             /\\_/\\ 
            ( ^o^ )
            > ^ --🎤  
            ''',
            '''
             /\\_/\\ 
            ( ^ O^ )
            > ^  --🎤  
            ''',
            '''
             /\\_/\\ 
            ( ^ O^ )🎤
            > ^  --/  
            ''',
            '''
             /\\_/\\ 
            ( ^O ^ )
            > ^ --🎤  
            '''
        ]
        
        # Ruta del efecto de sonido
        ruta_canto = os.path.join("efectos_sonido", "cantando.mp3")
        
        for _ in range(2):
            for i, frame in enumerate(ascii_frames):
                if not self.animacion_en_progreso:
                    break
                self.tamagotchi_label.config(text=frame)
                
                # Reproducir canto en el segundo frame
                if i == 1:
                    try:
                        self.reproducir_efecto_sonido(ruta_canto)
                    except:
                        pass
                
                time.sleep(0.8)
        
        self.tamagotchi_normal()
        self.animacion_en_progreso = False
    
    def ciclo_vida(self):
        """Ciclo de vida automático del tamagotchi"""
        while self.modo_automatico:
            # Solo ejecutar si no hay una animación en curso
            if not self.animacion_en_progreso:
                # Incrementar valores periódicamente
                tiempo_actual = time.time()
                tiempo_transcurrido = tiempo_actual - self.ultima_accion
                
                # Si han pasado más de 20 segundos desde la última acción
                if tiempo_transcurrido > 20:
                    # Incrementar aleatoriamente una necesidad
                    necesidad = random.randint(1, 4)
                    
                    if necesidad == 1:
                        self.comida = min(self.comida + 1, 5)
                    elif necesidad == 2:
                        self.sueno = min(self.sueno + 1, 5)
                    elif necesidad == 3:
                        self.gaming = min(self.gaming + 1, 5)
                    elif necesidad == 4:
                        self.divertido = min(self.divertido + 1, 5)
                    
                    # Actualizar la interfaz
                    self.actualizar_barras()
                    
                    # Incrementar contador de aburrimiento
                    self.aburrimiento += 1
                    
                    # Si alguna necesidad llega a 5, realizar la acción correspondiente
                    if self.comida >= 5:
                        self.accion_alimentar()
                    elif self.sueno >= 5:
                        self.accion_dormir()
                    elif self.gaming >= 5:
                        self.accion_jugar()
                    elif self.divertido >= 5:
                        self.accion_cantar()
                    # Si está aburrido, hacer algo aleatorio
                    elif self.aburrimiento >= 3:
                        accion = random.randint(1, 4)
                        if accion == 1:
                            self.accion_alimentar()
                        elif accion == 2:
                            self.accion_dormir()
                        elif accion == 3:
                            self.accion_jugar()
                        elif accion == 4:
                            self.accion_cantar()
                        
                        self.aburrimiento = 0
                    
                    # Resetear el temporizador
                    self.ultima_accion = tiempo_actual
            
            # Evitar consumo excesivo de CPU
            time.sleep(1)

# Función principal
def main():
    root = tk.Tk()
    app = TamagotchiInteligente(root)
    root.mainloop()

if __name__ == "__main__":
    main()