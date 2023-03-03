from nltk.corpus import stopwords
from collections import Counter
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from wordcloud import WordCloud
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from heapq import nlargest

def hacer_resumen(texto):
    """Realiza un resumen del texto.

    Args:
        texto (str): Texto del que se quiere hacer el resumen.

    Returns:
        resumen (str): Resumen del texto.
    """
    n=3
    oraciones = sent_tokenize(texto)
    palabras = word_tokenize(texto.lower())
    
    # Eliminar palabras vacías.
    palabras = [palabra for palabra in palabras if palabra not in stopwords.words('spanish')]
    
    # Calcular la frecuencia de cada palabra.
    frecuencia_palabras = nltk.FreqDist(palabras)
    
    # Calcular el puntaje de cada oración.
    puntajes = {}
    for i, oracion in enumerate(oraciones):
        for palabra in word_tokenize(oracion.lower()):
            if palabra in frecuencia_palabras:
                if i in puntajes:
                    puntajes[i] += frecuencia_palabras[palabra]
                else:
                    puntajes[i] = frecuencia_palabras[palabra]
                    
    # Obtener las oraciones con los puntajes más altos.
    oraciones_resumen = nlargest(n, puntajes, key=puntajes.get)
    resumen = ' '.join([oraciones[i] for i in sorted(oraciones_resumen)])
    return resumen

def wordcloud(texto:str):
    """Genera una imagen de un wordcloud a partir de un texto.

    Args:
        texto (str): Texto del que se quiere generar el wordcloud.

    Returns:
        img_base64 (base64): Imagen del wordcloud en formato base64.
    """
    ### Wordcloud ###
    wordcloud = WordCloud(width=400, height=150, background_color='white').generate(texto)

    # Generar imagen del WordCloud
    img = BytesIO()
    plt.figure(figsize=(8, 3.5), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    # Convertir imagen a formato base64
    img_base64 = base64.b64encode(img.getvalue()).decode("utf-8")
    return img_base64

def generar_histograma(texto, n=10):
    """Genera un histograma de las palabras más frecuentes en un texto.

    Args:
        texto (str): Texto del que se quiere generar el histograma.
        n (int, optional): Por defecto 10. Número de palabras que se quieren mostrar en el histograma.

    Returns:
        img_base64 (base64): Imagen del wordcloud en formato base64.
        frecuencia_palabras (dict): Diccionario con las palabras más frecuentes y su frecuencia.
    """
    # Limpiar texto de signos de puntuación y números
    texto_limpio = re.sub('[^A-Za-zñÑáéíóúÁÉÍÓÚ\s]+', '', texto)

    # Convertir texto a lista de palabras y convertirlas a minúsculas
    palabras = texto_limpio.lower().split()

    palabras_filtradas = [palabra for palabra in palabras if palabra.lower() not in stopwords.words('spanish') and palabra.isalpha()]

    frecuencia = Counter(palabras_filtradas)

    # Crear histograma
    palabras = [palabra for palabra, frec in frecuencia.most_common(n)]
    frecuencias = [frec for palabra, frec in frecuencia.most_common(n)]

    # Convertir imagen a base64
    img = BytesIO()
    plt.bar(palabras, frecuencias)
    plt.title("Histograma de palabras")
    plt.xlabel("Palabras")
    plt.ylabel("Frecuencia")
    plt.xticks(rotation=45)
    plt.subplots_adjust(bottom=0.3)
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    img_base64 = base64.b64encode(img.getvalue()).decode()

    frecuencia_palabras = dict(frecuencia.most_common(n))
    return img_base64, frecuencia_palabras

def average_word_length(texto):
    """Calcula la longitud media de las palabras de un texto.

    Args:
        texto (str): Texto del que se quiere calcular la longitud media de las palabras.

    Returns:
        longitud_media (float): Longitud media de las palabras del texto.
    """
    palabras = word_tokenize(texto.lower())
    stopwords_es = set(stopwords.words('spanish'))
    palabras_filtradas = [palabra for palabra in palabras if palabra not in stopwords_es]
    longitudes = [len(palabra) for palabra in palabras_filtradas]
    longitud_media = sum(longitudes) / len(longitudes)
    return longitud_media

def n_frases(texto):
    """Calcula el número de frases de un texto.

    Args:
        texto (str): Texto del que se quiere calcular el número de frases.

    Returns:
        Número de frases del texto.
    """
    return len(texto.split('.'))