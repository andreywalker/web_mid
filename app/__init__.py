from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from .config import Config


db = SQLAlchemy()

CRIMINALS = [
    dict(name="Garrick Voss", nickname="The Comet", reward=12000,
         latitude=42.7, longitude=-71.3, location_note=None,
         difficulty=7, armed=True, has_crew=True, escape_master=False),
    dict(name=None, nickname="Ghost of Kessel", reward=25000,
         latitude=None, longitude=None, location_note="Spotted near the Kessel spice mines",
         difficulty=9, armed=True, has_crew=False, escape_master=True),
    dict(name="Lyra Thane", nickname="Silver Viper", reward=8000,
         latitude=-12.4, longitude=130.8, location_note="Cargo port, dock 7",
         difficulty=5, armed=True, has_crew=False, escape_master=False),
    dict(name="Bo Merrick", nickname="Rustbucket", reward=1500,
         latitude=51.5, longitude=-0.1, location_note=None,
         difficulty=2, armed=False, has_crew=False, escape_master=False),
    dict(name=None, nickname="Nebula Twins", reward=18000,
         latitude=None, longitude=None, location_note="Hiding in the Orion nebula belt",
         difficulty=8, armed=False, has_crew=True, escape_master=True),
    dict(name="Dax Orren", nickname="Iron Jaw", reward=5000,
         latitude=35.6, longitude=139.7, location_note="Orbital station Tycho-3",
         difficulty=4, armed=True, has_crew=True, escape_master=False),
]

HUNTS = [
    (0, False, "Ambushed at the refuel station, target escaped with his crew."),
    (0, False, "Tracked to a moon base, crew opened fire."),
    (1, False, "Target escaped through an asteroid field."),
    (1, False, "Lost the signal in the spice mines."),
    (1, False, "Trap was detected, ghost vanished again."),
    (2, False, "Viper slipped away in the crowded cargo port."),
    (2, True, "Captured at dock 7 after a short fight."),
    (3, True, "Found asleep in his ship. Easy catch."),
    (4, False, "Twins split up, followed the wrong one."),
    (4, False, "Nebula interference blocked the scanners."),
    (5, False, "Iron Jaw's crew blocked the airlock."),
    (5, True, "Captured on Tycho-3 with station security."),
]


def seed():
    from .models import HuntLog, WantedCriminal
    if WantedCriminal.query.first() is not None:
        return

    criminals = [WantedCriminal(**data) for data in CRIMINALS]
    db.session.add_all(criminals)
    db.session.flush()

    db.session.add_all(
        HuntLog(criminal_id=criminals[i].id, success=success, notes=notes)
        for i, success, notes in HUNTS
    )
    db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    from .routes.WantedCriminal import criminals_bp
    from .routes.HuntLog import log_bp
    app.register_blueprint(criminals_bp, url_prefix="/api/criminals")
    app.register_blueprint(log_bp, url_prefix="/api/hunts")

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    with app.app_context():
        db.create_all()
        seed()

    return app