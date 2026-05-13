# -*- coding: utf-8 -*-
"""pytest-bdd fixture：AppTest 初始化。"""
import os
import sys

import pytest
from streamlit.testing.v1 import AppTest

# 確保 streamlit_app.py 可被找到
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

APP_PATH = os.path.join(PROJECT_ROOT, "streamlit_app.py")


@pytest.fixture
def app():
    """新鮮的 AppTest 實例，已執行初始 run()。"""
    at = AppTest.from_file(APP_PATH).run()
    return at
