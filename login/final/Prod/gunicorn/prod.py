from gunicorn_config import bind, certfile, keyfile
from login5 import app

if __name__ == '__main__':
    app.run()