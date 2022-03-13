"""Main module for running the Flask app."""
from traitsgarden import app

def run():
    """Main method to run the app."""
    app.run_server(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    run()
