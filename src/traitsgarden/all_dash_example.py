import os
import dash

from . import view

app = dash.Dash()

## Create Main View
app.layout = view.layout
view.get_callbacks(app)

def run():
    app.run_server(port=8888, host='0.0.0.0', debug=True)

if __name__ == '__main__':
    run()
