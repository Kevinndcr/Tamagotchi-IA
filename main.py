import tkinter as tk
import threading
import time
import os
import sys

# Configurar logging para depuración
print("Iniciando aplicación de mascota virtual...")
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

# API key configuration - better to use environment variables
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCGb5T6RNt_MOQTJQVq8wQmWIRJ3Jwm9Ts")
print(f"API Key configurada (primeros 5 caracteres): {API_KEY[:5]}...")

class MascotaVirtual:
    def __init__(self, root):
        self.root = root
        self.root.title("Mascota Virtual - Pez ASCII")
        self.root.geometry("500x500")
        
        # Configurar el cliente de Google Gemini
        if GEMINI_AVAILABLE:
            try:
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
        
        # Crear ASCII art del pez
        self.ascii_pez = '''
          ><(((º>
        '''
        
        # Crear elementos de la interfaz
        self.frame = tk.Frame(root)
        self.frame.pack(fill="both", expand=True)
        
        self.pez_label = tk.Label(self.frame, text=self.ascii_pez, font=("Courier", 20))
        self.pez_label.pack(pady=20)
        
        self.texto_entrada = tk.StringVar()
        self.texto_entrada.set("...")
        self.entrada_label = tk.Label(self.frame, textvariable=self.texto_entrada)
        self.entrada_label.pack(pady=10)
        
        self.texto_respuesta = tk.StringVar()
        self.texto_respuesta.set("...")
        self.respuesta_label = tk.Label(self.frame, textvariable=self.texto_respuesta)
        self.respuesta_label.pack(pady=10)
        
        # Añadir entrada de texto como alternativa al reconocimiento de voz
        self.entrada_texto = tk.Entry(self.frame, width=40)
        self.entrada_texto.pack(pady=10)
        self.entrada_texto.bind("<Return>", self.procesar_texto_entrada)
        
        # Botones
        self.boton_frame = tk.Frame(self.frame)
        self.boton_frame.pack(pady=10)
        
        self.boton_hablar = tk.Button(self.boton_frame, text="Hablar con la mascota", 
                                     command=self.iniciar_escucha)
        self.boton_hablar.pack(side=tk.LEFT, padx=5)
        if not SPEECH_AVAILABLE:
            self.boton_hablar.config(state=tk.DISABLED)
        
        self.boton_enviar = tk.Button(self.boton_frame, text="Enviar texto", 
                                     command=lambda: self.procesar_texto_entrada(None))
        self.boton_enviar.pack(side=tk.LEFT, padx=5)
        
        self.boton_salir = tk.Button(self.boton_frame, text="Salir", 
                                    command=self.root.destroy)
        self.boton_salir.pack(side=tk.LEFT, padx=5)
        
        self.estado_label = tk.Label(self.frame, text="Listo para interactuar")
        self.estado_label.pack(pady=10)
        
        # Mostrar advertencias si hay módulos faltantes
        self.mostrar_estado_dependencias()
    
    def mostrar_estado_dependencias(self):
        """Muestra advertencias sobre dependencias faltantes"""
        mensajes = []
        
        if not SPEECH_AVAILABLE:
            mensajes.append("Reconocimiento de voz no disponible. Usa la entrada de texto.")
        
        if not TTS_AVAILABLE:
            mensajes.append("Síntesis de voz no disponible. Las respuestas serán solo texto.")
        
        if not GEMINI_AVAILABLE:
            mensajes.append("API de Gemini no disponible. La mascota no podrá responder.")
        elif self.gemini_error:
            mensajes.append(f"Error con Gemini: {self.gemini_error}")
        elif self.modelo is None:
            mensajes.append("No se pudo inicializar el modelo de Gemini.")
        
        if mensajes:
            mensaje_final = "\n".join(mensajes)
            self.estado_label.config(text=mensaje_final)
    
    def procesar_texto_entrada(self, event):
        """Procesa el texto ingresado manualmente"""
        texto = self.entrada_texto.get().strip()
        if texto:
            self.texto_entrada.set(f"Tú: {texto}")
            self.entrada_texto.delete(0, tk.END)
            threading.Thread(target=self.obtener_respuesta_ia, args=(texto,)).start()
    
    def iniciar_escucha(self):
        if not self.escuchando and SPEECH_AVAILABLE:
            self.escuchando = True
            self.estado_label.config(text="Escuchando...")
            threading.Thread(target=self.escuchar).start()
    
    def escuchar(self):
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
        self.estado_label.config(text="Pensando...")
        
        if not GEMINI_AVAILABLE or self.modelo is None:
            self.texto_respuesta.set("Pez: Lo siento, no puedo responder sin la API de Gemini.")
            self.estado_label.config(text="API de Gemini no disponible")
            return
        
        try:
            # Personalizar el prompt para que el modelo actúe como un pez mascota
            prompt = """
            Eres un pez mascota virtual llamado Burbujas. Tienes una personalidad amigable, 
            divertida y juguetona. Tus respuestas deben ser breves (máximo 2 oraciones) y
            ocasionalmente puedes hacer referencias a la vida acuática.
            
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
            
            # Limpiar la respuesta si es necesario (a veces Gemini incluye comillas o formatos extraños)
            texto_respuesta = texto_respuesta.strip('"\'')
            
            self.texto_respuesta.set(f"Pez: {texto_respuesta}")
            
            # Animación simple del pez "hablando"
            self.animar_pez()
            
            # Leer respuesta en voz alta si está disponible
            if TTS_AVAILABLE:
                threading.Thread(target=self.hablar, args=(texto_respuesta,)).start()
            
            self.estado_label.config(text="Listo para interactuar")
            
        except Exception as e:
            error_msg = str(e)
            self.texto_respuesta.set(f"Pez: Glub glub... (Hubo un problema)")
            self.estado_label.config(text=f"Error al obtener respuesta: {error_msg}")
            print(f"Error detallado: {error_msg}")
    
    def animar_pez(self):
        # Animación simple alternando entre dos frames
        ascii_pez_hablando = '''
          ><(((O>
        '''
        for _ in range(3):
            self.pez_label.config(text=ascii_pez_hablando)
            self.root.update()
            time.sleep(0.3)
            self.pez_label.config(text=self.ascii_pez)
            self.root.update()
            time.sleep(0.3)
    
    def hablar(self, texto):
        if TTS_AVAILABLE:
            try:
                self.engine.say(texto)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Error en síntesis de voz: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MascotaVirtual(root)
    root.mainloop()