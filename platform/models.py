"""
models.py — Modelos de base de datos
=====================================
SQLAlchemy + SQLite. Sin servidor externo.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(50), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin      = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    solves       = db.relationship("Solve",       backref="user", lazy=True,
                                   cascade="all, delete-orphan")
    hint_unlocks = db.relationship("HintUnlock",  backref="user", lazy=True,
                                   cascade="all, delete-orphan")
    submissions  = db.relationship("Submission",  backref="user", lazy=True,
                                   cascade="all, delete-orphan")


class Challenge(db.Model):
    __tablename__ = "challenges"
    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(100), nullable=False)
    author         = db.Column(db.String(50), default="Docente")
    category       = db.Column(db.String(50), nullable=False)
    difficulty     = db.Column(db.String(20), default="medio")
    description    = db.Column(db.Text, nullable=False)
    value          = db.Column(db.Integer, nullable=False)
    flag           = db.Column(db.String(256), nullable=False)
    state          = db.Column(db.String(20), default="visible")
    challenge_type = db.Column(db.String(20), default="standard")
    service_url    = db.Column(db.String(200), default="")  # URL del servicio Docker
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    hints       = db.relationship("Hint",       backref="challenge", lazy=True,
                                  cascade="all, delete-orphan")
    solves      = db.relationship("Solve",      backref="challenge", lazy=True,
                                  cascade="all, delete-orphan")
    submissions = db.relationship("Submission", backref="challenge", lazy=True,
                                  cascade="all, delete-orphan")


class Hint(db.Model):
    __tablename__ = "hints"
    id           = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False)
    content      = db.Column(db.Text, nullable=False)
    cost         = db.Column(db.Integer, default=0)


class Solve(db.Model):
    __tablename__ = "solves"
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False)
    solved_at    = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("user_id", "challenge_id"),)


class HintUnlock(db.Model):
    __tablename__ = "hint_unlocks"
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    hint_id     = db.Column(db.Integer, db.ForeignKey("hints.id"), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("user_id", "hint_id"),)
    hint = db.relationship("Hint")


class Submission(db.Model):
    __tablename__ = "submissions"
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    challenge_id   = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False)
    flag_submitted = db.Column(db.String(256))
    is_correct     = db.Column(db.Boolean)
    submitted_at   = db.Column(db.DateTime, default=datetime.utcnow)


class Setting(db.Model):
    __tablename__ = "settings"
    id    = db.Column(db.Integer, primary_key=True)
    key   = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text, default="")
