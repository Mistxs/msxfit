import os
import click
from flask import Flask, jsonify

from .config import Config
from .extensions import db, cors
from .cache import cache


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    cache.init_app(app)

    from .api import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.get("/health")
    def health():
        return jsonify(
            status="ok",
            db=app.config["SQLALCHEMY_DATABASE_URI"].split(":")[0],
            redis=cache.available(),
        )

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify(error="not found"), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.exception("server error: %s", e)
        return jsonify(error="server error"), 500

    @app.cli.command("init-db")
    def init_db():
        """Создать схему, дефолтный профиль и наполнить справочник продуктов."""
        from .models import Profile
        from .seed import seed_defaults
        db.create_all()
        if not Profile.query.get(1):
            db.session.add(Profile(id=1))
            db.session.commit()
        seed_defaults()
        click.echo("✓ DB initialized, profile + defaults seeded")

    return app
