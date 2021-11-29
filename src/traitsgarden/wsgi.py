"""Main module for running the Flask app."""
from traitsgarden import index

def run():
    """Main method to run the app."""
    index.launch(debug=True)

if __name__ == "__main__":
    run()
