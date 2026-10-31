from datetime import datetime, timezone

from . import db


class WantedCriminal(db.Model):
    __tablename__ = "wanted_criminals"
    __table_args__ = (
        db.CheckConstraint("difficulty BETWEEN 1 AND 10", name="difficulty_1_to_10"),
        db.CheckConstraint("reward >= 0", name="reward_not_negative"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    nickname = db.Column(db.String(100), nullable=False)
    reward = db.Column(db.Integer, nullable=False)

    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    location_note = db.Column(db.Text, nullable=True)

    difficulty = db.Column(db.Integer, nullable=False)
    armed = db.Column(db.Boolean, nullable=False, default=False)
    has_crew = db.Column(db.Boolean, nullable=False, default=False)
    escape_master = db.Column(db.Boolean, nullable=False, default=False)

    hunts = db.relationship(
        "HuntLog", back_populates="criminal",
        cascade="all, delete-orphan", order_by="HuntLog.id",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "nickname": self.nickname,
            "reward": self.reward,
            "last_known_location": {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "note": self.location_note,
            },
            "difficulty": self.difficulty,
            "armed": self.armed,
            "has_crew": self.has_crew,
            "escape_master": self.escape_master,
        }


class HuntLog(db.Model):
    __tablename__ = "hunt_logs"

    id = db.Column(db.Integer, primary_key=True)
    criminal_id = db.Column(
        db.Integer, db.ForeignKey("wanted_criminals.id"), nullable=False, index=True
    )
    success = db.Column(db.Boolean, nullable=False, default=False)
    notes = db.Column(db.Text, nullable=False, default="")
    # Set by the server, never by the client
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    criminal = db.relationship("WantedCriminal", back_populates="hunts")

    def to_dict(self):
        return {
            "id": self.id,
            "criminal_id": self.criminal_id,
            "criminal_nickname": self.criminal.nickname,
            "success": self.success,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }