"""Set up Flask app"""
import dash

from traitsgarden.settings import AppConfig

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
server.config.from_object(AppConfig())
app.config.suppress_callback_exceptions = True
