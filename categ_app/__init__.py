import os
from .views import app
from . import models
import logging as log


def join(dest_file, read_size):
    # Create a new destination file
    output_file = open(dest_file, 'wb')

    # Get a list of the file parts
    basedir = os.path.abspath(os.path.dirname(__file__))
    models_dir = os.path.join(basedir, 'static', 'models')
    parts = [f for f in os.listdir('.') if f.startswith(dest_file.split('.')[0])]

    # Go through each portion one by one
    for file in parts:

        # Assemble the full path to the file
        path = file

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


join(dest_file="classifier.pkl", read_size=50000000)
log.warning('Classifier reassembled !')
