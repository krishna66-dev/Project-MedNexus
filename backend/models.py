import uuid
from datetime import datetime, date
from extensions import db


def gen_uuid():
    return str(uuid.uuid4())


class User(db.Model):
    """
    A registered user of MedNexus.
    role: 'self' (personal monitoring), 'asha', 'anm', 'admin'
    """
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    name = db.Column(db.String(120), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="self")
    region = db.Column(db.String(120), nullable=True)  # e.g. village/ward for ASHA/ANM
    phone = db.Column(db.String(15), nullable=True)
    preferred_language = db.Column(db.String(5), nullable=False, default="en")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patients = db.relationship("Patient", backref="registered_by", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "dob": self.dob.isoformat() if self.dob else None,
            "age": self.age,
            "email": self.email,
            "role": self.role,
            "region": self.region,
            "phone": self.phone,
            "preferred_language": self.preferred_language,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Patient(db.Model):
    """
    A patient record. For 'self' role users this is auto-created to mirror the
    user's own profile. For ASHA/ANM workers, many patients can be registered
    under one worker account.
    """
    __tablename__ = "patients"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    dob = db.Column(db.Date, nullable=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    village_ward = db.Column(db.String(160), nullable=True)
    contact_number = db.Column(db.String(15), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vitals = db.relationship("VitalsRecord", backref="patient", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "dob": self.dob.isoformat() if self.dob else None,
            "age": self.age,
            "gender": self.gender,
            "village_ward": self.village_ward,
            "contact_number": self.contact_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class VitalsRecord(db.Model):
    """
    A single vitals + symptoms capture, along with the computed triage result.
    """
    __tablename__ = "vitals_records"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    patient_id = db.Column(db.String(36), db.ForeignKey("patients.id"), nullable=False)
    recorded_by = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)

    # Vitals
    systolic_bp = db.Column(db.Integer, nullable=True)
    diastolic_bp = db.Column(db.Integer, nullable=True)
    heart_rate = db.Column(db.Integer, nullable=True)          # bpm
    respiratory_rate = db.Column(db.Integer, nullable=True)    # breaths/min
    temperature_c = db.Column(db.Float, nullable=True)         # Celsius
    spo2 = db.Column(db.Integer, nullable=True)                # %
    blood_sugar = db.Column(db.Float, nullable=True)           # mg/dL
    sugar_test_type = db.Column(db.String(10), nullable=True)  # 'fasting' | 'random' | 'pp'
    body_weight_kg = db.Column(db.Float, nullable=True)
    height_cm = db.Column(db.Float, nullable=True)
    consciousness = db.Column(db.String(10), nullable=True)    # AVPU: A/V/P/U

    symptoms = db.Column(db.JSON, nullable=True)  # list[str] of symptom codes
    notes = db.Column(db.Text, nullable=True)

    # Computed triage output
    severity_score = db.Column(db.Integer, nullable=False, default=0)
    severity_level = db.Column(db.String(10), nullable=False, default="green")  # green/yellow/orange/red
    severity_label = db.Column(db.String(40), nullable=False, default="")
    recommendation = db.Column(db.Text, nullable=True)
    contributing_factors = db.Column(db.JSON, nullable=True)  # list[str]

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "recorded_by": self.recorded_by,
            "vitals": {
                "systolic_bp": self.systolic_bp,
                "diastolic_bp": self.diastolic_bp,
                "heart_rate": self.heart_rate,
                "respiratory_rate": self.respiratory_rate,
                "temperature_c": self.temperature_c,
                "spo2": self.spo2,
                "blood_sugar": self.blood_sugar,
                "sugar_test_type": self.sugar_test_type,
                "body_weight_kg": self.body_weight_kg,
                "height_cm": self.height_cm,
                "consciousness": self.consciousness,
            },
            "symptoms": self.symptoms or [],
            "notes": self.notes,
            "triage": {
                "severity_score": self.severity_score,
                "severity_level": self.severity_level,
                "severity_label": self.severity_label,
                "recommendation": self.recommendation,
                "contributing_factors": self.contributing_factors or [],
            },
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
