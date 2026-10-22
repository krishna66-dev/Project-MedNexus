from datetime import datetime, date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db, bcrypt
from models import User, Patient

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

VALID_ROLES = {"self", "asha", "anm", "admin"}


def _parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _calc_age(dob: date) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    dob_raw = data.get("dob")
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = data.get("role", "self")
    region = (data.get("region") or "").strip() or None
    phone = (data.get("phone") or "").strip() or None
    gender = (data.get("gender") or "").strip().lower() or None
    if gender not in (None, "male", "female", "other"):
        gender = None
    preferred_language = data.get("preferred_language", "en")

    errors = {}
    if not name:
        errors["name"] = "Name is required"
    dob = _parse_date(dob_raw)
    if not dob:
        errors["dob"] = "Valid date of birth (YYYY-MM-DD) is required"
    elif dob >= date.today():
        errors["dob"] = "Date of birth must be in the past"
    if not email or "@" not in email:
        errors["email"] = "A valid email address is required"
    if not password or len(password) < 8:
        errors["password"] = "Password must be at least 8 characters"
    if role not in VALID_ROLES:
        errors["role"] = "Invalid role"

    if errors:
        return jsonify({"errors": errors}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"errors": {"email": "An account with this email already exists"}}), 409

    age = _calc_age(dob)
    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(
        name=name,
        dob=dob,
        age=age,
        email=email,
        password_hash=pw_hash,
        role=role,
        region=region,
        phone=phone,
        preferred_language=preferred_language if preferred_language in ("en", "hi") else "en",
    )
    db.session.add(user)
    db.session.flush()  # get user.id before commit

    # For personal-monitoring users, auto-create a linked patient profile
    if role == "self":
        self_patient = Patient(
            user_id=user.id,
            name=name,
            dob=dob,
            age=age,
            gender=gender,
        )
        db.session.add(self_patient)

    db.session.commit()

    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200
