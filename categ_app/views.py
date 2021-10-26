from flask import Flask, render_template, request
import os
import logging as log
import pickle

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
app.classifier = pickle.load(open(os.path.join(models_dir, "classifier.pkl"), 'rb'))

# et le multilabelbinazer
app.mlb = pickle.load(open(os.path.join(models_dir, "mlb.pkl"), 'rb'))


@app.route('/')
@app.route('/index/')
def index():
    return render_template('index.html')


@app.route('/api/')
def result():

    # TODO implémenter le nettoyage
    question = request.args.get('question')

    res = app.classifier.predict([question])
    tags = app.mlb.inverse_transform(res)[0]

    return render_template('api.html', tags)
