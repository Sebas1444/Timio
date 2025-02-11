import os
import logging
from PIL import Image
import fnmatch

# Configuración centralizada de calidad
def obtener_calidad():
    return 85  # Cambia este valor para afectar todo el proceso

def configurar_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def compresor_imagen(origen_path, destino_path):
    try:
        calidad = obtener_calidad()  # Se obtiene la calidad de una sola función
        imagen = Image.open(origen_path).convert('RGB')
        imagen.save(destino_path, 'WebP', quality=calidad, optimize=True)
        logging.info(f"Imagen comprimida: {os.path.basename(origen_path)} -> {os.path.basename(destino_path)}")
    except Exception as e:
        logging.error(f"Error al comprimir {origen_path}: {e}")

def obtener_imagenes_existentes(destino_folder):
    return {os.path.splitext(f)[0] for f in os.listdir(destino_folder) if fnmatch.fnmatch(f, '*.webp')}

def procesar_imagenes(rutas):
    origen_folder = rutas['origen']
    destino_folder = rutas['destino']
    
    os.makedirs(destino_folder, exist_ok=True)  # Asegurar que la carpeta de destino exista
    imagenes_existentes = obtener_imagenes_existentes(destino_folder)
    
    for archivo in os.listdir(origen_folder):
        if archivo.lower().endswith('.jpg'):
            nombre_base = os.path.splitext(archivo)[0]
            archivo_origen = os.path.join(origen_folder, archivo)
            archivo_destino = os.path.join(destino_folder, f"{nombre_base}.webp")
            
            if nombre_base in imagenes_existentes:
                logging.info(f"Imagen ya comprimida, ignorando: {archivo}")
            else:
                compresor_imagen(archivo_origen, archivo_destino)

if __name__ == "__main__":
    configurar_logging()
    rutas = {
        'origen': r'/home/redesiiucsa/original',
        'destino': r'/home/redesiiucsa/webp'
    }
    procesar_imagenes(rutas)
