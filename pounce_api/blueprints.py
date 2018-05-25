# Import every blueprint file
from pounce_api.views import general, pounce_v1, index


def register_blueprints(app):
    """Adds all blueprint objects into the app."""
    app.register_blueprint(general.general)
    app.register_blueprint(pounce_v1.pounce_v1, url_prefix='/v1')
    app.register_blueprint(index.index)

    # All done!
    app.logger.info("Blueprints registered")
