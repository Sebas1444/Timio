import os
import logging
import time
from PIL import Image
import fnmatch

# Configuración centralizada de calidad
def obtener_calidad():
    return 85  

def configurar_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def compresor_imagen(origen_path, destino_path):
    try:
        calidad = obtener_calidad()
        imagen = Image.open(origen_path).convert('RGB')
        imagen.save(destino_path, 'WebP', quality=calidad, optimize=True)
        logging.info(f" Imagen comprimida: {os.path.basename(origen_path)} -> {os.path.basename(destino_path)}")
    except Exception as e:
        logging.error(f" Error al comprimir {origen_path}: {e}")

def obtener_imagenes_existentes(destino_folder):
    return {os.path.splitext(f)[0] for f in os.listdir(destino_folder) if fnmatch.fnmatch(f, '*.webp')}

def procesar_imagenes(rutas):
    while True:
        origen_folder = rutas['origen']
        destino_folder = rutas['destino']
        
        os.makedirs(destino_folder, exist_ok=True)
        imagenes_existentes = obtener_imagenes_existentes(destino_folder)
        
        for archivo in os.listdir(origen_folder):
            if archivo.lower().endswith(('.jpg', '.jpeg')):
                nombre_base = os.path.splitext(archivo)[0]
                archivo_origen = os.path.join(origen_folder, archivo)
                archivo_destino = os.path.join(destino_folder, f"{nombre_base}.webp")
                
                if nombre_base in imagenes_existentes:
                    logging.info(f" Imagen ya comprimida, ignorando: {archivo}")
                else:
                    compresor_imagen(archivo_origen, archivo_destino)
        
        time.sleep(2)  # Espera 2 segundos antes de volver a verificar

if __name__ == "__main__":
    configurar_logging()
    rutas = {
        'origen': 'timio/nikon/original',
        'destino': 'timio/nikon/webp'
    }
    procesar_imagenes(rutas)
