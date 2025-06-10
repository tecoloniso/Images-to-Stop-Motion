import cv2
import os
import argparse
from PIL import Image
from PIL.ExifTags import TAGS
import datetime

def get_image_date(image_path):
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    if tag_name == 'DateTimeOriginal':
                        # Formato EXIF: "YYYY:MM:DD HH:MM:SS"
                        return datetime.datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception as e:
        print(f"No se pudo obtener fecha para {image_path}: {str(e)}")
    return None

def crear_stop_motion(carpeta_imagenes, fps, nombre_salida):
    # Obtener y ordenar imágenes por fecha EXIF
    imagenes = []
    for img_name in os.listdir(carpeta_imagenes):
        if img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(carpeta_imagenes, img_name)
            date = get_image_date(img_path)
            imagenes.append((img_path, date or datetime.datetime.min))
    
    if not imagenes:
        print("No se encontraron imágenes en la carpeta.")
        return
    
    # Ordenar por fecha
    imagenes.sort(key=lambda x: x[1])
    sorted_image_paths = [img[0] for img in imagenes]
    
    print(f"Se procesarán {len(sorted_image_paths)} imágenes ordenadas por fecha:")
    for i, img_path in enumerate(sorted_image_paths):
        print(f"{i+1}. {os.path.basename(img_path)}")
    
    # Obtener dimensiones de la primera imagen
    primera_img = cv2.imread(sorted_image_paths[0])
    if primera_img is None:
        print(f"No se pudo leer la imagen {sorted_image_paths[0]}")
        return
    
    altura, ancho, _ = primera_img.shape
    
    # Configurar el video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(nombre_salida, fourcc, fps, (ancho, altura))
    
    print(f"\nCreando video a {fps} FPS...")
    
    for i, img_path in enumerate(sorted_image_paths):
        print(f"Procesando: {os.path.basename(img_path)}")
        frame = cv2.imread(img_path)
        
        if frame is not None:
            video.write(frame)
        else:
            print(f"Error al leer {img_path}")
        
        # Mostrar progreso cada 50 imágenes o al final
        if (i+1) % 50 == 0 or i+1 == len(sorted_image_paths):
            print(f"Progreso: {i+1}/{len(sorted_image_paths)} imágenes")
    
    video.release()
    print(f"\nVideo guardado como {nombre_salida}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Creador de video stop motion ordenado por fecha EXIF')
    parser.add_argument('carpeta', help='Carpeta con las imágenes')
    parser.add_argument('--fps', type=int, default=12, help='Fotogramas por segundo')
    parser.add_argument('--output', default='stop_motion.mp4', help='Nombre del archivo de salida')
    
    args = parser.parse_args()
    
    crear_stop_motion(args.carpeta, args.fps, args.output)