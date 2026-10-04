from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Patient, VitalsRecord
from utils.triage_engine import compute_triage

triage_bp = Blueprint("triage", __name__, url_prefix="/api")


def _num(data, key, cast=float):
    v = data.get(key)
    if v in (None, ""):
        return None
    try:
        return cast(v)
    except (ValueError, TypeError):
        return None


@triage_bp.route("/triage", methods=["POST"])
@jwt_required()
def submit_triage():
    """
    Accepts vitals + symptoms for a given patient, computes severity,
    stores the record, and returns the triage result.
    """
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    patient_id = data.get("patient_id")
    patient = Patient.query.filter_by(id=patient_id, user_id=user_id).first()
    if not patient:
        return jsonify({"error": "Patient not found or not accessible"}), 404

    lang = data.get("lang", "en")

    vitals_payload = {
        "systolic_bp": _num(data, "systolic_bp", int),
        "diastolic_bp": _num(data, "diastolic_bp", int),
        "heart_rate": _num(data, "heart_rate", int),
        "respiratory_rate": _num(data, "respiratory_rate", int),
        "temperature_c": _num(data, "temperature_c", float),
        "spo2": _num(data, "spo2", int),
        "blood_sugar": _num(data, "blood_sugar", float),
        "sugar_test_type": data.get("sugar_test_type"),
        "consciousness": data.get("consciousness"),
        "symptoms": data.get("symptoms") or [],
    }

    result = compute_triage(vitals_payload, lang=lang)

    record = VitalsRecord(
        patient_id=patient.id,
        recorded_by=user_id,
        systolic_bp=vitals_payload["systolic_bp"],
        diastolic_bp=vitals_payload["diastolic_bp"],
        heart_rate=vitals_payload["heart_rate"],
        respiratory_rate=vitals_payload["respiratory_rate"],
        temperature_c=vitals_payload["temperature_c"],
        spo2=vitals_payload["spo2"],
        blood_sugar=vitals_payload["blood_sugar"],
        sugar_test_type=vitals_payload["sugar_test_type"],
        body_weight_kg=_num(data, "body_weight_kg", float),
        height_cm=_num(data, "height_cm", float),
        consciousness=vitals_payload["consciousness"],
        symptoms=vitals_payload["symptoms"],
        notes=data.get("notes"),
        severity_score=result["severity_score"],
        severity_level=result["severity_level"],
        severity_label=result["severity_label"],
        recommendation=result["recommendation"],
        contributing_factors=result["contributing_factors"],
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({"record": record.to_dict()}), 201


@triage_bp.route("/patients/<patient_id>/history", methods=["GET"])
@jwt_required()
def patient_history(patient_id):
    user_id = get_jwt_identity()
    patient = Patient.query.filter_by(id=patient_id, user_id=user_id).first()
    if not patient:
        return jsonify({"error": "Patient not found or not accessible"}), 404

    records = (
        VitalsRecord.query.filter_by(patient_id=patient.id)
        .order_by(VitalsRecord.created_at.desc())
        .all()
    )
    return jsonify({"records": [r.to_dict() for r in records]}), 200


@triage_bp.route("/records/<record_id>", methods=["GET"])
@jwt_required()
def get_record(record_id):
    user_id = get_jwt_identity()
    record = VitalsRecord.query.get(record_id)
    if not record or record.patient.user_id != user_id:
        return jsonify({"error": "Record not found"}), 404
    return jsonify({"record": record.to_dict()}), 200
