import os
import shutil
import time


# Rutas de Origen y Destino
Origen_nikon = "/home/redesiiucsa/fotos"  # Carpeta de origen
Destino_pi = "/home/redesiiucsa/original"  # Carpeta destino

# Archivos de control
Contador_dir = "/home/logs"
Contador_id = os.path.join(Contador_dir, "contador.txt")
Procesados_id = os.path.join(Contador_dir, "procesados.txt")

# Crear carpetas si no existen
os.makedirs(Destino_pi, exist_ok=True)
os.makedirs(Contador_dir, exist_ok=True)

# Obtener el último ID usado
def get_ultimo_id():
    if not os.path.exists(Contador_id):
        with open(Contador_id, "w") as f:
            f.write("0")  # Crear archivo y escribir "0"
        return 0

    with open(Contador_id, "r") as f:
        contenido = f.read().strip()
        return int(contenido) if contenido.isdigit() else 0

# Guardar el nuevo ID
def guardar_id(ultimo_id):
    with open(Contador_id, "w") as f:
        f.write(str(ultimo_id))

# Obtener la fecha de creación del archivo
def get_fecha_id(ruta_archivo):
    return os.path.getctime(ruta_archivo)  # Devuelve la fecha de creación en segundos desde 1970

# Leer lista de archivos ya procesados
def cargar_procesados():
    if not os.path.exists(Procesados_id):
        with open(Procesados_id, "w") as f:  # Crea el archivo si no existe
            pass
        return {}

    procesados = {}
    with open(Procesados_id, "r") as f:
        for line in f:
            line = line.strip()
            if not line:  # Ignorar líneas vacías
                continue

            try:
                nombre, fecha_creacion = line.split(',')
                procesados[nombre] = float(fecha_creacion)
            except ValueError:
                print(f"⚠️ Línea malformada en {Procesados_id}: {line}, ignorando...")
                continue  # Ignorar líneas incorrectas

    return procesados

# Guardar archivo procesado con fecha de creación
def guardar_procesado(nombre_archivo, fecha_creacion):
    with open(Procesados_id, "a") as f:
        f.write(f"{nombre_archivo},{fecha_creacion}\n")

# Copiar imágenes sin duplicados y comparar por fecha de creación
def copiar_id():
    viejo_id = get_ultimo_id()
    procesados = cargar_procesados()

    print(f" Buscando imágenes en: {Origen_nikon}")
    print(f"Archivos ya procesados: {list(procesados.keys())}")

    for root, _, files in os.walk(Origen_nikon):
        print(f"Explorando: {root}, Archivos encontrados: {len(files)}")

        for file in files:
            if file.lower().endswith(".jpg"):
                src = os.path.join(root, file)
                fecha_creacion = get_fecha_id(src)

                # Verificar si el archivo ya ha sido procesado
                if file in procesados:
                    # Comparar las fechas de creación (si la foto ya existe y la fecha es más antigua, no copiarla)
                    if procesados[file] >= fecha_creacion:
                        print(f"⚠️ Duplicado encontrado (más antiguo): {file}, ignorando...")
                        continue

                # Si el archivo es más reciente o no existe, copiarlo
                viejo_id += 1
                dest_nombre = f"Arasunu_{viejo_id:03d}_{time.strftime('%Y%m%d_%H%M%S', time.localtime(fecha_creacion))}.jpg"
                dest = os.path.join(Destino_pi, dest_nombre)

                shutil.copy2(src, dest)  # Copia manteniendo metadatos
                print(f"✅ Copiado: {dest}")

                # Guardar el archivo como procesado con su fecha de creación
                guardar_procesado(file, fecha_creacion)
                guardar_id(viejo_id)

if __name__ == "__main__":
    copiar_id()

