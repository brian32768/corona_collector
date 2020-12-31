import os
from app import app

if __name__ == '__main__':
    print("We're starting up the Dash application.")
    app.run_server(debug=True)
