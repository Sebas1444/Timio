import os
import shutil
import exiftool

# Rutas de Origen y Destino
Origen_nikon = "/home/redesiiucsa/fotos"
Destino_pi = "/home/redesiiucsa/original"

# Archivos de control
Contador_dir = "/home/logs"
Contador_id = os.path.join(Contador_dir, "contador.txt")
Procesados_id = os.path.join(Contador_dir, "procesados.txt")

# Crear carpetas si no existen
os.makedirs(Destino_pi, exist_ok=True)
os.makedirs(Contador_dir, exist_ok=True)

# --- Funciones de manejo de IDs ---
def get_ultimo_id():
    try:
        with open(Contador_id, "r") as f:
            contenido = f.read().strip()
            return int(contenido) if contenido.isdigit() else 0
    except FileNotFoundError:
        return 0

def guardar_id(ultimo_id):
    with open(Contador_id, "w") as f:
        f.write(str(ultimo_id))

# --- Funciones de manejo de archivos procesados ---
def cargar_procesados():
    procesados = {}
    try:
        with open(Procesados_id, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        nombre, fecha_creacion = line.split(',')
                        procesados[nombre] = fecha_creacion
                    except ValueError:
                        print(f"⚠ Línea malformada en {Procesados_id}: {line}, ignorando...")
    except FileNotFoundError:
        pass
    return procesados

def guardar_procesados(procesados):
    with open(Procesados_id, "w") as f:
        for nombre, fecha in procesados.items():
            f.write(f"{nombre},{fecha}\n")

# --- Función para obtener metadatos EXIF ---
def get_fechas_exif(rutas_archivos):
    fechas = {}
    with exiftool.ExifTool() as et:

      try:
        metadata = et.get_metadata_batch(rutas_archivos)
      except AttributeError as e:
        print(f"Error al llamar a get_metadata_batch: {e}")
        print(f"Probablemente pyexiftool no está instalado correctamente o no es accesible.")
        return {} # Retornamos un diccionario vacío para que el script pueda continuar

      for d in metadata:
          if "SourceFile" in d:
              nombre = os.path.basename(d["SourceFile"])
              fecha = d.get("EXIF:DateTimeOriginal") or d.get("File:CreateDate")
              if fecha:
                  fechas[nombre] = fecha
              else:
                  print(f"⚠ No se encontró fecha en {nombre}, ignorando...")
          else:
              print(f"⚠ Archivo sin 'SourceFile' en metadatos, ignorando...")
    return fechas

# --- Función principal de copia ---
def copiar_id():
    viejo_id = get_ultimo_id()
    procesados = cargar_procesados()
    nuevos_procesados = procesados.copy()

    print(f"Buscando imágenes en: {Origen_nikon}")
    print(f" Archivos ya procesados: {len(procesados)}")

    for root, _, files in os.walk(Origen_nikon):
        print(f"Explorando: {root}, Archivos encontrados: {len(files)}")
        archivos_jpg = [os.path.join(root, f) for f in files if f.lower().endswith((".jpg", ".jpeg", ".JPG", ".JPEG"))]
        fechas_creacion = get_fechas_exif(archivos_jpg)

        for file, fecha_creacion in fechas_creacion.items():
            if not fecha_creacion:
                continue

            if file in procesados and procesados[file] == fecha_creacion:
                print(f" {file} ya fue procesado, ignorando...")
                continue

            viejo_id += 1
            dest_nombre = f"Arasunu_{viejo_id:03d}_{fecha_creacion.replace(':', '').replace(' ', '')}.jpg"
            dest = os.path.join(Destino_pi, dest_nombre)

            try:
                shutil.copy2(os.path.join(root, file), dest)
                print(f"Copiado: {dest}")
                nuevos_procesados[file] = fecha_creacion
            except Exception as e:
                print(f"⚠ Error al copiar {file}: {e}")

    guardar_procesados(nuevos_procesados)
    guardar_id(viejo_id)

# --- Añadimos líneas de depuración ---
import sys
import os

print(f"Ruta de pyexiftool (si existe): {getattr(exiftool, '__file__', 'No encontrado')}")
print(f"PATH: {os.environ.get('PATH')}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
print(f"Versión de Python: {sys.version}")

if __name__ == "__main__":
    copiar_id()