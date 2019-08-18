import pathlib

from .middlewares import import_exist, update_citizen_validation, validate_citizen
from .views import add_import, update_citizen, get_citizens, get_birthdays, get_percentile

PROJECT_ROOT = pathlib.Path(__file__).parent


def setup_routes(app):
    app.router.add_post('/imports', add_import)
    app.router.add_patch(r'/imports/{import_id:\d+}/citizens/{citizen_id:\d+}', update_citizen_validation,
                         validate_citizen, update_citizen)
    app.router.add_get(r'/imports/{import_id:\d+}/citizens', import_exist, get_citizens)
    app.router.add_get(r'/imports/{import_id:\d+}/citizens/birthdays', import_exist, get_birthdays)
    app.router.add_get(r'/imports/{import_id:\d+}/towns/stat/percentile/age', import_exist, get_percentile)
