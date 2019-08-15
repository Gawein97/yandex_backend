import pathlib

from .views import add_import

PROJECT_ROOT = pathlib.Path(__file__).parent


def setup_routes(app):
    app.router.add_post('/imports', add_import)
