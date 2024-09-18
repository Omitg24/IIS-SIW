import glob
import os
import random
import re

from tqdm import tqdm
from transformers import BertTokenizer, BertModel
from vespa.application import Vespa

"""

Función que recibe un texto *en inglés* y genera un embedding de 348 dimensiones.

"""

tokenizer = BertTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
model = BertModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

def text_to_embedding(text):
    tokens = tokenizer(text, return_tensors="pt", max_length=100, truncation=True, padding=True)
    outputs = model(**tokens)
    return outputs[0].tolist()[0][0]

"""

Función muy sencilla para que las rutas de los archivos no den problemas como identificadores...

"""

def ruta_archivo_to_id(ruta):
    ruta = ruta.split("20news-18828\\")
    ruta = ruta[1]
    ruta = ruta.replace(".","_")
    ruta = ruta.replace("\\","_")
    return ruta

"""

Procesamos la colección 20 Newsgroups. A Vespa se le pasará el texto (que indexará
para realizar búsquedas con BM25 y Native Rank) y los embeddings (contra los que
se podrán comparar embeddings de consultas).

¡Atención! Este procesamiento no implica aún "indexado" en Vespa, es lento porque
codificar los textos de los documentos en embeddings lleva bastante tiempo.

"""

folder_path = "files\\20news-18828"

collection = list()

count = 0

archivos = glob.glob(os.path.join(folder_path, '**', '*'), recursive=True)

# Si no queréis procesar todos podéis descomentar esto...
#
random.shuffle(archivos)
#archivos = archivos[0:100]

# Es un poco chapuza poner el total así pero en este caso concreto lo conozco...
#
with tqdm(total=18828) as barra:
    for archivo in archivos:
        if not os.path.isdir(archivo):
            # Mucho más elegante usar tqdm que mostrar el archivo por el que vamos...
            #
            # print(archivo)

            with open(archivo, "r", encoding="latin1") as f:
                #
                # Chapucilla para evitar que textos Latin1 con caracteres
                # que dan problemas acaben en la colección (habría que quitar
                # los caracteres y no los documentos...)
                #
                try:
                    text = f.read()

                    text = text.encode("latin1") # Se convierte desde Latin1 a una secuencia de bytes
                    text = text.decode("utf-8") # Se codifica esa secuencia de bytes en UTF-8
                    text = " ".join(text.splitlines()) # Eliminamos saltos de línea
                    text = re.sub(r'\s+', ' ', text) # Eliminamos múltiples espacios en blanco

                    # Como aún sigue habiendo caracteres de escape que dan problemas
                    # al enviarse a Vespa hacemos una última chapuza...

                    for remove in ["\x08","\x02", "\x18", "\x10", "\x1b", "\x06", "\x19", "\x03", "\x1a"]:
                        text = text.replace(remove,"") # \x08 es backspace... \x02 start of text \x18 cancel \x10 data link escape

                    collection.append({
                        "id": ruta_archivo_to_id(archivo),
                        "fields": {
                            "text": text,
                            "text_embeddings": text_to_embedding(text)
                        }
                    })
                except Exception as e:
                    print(e)

                barra.update(1)

"""

Nos conectamos a la instancia de Vespa correcta.

Le pasamos un trabajo por lotes, ¡ojo al esquema!

"""

app = Vespa(url = "http://localhost:8080/")

"""

¡Atención! Se ha bajado bastante el tamaño de cada lote respecto al valor por
defecto (1000), estos documentos son bastante más pesados y, después de todo,
son peticiones HTTP con latencia y timeouts...

"""

feed_res = app.feed_batch(batch=collection, schema="VespaDemoSIW", asynchronous=False, batch_size=100, total_timeout=60)