from hafifa.data_base_wrap.SQLAlchemyWrapper import SQLAlchemyWrapper


if __name__ == '__main__':
    db = SQLAlchemyWrapper()
    db.create_tables()
