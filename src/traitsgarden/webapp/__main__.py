"""Main module for running the Flask app."""
from .index import launch

def run():
    """Main method to run the app."""
    launch(debug=True)

if __name__ == "__main__":
    run()
