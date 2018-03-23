import os

from app import create_app
from app import models

config_name = os.getenv('APP_SETTINGS')  # config_name = "development"
app = create_app(config_name)

if __name__ == '__main__':
    #app.run()
    # We need to run test server with ssl_context to because Facebook API only accept request from "https"
    app.run(ssl_context='adhoc')
