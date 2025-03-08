funciona bien, pero, ahora mira este codigo:
import random
import time
import os
import pygame

# Estas stats cuando lleguen a 10, hace X accion y se resetea el contador
comida = 0
sueno = 0
gaming = 0
divertido = 0

import pygame

def reproducir_efecto_sonido(ruta_efecto_sonido):
    pygame.init()
    pygame.mixer.init()

    try:
        efecto_sonido = pygame.mixer.Sound(ruta_efecto_sonido)
        efecto_sonido.play()
        pygame.time.wait(int(efecto_sonido.get_length() * 1000))  # Esperar hasta que termine el sonido
    except pygame.error as e:
        print(f"Error al reproducir el efecto de sonido: {e}")
    finally:
        pygame.mixer.quit()
        pygame.quit()




def aleatoriedad(): 
    randomxd = random.randint(1,4)
    return randomxd

def tamagochi_normal(): 
    print("""
            /\\_/\\ 
           ( o.o )
            > ^ <
          """)
    

def tamagochi_gaming(): #1
    os.system('cls')
    for i in range(1, 3):
        os.system('cls')
        print("""
                 /\\_/\\ 
                ( W u W ) 
                > 🎮 < 
            
            """)
        time.sleep(1)
        os.system('cls')
        print("""
                 /\\_/\\ 
                ( W u W ) 
                >🎮< 
            
            """)
        time.sleep(1)
        os.system('cls')
        print("""
                 /\\_/\\ 
                ( W u W ) 
                 >🎮< 
            
            """)
        time.sleep(1)
        os.system('cls')
        print("""
                 /\\_/\\ 
                ( W u W ) 
                  >🎮< 
            
            """)
        os.system('cls')
        print("""
                 /\\_/\\ 
                ( o u o ) 
                  >🎮< 
            
            """)
        ruta_efecto = "C:/Users/cordo/Desktop/Programacion/python/Experimentos Kevin/efectos_sonido/playing.mp3"
        reproducir_efecto_sonido(ruta_efecto)
        time.sleep(1)
        
    
def tamagochi_comiendo(): #2
    os.system('cls')
    for i in range(1, 3):
        os.system('cls')
        print("""
            /\\_/\\ 
            ( o.o )
            > 🍔 <
            """)
        time.sleep(1)
        os.system('cls')
        print("""
            /\\_/\\ 
            ( ^o^ )
            > 🍔 <
            """)
        time.sleep(1)
        os.system('cls')
        print("""
            /\\_/\\ 
            ( u.u )
            >    <
            """)
        ruta_efecto = "C:/Users/cordo/Desktop/Programacion/python/Experimentos Kevin/efectos_sonido/tragando.mp3"
        reproducir_efecto_sonido(ruta_efecto)
        time.sleep(1)
        os.system('cls')
        print("""
            /\\_/\\ 
            ( .O. ) *burp
            >    <
            """)
        ruta_efecto = "C:/Users/cordo/Desktop/Programacion/python/Experimentos Kevin/efectos_sonido/burp.mp3"
        reproducir_efecto_sonido(ruta_efecto)
        
        time.sleep(1)
        


def tamagochi_mimiendo(): #3
    os.system('cls')
    for i in range(1, 3):
        os.system('cls')
        print("""
                 /\\_/\\  z 
                ( -.- )
                > ^ <
            """) 
        time.sleep(1)
        os.system('cls')
        print("""
                 /\\_/\\  zZ 
                ( -.- )
                > ^ <
            """)
        time.sleep(1)
        ruta_efecto = "C:/Users/cordo/Desktop/Programacion/python/Experimentos Kevin/efectos_sonido/roncando.mp3"
        reproducir_efecto_sonido(ruta_efecto)
        os.system('cls')
        print("""                           z
                 /\\_/\\  zZ
                ( -.- )
                > ^ <
            """)
        time.sleep(1)
        os.system('cls')
        print("""                           zZ
                 /\\_/\\  zZ
                ( -.- )
                > ^ <
            """)
        time.sleep(1)
            
    
def tamagochi_cantando(): #4
    os.system('cls')
    for i in range(1, 3):
        os.system('cls')
        print("""
                 /\\_/\\ 
                ( ^o^ )
                > ^ --🎤  
            """)
        time.sleep(1)
        os.system('cls')
        print("""
                 /\\_/\\ 
                ( ^ O^ )
                > ^  --🎤  
            """)
        ruta_efecto = "C:/Users/cordo/Desktop/Programacion/python/Experimentos Kevin/efectos_sonido/cantando.mp3"
        reproducir_efecto_sonido(ruta_efecto)

        time.sleep(1)
        os.system('cls')
        print("""
                 /\\_/\\ 
                ( ^ O^ )🎤
                > ^  --/  
            """)
        time.sleep(1)
        os.system('cls')
        print("""
                 /\\_/\\ 
                ( ^O ^ )
                > ^ --🎤  
            """)
        time.sleep(1)
        


print('Este mae es Otto, Otto es un gatito y es joto')

while True:
    os.system('cls')
    #Dando naturalidad
    tamagochi_normal()
    freeze = random.randint(1,4)
    #print(f'{freeze}') #pa ver cuanto tiemp se va esperando
    time.sleep(freeze)
    
    #stat para llevar a cabo la accion
    stat = aleatoriedad() # del 1 al 4
    

    #testing 
    #tamagochi_comiendo()
    #tamagochi_mimiendo()
    #tamagochi_gaming()
    #tamagochi_cantando()


    if stat == 1:
        gaming += 1

    elif stat == 2:
        comida += 1
    
    elif stat == 3:
        sueno += 1

    elif stat == 4:
        divertido += 1


    #puro if pa ver si ya hace algo
    if comida == 5:
        tamagochi_comiendo()
        comida = 0

    if sueno == 5:
        tamagochi_mimiendo()
        sueno = 0

    if divertido == 5:
        tamagochi_cantando()
        divertido = 0
    
    if gaming == 5:
        tamagochi_gaming()
        gaming = 0