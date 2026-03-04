"""
CTF Docente – Plataforma Web Propia
=====================================
Flask · SQLite · Bootstrap 5
Sin dependencias de CTFd ni servicios externos.

Rutas:
  GET  /                       → Splash / redirect
  GET  /login  POST /login     → Autenticación
  GET  /register POST          → Registro de alumnos
  GET  /logout                 → Cerrar sesión
  GET  /challenges             → Lista de retos
  POST /challenges/<id>/submit → Enviar flag
  POST /challenges/<id>/hint/<hid> → Desbloquear pista
  GET  /scoreboard             → Ranking
  GET  /admin                  → Panel administrador
  POST /admin/import           → Importar retos desde YAML
  POST /admin/settings         → Guardar configuración
  POST /admin/challenge/<id>/toggle → Mostrar/ocultar reto
  POST /admin/challenge/<id>/service-url → Actualizar URL servicio
  POST /admin/challenge/<id>/delete → Eliminar reto
  POST /admin/user/<id>/delete → Eliminar usuario
  POST /admin/reset-progress   → Resetear progreso (tests)
  GET  /api/scoreboard         → JSON para auto-refresh
"""

import os
import pathlib
import markdown as md
from functools import wraps
from datetime import datetime
from markupsafe import Markup
from flask import (Flask, render_template, request, redirect, url_for,
                   session, jsonify, flash, abort)
from werkzeug.security import generate_password_hash, check_password_hash
import yaml

from models import db, User, Challenge, Hint, Solve, HintUnlock, Submission, Setting

# ══════════════════════════════════════════════════════════════════════════════
# Configuración de la aplicación
# ══════════════════════════════════════════════════════════════════════════════

app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", "CAMBIA_ESTA_CLAVE_EN_PRODUCCION_2024")

DB_PATH = os.environ.get("DATABASE_URL", "sqlite:////data/ctf.db")
app.config["SQLALCHEMY_DATABASE_URI"] = DB_PATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# ══════════════════════════════════════════════════════════════════════════════
# Filtros y procesadores de contexto
# ══════════════════════════════════════════════════════════════════════════════

@app.template_filter("markdown")
def markdown_filter(text: str) -> Markup:
    """Convierte Markdown a HTML seguro."""
    return Markup(md.markdown(text or "", extensions=["fenced_code", "tables", "nl2br"]))


@app.context_processor
def inject_globals():
    """Variables disponibles en todos los templates."""
    u = _current_user()
    return {
        "ctf_name":    _setting("ctf_name", "CTF Docente"),
        "current_user": u,
        "user_score":  _calc_score(u) if u else 0,
        "session":     session,
    }


# ══════════════════════════════════════════════════════════════════════════════
# Helpers internos
# ══════════════════════════════════════════════════════════════════════════════

def _current_user():
    if "user_id" not in session:
        return None
    return db.session.get(User, session["user_id"])


def _setting(key: str, default: str = "") -> str:
    s = Setting.query.filter_by(key=key).first()
    return s.value if s else default


def _set_setting(key: str, value: str):
    s = Setting.query.filter_by(key=key).first()
    if s:
        s.value = value
    else:
        db.session.add(Setting(key=key, value=value))
    db.session.commit()


def _calc_score(user: User) -> int:
    """Puntuación = Σ max(0, valor_reto − coste_pistas_usadas) por cada reto resuelto."""
    if not user:
        return 0
    total = 0
    for solve in user.solves:
        ch = solve.challenge
        unlocked = (HintUnlock.query
                    .join(Hint)
                    .filter(HintUnlock.user_id == user.id,
                            Hint.challenge_id == ch.id)
                    .all())
        hint_deduction = sum(u.hint.cost for u in unlocked)
        total += max(0, ch.value - hint_deduction)
    return total


def _ctf_open() -> bool:
    return _setting("ctf_started", "false") == "true"


# ══════════════════════════════════════════════════════════════════════════════
# Decoradores de acceso
# ══════════════════════════════════════════════════════════════════════════════

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión para acceder.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        u = db.session.get(User, session["user_id"])
        if not u or not u.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ══════════════════════════════════════════════════════════════════════════════
# Rutas: Autenticación
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/")
def index():
    if _ctf_open() and "user_id" in session:
        return redirect(url_for("challenges"))
    return render_template("index.html",
                           ctf_started=_ctf_open(),
                           ctf_description=_setting("ctf_description"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("challenges"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session["user_id"]  = user.id
            session["username"] = user.username
            session["is_admin"] = user.is_admin
            flash(f"¡Bienvenido de vuelta, {user.username}!", "success")
            return redirect(url_for("challenges") if _ctf_open() else url_for("index"))

        flash("Usuario o contraseña incorrectos.", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if _setting("registration_open", "true") != "true":
        flash("El registro está cerrado. Contacta con el profesor.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm", "")

        errors = []
        if not username or not email or not password:
            errors.append("Todos los campos son obligatorios.")
        if len(username) < 3:
            errors.append("El nombre de usuario debe tener al menos 3 caracteres.")
        if password != confirm:
            errors.append("Las contraseñas no coinciden.")
        if len(password) < 6:
            errors.append("La contraseña debe tener al menos 6 caracteres.")
        if User.query.filter_by(username=username).first():
            errors.append("Ese nombre de usuario ya está en uso.")
        if User.query.filter_by(email=email).first():
            errors.append("Ese email ya está registrado.")

        if errors:
            for e in errors:
                flash(e, "danger")
        else:
            user = User(username=username, email=email,
                        password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            session.clear()
            session["user_id"]  = user.id
            session["username"] = user.username
            session["is_admin"] = False
            flash("¡Cuenta creada! ¡Mucha suerte en el CTF! 🏴", "success")
            return redirect(url_for("challenges") if _ctf_open() else url_for("index"))

    return render_template("register.html")


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ══════════════════════════════════════════════════════════════════════════════
# Rutas: Retos
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/challenges")
@login_required
def challenges():
    if not _ctf_open():
        flash("El CTF aún no ha comenzado. ¡Espera la señal del profesor! ⏳", "info")
        return redirect(url_for("index"))

    user = _current_user()
    all_challenges = (Challenge.query
                      .filter_by(state="visible")
                      .order_by(Challenge.category, Challenge.value)
                      .all())

    solved_ids         = {s.challenge_id for s in Solve.query.filter_by(user_id=user.id)}
    unlocked_hint_ids  = {u.hint_id for u in HintUnlock.query.filter_by(user_id=user.id)}
    categories         = sorted({c.category for c in all_challenges})

    return render_template("challenges.html",
                           challenges=all_challenges,
                           solved_ids=solved_ids,
                           unlocked_hint_ids=unlocked_hint_ids,
                           categories=categories)


@app.post("/challenges/<int:cid>/submit")
@login_required
def submit_flag(cid):
    if not _ctf_open():
        return jsonify(correct=False, message="El CTF no está activo."), 400

    challenge  = Challenge.query.get_or_404(cid)
    user       = _current_user()
    flag_input = (request.json or {}).get("flag", "").strip()

    # ¿Ya resuelto?
    if Solve.query.filter_by(user_id=user.id, challenge_id=cid).first():
        return jsonify(correct=True, already=True,
                       message="¡Ya habías resuelto este reto! 🎉")

    is_correct = (flag_input == challenge.flag)

    # Registrar intento (siempre)
    db.session.add(Submission(user_id=user.id, challenge_id=cid,
                               flag_submitted=flag_input, is_correct=is_correct))

    if is_correct:
        db.session.add(Solve(user_id=user.id, challenge_id=cid))
        db.session.commit()

        unlocked = (HintUnlock.query.join(Hint)
                    .filter(HintUnlock.user_id == user.id, Hint.challenge_id == cid)
                    .all())
        deduction = sum(u.hint.cost for u in unlocked)
        earned    = max(0, challenge.value - deduction)
        solves    = Solve.query.filter_by(challenge_id=cid).count()

        return jsonify(correct=True, message=f"¡Correcto! +{earned} puntos 🎉",
                       points=earned, solves=solves)

    db.session.commit()

    # Feedback proporcional a los intentos para motivar
    attempts = Submission.query.filter_by(user_id=user.id,
                                          challenge_id=cid,
                                          is_correct=False).count()
    tips = [
        "Flag incorrecta. ¡Sigue intentando!",
        "Casi... pero no. Revisa mayúsculas/minúsculas.",
        "Tercer intento. ¿Has leído bien la descripción?",
        "Muchos intentos... quizá quieras desbloquear una pista.",
    ]
    msg = tips[min(attempts - 1, len(tips) - 1)]
    return jsonify(correct=False, message=msg, attempts=attempts)


@app.post("/challenges/<int:cid>/hint/<int:hid>")
@login_required
def unlock_hint(cid, hid):
    hint = Hint.query.get_or_404(hid)
    if hint.challenge_id != cid:
        abort(400)

    user     = _current_user()
    existing = HintUnlock.query.filter_by(user_id=user.id, hint_id=hid).first()
    if existing:
        return jsonify(content=hint.content, already_unlocked=True, cost=hint.cost)

    db.session.add(HintUnlock(user_id=user.id, hint_id=hid))
    db.session.commit()
    return jsonify(content=hint.content, already_unlocked=False, cost=hint.cost)


# ══════════════════════════════════════════════════════════════════════════════
# Rutas: Scoreboard
# ══════════════════════════════════════════════════════════════════════════════

def _build_ranking():
    users   = User.query.filter_by(is_admin=False).all()
    ranking = []
    for u in users:
        score = _calc_score(u)
        last  = (Solve.query.filter_by(user_id=u.id)
                 .order_by(Solve.solved_at.desc()).first())
        ranking.append({
            "id":         u.id,
            "username":   u.username,
            "score":      score,
            "solves":     len(u.solves),
            "last_solve": last.solved_at.strftime("%d/%m %H:%M") if last else "—",
            "last_ts":    last.solved_at.isoformat() if last else "9999",
        })
    ranking.sort(key=lambda x: (-x["score"], x["last_ts"]))
    return ranking


@app.get("/scoreboard")
@login_required
def scoreboard():
    if not _ctf_open():
        flash("El CTF aún no ha comenzado.", "info")
        return redirect(url_for("index"))
    return render_template("scoreboard.html",
                           ranking=_build_ranking(),
                           current_user_id=session["user_id"])


@app.get("/api/scoreboard")
@login_required
def api_scoreboard():
    return jsonify(ranking=_build_ranking())


# ══════════════════════════════════════════════════════════════════════════════
# Rutas: Admin
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/admin")
@admin_required
def admin_dashboard():
    challenges_all = Challenge.query.order_by(Challenge.category, Challenge.value).all()
    users_all      = User.query.filter_by(is_admin=False).order_by(User.username).all()

    user_data = [{"user": u, "score": _calc_score(u), "solves": len(u.solves)}
                 for u in users_all]

    return render_template("admin.html",
                           stats={
                               "users":       len(users_all),
                               "challenges":  len(challenges_all),
                               "solves":      Solve.query.count(),
                               "submissions": Submission.query.count(),
                           },
                           challenges=challenges_all,
                           user_data=user_data,
                           settings={
                               "ctf_name":          _setting("ctf_name", "CTF Docente"),
                               "ctf_description":   _setting("ctf_description"),
                               "ctf_started":       _setting("ctf_started", "false"),
                               "registration_open": _setting("registration_open", "true"),
                           })


@app.post("/admin/import")
@admin_required
def admin_import():
    challenges_root = pathlib.Path("/challenges")
    if not challenges_root.exists():
        flash("❌ Directorio /challenges no montado. Revisa el docker-compose.yml", "danger")
        return redirect(url_for("admin_dashboard"))

    imported = skipped = errors = 0

    for yml_path in sorted(challenges_root.rglob("challenge.yml")):
        try:
            data = yaml.safe_load(yml_path.read_text(encoding="utf-8"))
            if not data or "name" not in data:
                continue

            # Inferir dificultad desde la ruta del directorio
            difficulty = "medio"
            for part in yml_path.parts:
                if part in ("facil", "medio", "dificil", "avanzado"):
                    difficulty = part
                    break

            # Parsear flag (puede ser string o dict)
            raw_flags = data.get("flags", [])
            if raw_flags:
                f0 = raw_flags[0]
                flag_value = f0.get("content", "") if isinstance(f0, dict) else str(f0)
            else:
                flag_value = ""

            # Evitar duplicados por nombre
            if Challenge.query.filter_by(name=data["name"]).first():
                skipped += 1
                continue

            ch = Challenge(
                name           = data["name"],
                author         = data.get("author", "Docente"),
                category       = data.get("category", "Misc"),
                difficulty     = difficulty,
                description    = data.get("description", ""),
                value          = int(data.get("value", 100)),
                flag           = flag_value,
                state          = data.get("state", "visible"),
                challenge_type = data.get("type", "standard"),
                service_url    = data.get("extra", {}).get("service_url", "") if isinstance(data.get("extra"), dict) else "",
            )
            db.session.add(ch)

            for h in data.get("hints", []):
                if isinstance(h, dict):
                    content, cost = h.get("content", ""), h.get("cost", 0)
                else:
                    content, cost = str(h), 0
                db.session.add(Hint(challenge=ch, content=content, cost=cost))

            db.session.commit()
            imported += 1

        except Exception as exc:
            errors += 1
            flash(f"⚠️ Error en {yml_path.name}: {exc}", "warning")

    flash(f"✅ Importados: {imported} | Ya existían: {skipped} | Errores: {errors}", "success")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/settings")
@admin_required
def admin_settings():
    _set_setting("ctf_name",          request.form.get("ctf_name", "CTF Docente"))
    _set_setting("ctf_description",   request.form.get("ctf_description", ""))
    _set_setting("ctf_started",       "true" if request.form.get("ctf_started")       else "false")
    _set_setting("registration_open", "true" if request.form.get("registration_open") else "false")
    flash("✅ Configuración guardada.", "success")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/challenge/<int:cid>/toggle")
@admin_required
def admin_toggle_challenge(cid):
    ch = Challenge.query.get_or_404(cid)
    ch.state = "hidden" if ch.state == "visible" else "visible"
    db.session.commit()
    return jsonify(state=ch.state)


@app.post("/admin/challenge/<int:cid>/service-url")
@admin_required
def admin_set_service_url(cid):
    ch = Challenge.query.get_or_404(cid)
    ch.service_url = request.json.get("url", "").strip()
    db.session.commit()
    return jsonify(ok=True)


@app.post("/admin/challenge/<int:cid>/delete")
@admin_required
def admin_delete_challenge(cid):
    ch = Challenge.query.get_or_404(cid)
    name = ch.name
    db.session.delete(ch)
    db.session.commit()
    flash(f"🗑️ Reto '{name}' eliminado.", "success")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/user/<int:uid>/delete")
@admin_required
def admin_delete_user(uid):
    u = User.query.get_or_404(uid)
    name = u.username
    db.session.delete(u)
    db.session.commit()
    flash(f"🗑️ Usuario '{name}' eliminado.", "success")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/reset-progress")
@admin_required
def admin_reset_progress():
    HintUnlock.query.delete()
    Submission.query.delete()
    Solve.query.delete()
    db.session.commit()
    flash("⚠️ Todos los progresos han sido reseteados.", "warning")
    return redirect(url_for("admin_dashboard"))


# ══════════════════════════════════════════════════════════════════════════════
# Inicialización
# ══════════════════════════════════════════════════════════════════════════════

def _import_challenges():
    """Importa todos los challenge.yml de /challenges. Omite los ya existentes."""
    challenges_root = pathlib.Path("/challenges")
    if not challenges_root.exists():
        return

    imported = 0
    for yml_path in sorted(challenges_root.rglob("challenge.yml")):
        try:
            data = yaml.safe_load(yml_path.read_text(encoding="utf-8"))
            if not data or "name" not in data:
                continue

            if Challenge.query.filter_by(name=data["name"]).first():
                continue

            difficulty = "medio"
            for part in yml_path.parts:
                if part in ("facil", "medio", "dificil", "avanzado"):
                    difficulty = part
                    break

            raw_flags = data.get("flags", [])
            if raw_flags:
                f0 = raw_flags[0]
                flag_value = f0.get("content", "") if isinstance(f0, dict) else str(f0)
            else:
                flag_value = ""

            ch = Challenge(
                name           = data["name"],
                author         = data.get("author", "Docente"),
                category       = data.get("category", "Misc"),
                difficulty     = difficulty,
                description    = data.get("description", ""),
                value          = int(data.get("value", 100)),
                flag           = flag_value,
                state          = data.get("state", "visible"),
                challenge_type = data.get("type", "standard"),
                service_url    = data.get("extra", {}).get("service_url", "") if isinstance(data.get("extra"), dict) else "",
            )
            db.session.add(ch)

            for h in data.get("hints", []):
                if isinstance(h, dict):
                    content, cost = h.get("content", ""), h.get("cost", 0)
                else:
                    content, cost = str(h), 0
                db.session.add(Hint(challenge=ch, content=content, cost=cost))

            db.session.commit()
            imported += 1
        except Exception as exc:
            print(f"[init] Error importando {yml_path}: {exc}", flush=True)

    if imported:
        print(f"[init] Retos importados automáticamente: {imported}", flush=True)


def init_app():
    os.makedirs("/data", exist_ok=True)
    with app.app_context():
        db.create_all()

        # Crear admin por defecto si no existe
        if not User.query.filter_by(username="admin").first():
            admin_pw = os.environ.get("ADMIN_PASSWORD", "ctf_admin_2024")
            db.session.add(User(
                username      = "admin",
                email         = "admin@ctf.local",
                password_hash = generate_password_hash(admin_pw),
                is_admin      = True,
            ))

        # Ajustes por defecto
        defaults = {
            "ctf_name":          os.environ.get("CTF_NAME", "CTF Docente"),
            "ctf_description":   "Plataforma de retos de ciberseguridad para el aula.",
            "ctf_started":       "true",
            "registration_open": "true",
        }
        for k, v in defaults.items():
            if not Setting.query.filter_by(key=k).first():
                db.session.add(Setting(key=k, value=v))

        db.session.commit()

        # Importar retos automáticamente al arrancar
        _import_challenges()


init_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
