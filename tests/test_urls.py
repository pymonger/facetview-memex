#! ../env/bin/python
# -*- coding: utf-8 -*-
from memex import create_app
from memex.models import db


class TestURLs:
    def setup(self):
        app = create_app('memex.settings.DevConfig', env='dev')
        self.app = app.test_client()
        db.app = app
        db.create_all()

    def teardown(self):
        db.session.remove()
        db.drop_all()

    def test_home(self):
        rv = self.app.get('/')
        assert rv.status_code == 200

    def test_login(self):
        rv = self.app.get('/login')
        assert rv.status_code == 200

    def test_logout(self):
        rv = self.app.get('/logout')
        assert rv.status_code == 302

    def test_restricted(self):
        rv = self.app.get('/restricted')
        assert rv.status_code == 302
