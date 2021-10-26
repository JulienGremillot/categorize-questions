from flask import Flask, render_template, request
import os
import logging as log
import pickle
import gc
import nltk

app = Flask(__name__)

# Config options - Make sure you created a 'config.py' file.
app.config.from_object('config')
# To get one variable, tape app.config['MY_VARIABLE']


def join(models_dir, dest_file, read_size):

    # Create a new destination file
    output_path = os.path.join(models_dir, dest_file)
    if os.path.isfile(output_path):
        log.warning("Le fichier " + output_path + " existe déjà : on le supprime")
        os.remove(output_path)

    # Get a list of the file parts
    parts = [f for f in os.listdir(models_dir) if f.startswith(dest_file.split('.')[0])]
    parts.sort()
    log.warning("Récupération des " + str(len(parts)) + " fichiers du modèle")

    output_file = open(output_path, 'wb')

    # Go through each portion one by one
    for file in parts:

        # Assemble the full path to the file
        path = os.path.join(models_dir, file)
        log.warning("Est-ce que le fichier " + path + " existe ? => " + str(os.path.isfile(path)))

        # Open the part
        input_file = open(path, 'rb')

        while True:
            # Read all bytes of the part
            bytes = input_file.read(read_size)
            # Break out of loop if we are at end of file
            if not bytes:
                break
            # Write the bytes to the output file
            output_file.write(bytes)

        # Close the input file
        input_file.close()

    # Close the output file
    output_file.close()
    log.warning("Ecriture du fichier " + str(output_path))


basedir = os.path.abspath(os.path.dirname(__file__))
models_dir = os.path.join(basedir, 'static', 'models')
join(models_dir=models_dir, dest_file="classifier.pkl", read_size=50000000)
log.warning('Classifier reassembled !')

# Je charge le classifier
classifier_path = os.path.join(models_dir, "classifier.pkl")
if os.path.isfile(classifier_path):
    log.warning("Le fichier " + classifier_path + " existe bien")
app.classifier = pickle.load(open(classifier_path, 'rb'))

# et le multilabelbinazer
mlb_path = os.path.join(models_dir, "mlb.pkl")
if os.path.isfile(mlb_path):
    log.warning("Le fichier " + mlb_path + " existe bien")
app.mlb = pickle.load(open(mlb_path, 'rb'))

# Initialisation d'un tokenizer
tokenizer = nltk.RegexpTokenizer(r'\w+')

# On récupère une liste de stopwords anglais
nltk.download('stopwords')
app.sw = nltk.corpus.stopwords.words('english')

gc.collect()

@app.route('/')
@app.route('/index/')
def index():
    return render_template('index.html')


@app.route('/api/')
def result():

    # Récupération du paramètre
    question = request.args.get('question')

    log.warning("On a la question suivante : " + question)

    # On passe la question en minuscules, on la tokenize et on supprime les stopwords
    question = tokenizer.tokenize(question.lower())
    log.warning("On a la question tokenizée : " + question)

    question = [w for w in question if w not in app.sw]
    log.warning("On a la question cleanée : " + question)

    res = app.classifier.predict([' '.join(question)])
    tags = app.mlb.inverse_transform(res)[0]

    log.warning("Le modèle a renvoyé " + str(len(tags)) + " tags : " + ' '.join(tags))

    return render_template('api.html', tags=tags)
