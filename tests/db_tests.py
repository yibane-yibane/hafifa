import os
import pytest
import tempfile
from sqlalchemy.testing import mock
from hafifa.data_base import data_models
from hafifa.tests.flaskr import create_app
from sqlalchemy.exc import OperationalError
from hafifa.data_base.query_creator import create_query
from alchemy_mock.mocking import UnifiedAlchemyMagicMock
from hafifa.data_base.SQLAlchemy import SQLAlchemyHandler


def test_db_connection():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({'TESTING': True, 'DATABASE': db_path})

    db = SQLAlchemyHandler()
    db.db.init_app(app)

    try:
        engine = db.db.get_engine(app)
        db_connection = engine.connect()
        engine.dispose()
        db_connection.close()
        is_connection_valid = True

    except OperationalError:
        is_connection_valid = False

    os.close(db_fd)
    os.unlink(db_path)

    assert is_connection_valid


def test_filter_no_condition():
    session = UnifiedAlchemyMagicMock()

    session.query = session.query(data_models.Video)
    session.query = create_query(session.query, [], {})

    session.assert_has_calls([])


def test_filter_single_condition():
    session = UnifiedAlchemyMagicMock()

    session.query = session.query()
    session.query = create_query(session.query, [], {data_models.Video.id: '1'})

    session.assert_has_calls([
        mock.call(data_models.Video.id == '1')
    ])


def test_filter_multi_conditions():
    session = UnifiedAlchemyMagicMock()

    session.query = session.query()
    session.query = create_query(session.query, [], {data_models.Video.number_of_frames: 10, data_models.Video.id: '1'})

    session.filter.assert_has_calls([
        mock.call(data_models.Video.number_of_frames == 10, data_models.Video.id == '1'),
    ])


def test_filter_with_relation():
    session = UnifiedAlchemyMagicMock()

    session.query = session.query()
    session.query = create_query(session.query, [], {data_models.Frame.video_id: data_models.Video.id, data_models.Frame.index: 10})

    session.filter.assert_has_calls([
        mock.call(data_models.Frame.video_id == data_models.Video.id, data_models.Frame.index == 10),
    ])


def test_filter_with_relation_without_invalid_attribute():
    session = UnifiedAlchemyMagicMock()
    session.query = session.query()

    with pytest.raises(AttributeError):
        create_query(session.query, [], {data_models.Frame.fff: data_models.Video.id, data_models.Frame.index: 10})
