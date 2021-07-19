from hafifa.flask_app.FlaskApp import FlaskAppHandler


if __name__ == '__main__':
    app = FlaskAppHandler()
    # app.init_database()
    app.run()
