#Importamos las librerías necesarias para el funcionamiento
import ollama
import time
#Importamos funciones de otros bloques de código
#from archivo import funcion
from memoria import guardar_memoria, acceso_memoria_inteligente, guardar_indice

#DEFINIMOS VARIABLES DEL PROYECTO
modelo = 'gemma4:e4b'
pregunta = ""
mensaje = []
respuesta = ""

def chat():
    print("\n" + "="*40)
    print("Hola señor, estoy listo para servirle")

    while True:
        #Le pedimos un mensaje al usuario
        pregunta = str(input("Usuario: "))

        #Esto evita el error de darle a enter por accidente
        if pregunta == "":
            continue

        #Salir del asistente
        if pregunta.lower() in ['salir', 'apágate', 'desconectar', 'adios']:
            print("Entendido Señor. Que tenga un buen día.")
            break 
        
        #Le indicamos a la IA como debe responder
        mensaje.append({"role": "user",
                         "content": f"{pregunta}"
                         })

        try:
            #Aquí se lanza el mensaje
            respuesta = ollama.chat(model=modelo, messages=mensaje)
            
            #Imprimimos el mensaje
            print(respuesta.message.content)
        
        #Comprobamos si hay error y lo mandamos
        except Exception as error:
            print(f"El código falló debido a: {error}")

        #Guardamos la memoria de la conversación
        guardar_memoria(pregunta, respuesta.message.content)
if __name__ == "__main__":
    guardar_indice()
    chat()