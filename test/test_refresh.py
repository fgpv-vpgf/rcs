from services.registration import refresh_records
from flask import Flask


def test_empty(monkeypatch):
    app = Flask('temp')
    monkeypatch.setattr("services.db.query", lambda q: [])
    with app.app_context():
        x = refresh_records(1, 1, {})
        assert x['updated'] == []
        assert x['errors'] == {}


def test_single(monkeypatch):
    app = Flask('temp')
    monkeypatch.setattr("services.db.query", lambda q: [{'id': '1', 'value': {'request': {}, 'updated': 3, 'version': '2.0'}}])  # noqa
    monkeypatch.setattr("services.db.put_doc", lambda *args, **kw: args[0])
    monkeypatch.setattr("services.regparse.make_node", lambda *args: ({'en': {'layerType': 'random'}}, None))
    with app.app_context():
        x = refresh_records(1, 1, {})
        assert x['updated'] == ['1']
        assert x['errors'] == {}


def test_limit(monkeypatch):
    app = Flask('temp')
    monkeypatch.setattr("services.db.query", lambda q: [{'id': '1', 'value': {'request': {}, 'updated': 3, 'version': '2.0'}}, {'id': '2', 'value': {'request': {}, 'updated': 5, 'version': '2.0'}}])  # noqa
    monkeypatch.setattr("services.db.put_doc", lambda *args, **kw: args[0])
    monkeypatch.setattr("services.regparse.make_node", lambda *args: ({'en': {'layerType': 'random'}}, None))
    with app.app_context():
        x = refresh_records(1, 1, {})
        assert x['updated'] == ['1']
        assert x['limit_reached'] is True


def test_old(monkeypatch):
    app = Flask('temp')
    monkeypatch.setattr("services.db.query", lambda q: [{'id': '1', 'value': {'request': {}, 'updated': 3}}])  # noqa
    monkeypatch.setattr("services.db.put_doc", lambda *args, **kw: args[0])
    monkeypatch.setattr("services.regparse.make_node", lambda *args: ({'en': {'layerType': 'random'}}, None))
    with app.app_context():
        x = refresh_records(1, 1, {})
        assert '1' in x['errors']
