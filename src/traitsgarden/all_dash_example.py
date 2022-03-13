import os
import dash

import view

app = dash.Dash()

## Create Main View
app.layout = view.layout

def run():
    app.run_server(port=5000, host='0.0.0.0', debug=True)

if __name__ == '__main__':
    run()
