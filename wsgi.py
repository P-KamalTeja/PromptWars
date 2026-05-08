"""WSGI entrypoint for Cloud Run."""
from src.core import Config
from src.ui.web_ui import WebUI


config = Config.from_env()
app = WebUI(config).app
