import whisper
import pickle
import os

def main():
    """Carga los modelos de whisper y los guarda en un archivo .pkl para que se carguen más rápido.

    Returns:
        None
    """
    if not os.path.exists('modelos'):
        os.mkdir('modelos')
    
    print('Cargando modelos rápidamente... ¡Ahora se iniciará la aplicación!')
    
    tiny_model = whisper.load_model('tiny')
    base_model = whisper.load_model('base')

    pickle.dump(tiny_model, open('modelos/tiny.pkl', 'wb'))
    pickle.dump(base_model, open('modelos/base.pkl', 'wb'))

    return None