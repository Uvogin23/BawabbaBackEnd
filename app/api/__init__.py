from flask import Flask
from .diplomats import diplomats_bp
from .citizens import citizens_bp
from .tourists import tourists_bp
from .algerian_tourists import algerian_tourists_bp
from .non_residents import non_residents_bp
from .stats import stats_bp
from .login import login_bp

def register_blueprints(app: Flask):
    app.register_blueprint(diplomats_bp)
    app.register_blueprint(citizens_bp)
    app.register_blueprint(tourists_bp)
    app.register_blueprint(algerian_tourists_bp)
    app.register_blueprint(non_residents_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(login_bp)