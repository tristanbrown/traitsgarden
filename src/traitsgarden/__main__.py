"""Main module for running the Flask app."""
import os
import argparse
from traitsgarden import app

parser = argparse.ArgumentParser(description='Set the app startup mode.')
parser.add_argument('-t', '--test', action='store_true')
args = parser.parse_args()
if args.test:
    os.environ['APP_ENV'] = 'test'

def run():
    """Main method to run the app."""
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    run()
