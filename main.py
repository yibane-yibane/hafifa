from hafifa.data_base.SQLAlchemy import SQLAlchemyHandler
from hafifa.flask_app.FlaskApp import FlaskAppHandler


if __name__ == '__main__':
    app = FlaskAppHandler()
    db = SQLAlchemyHandler()
    db.db.init_app(app.app)

    with app.app.app_context():
        db.init_database()

    app.run()
