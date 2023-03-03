import whisper
import pickle
import os

def main():
    if not os.path.exists('modelos'):
        os.mkdir('modelos')
    
    print('Cargando modelos rápidamente... ¡Ahora se iniciará la aplicación!')
    
    tiny_model = whisper.load_model('tiny')
    base_model = whisper.load_model('base')

    pickle.dump(tiny_model, open('modelos/tiny.pkl', 'wb'))
    pickle.dump(base_model, open('modelos/base.pkl', 'wb'))

    return None