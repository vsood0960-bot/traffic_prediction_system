import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app as flask_app


def test_database_config_uses_environment_variables():
    assert flask_app.DB_CONFIG['host'] != 'localhost'
