import pathlib

from .views import add_import, update_citizen, get_citizens, get_birthdays

PROJECT_ROOT = pathlib.Path(__file__).parent


def setup_routes(app):
    app.router.add_post('/imports', add_import)
    app.router.add_patch(r'/imports/{import_id:\d+}/citizens/{citizen_id:\d+}', update_citizen)
    app.router.add_get(r'/imports/{import_id:\d+}/citizens', get_citizens)
    app.router.add_get(r'/imports/{import_id:\d+}/citizens/birthdays', get_birthdays)
