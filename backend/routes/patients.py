from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Patient, User

patients_bp = Blueprint("patients", __name__, url_prefix="/api/patients")


def _parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


@patients_bp.route("", methods=["GET"])
@jwt_required()
def list_patients():
    user_id = get_jwt_identity()
    patients = Patient.query.filter_by(user_id=user_id).order_by(Patient.created_at.desc()).all()
    return jsonify({"patients": [p.to_dict() for p in patients]}), 200


@patients_bp.route("", methods=["POST"])
@jwt_required()
def create_patient():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user.role not in ("asha", "anm", "admin"):
        return jsonify({"error": "Only ASHA/ANM/admin accounts can register new patients"}), 403

    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"errors": {"name": "Patient name is required"}}), 400

    dob = _parse_date(data.get("dob"))
    age = data.get("age")
    if dob and not age:
        today = datetime.utcnow().date()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    patient = Patient(
        user_id=user_id,
        name=name,
        dob=dob,
        age=age,
        gender=data.get("gender"),
        village_ward=data.get("village_ward"),
        contact_number=data.get("contact_number"),
    )
    db.session.add(patient)
    db.session.commit()
    return jsonify({"patient": patient.to_dict()}), 201


@patients_bp.route("/<patient_id>", methods=["GET"])
@jwt_required()
def get_patient(patient_id):
    user_id = get_jwt_identity()
    patient = Patient.query.filter_by(id=patient_id, user_id=user_id).first()
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify({"patient": patient.to_dict()}), 200
