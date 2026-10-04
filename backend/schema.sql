-- MedNexus PostgreSQL schema
-- Run against an empty database, e.g.:
--   createdb mednexus_db
--   psql -d mednexus_db -f schema.sql
-- (Alternatively, use `flask db upgrade` with the included Flask-Migrate setup
--  which will generate/manage this schema from models.py automatically.)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
    id                  VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    name                VARCHAR(120) NOT NULL,
    dob                 DATE NOT NULL,
    age                 INTEGER NOT NULL,
    email               VARCHAR(160) UNIQUE NOT NULL,
    password_hash       VARCHAR(255) NOT NULL,
    role                VARCHAR(20) NOT NULL DEFAULT 'self',
    region              VARCHAR(120),
    phone               VARCHAR(15),
    preferred_language  VARCHAR(5) NOT NULL DEFAULT 'en',
    created_at          TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

CREATE TABLE IF NOT EXISTS patients (
    id              VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id         VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            VARCHAR(120) NOT NULL,
    dob             DATE,
    age             INTEGER,
    gender          VARCHAR(10),
    village_ward    VARCHAR(160),
    contact_number  VARCHAR(15),
    created_at      TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_patients_user_id ON patients(user_id);

CREATE TABLE IF NOT EXISTS vitals_records (
    id                     VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    patient_id             VARCHAR(36) NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    recorded_by            VARCHAR(36) NOT NULL REFERENCES users(id),
    systolic_bp            INTEGER,
    diastolic_bp           INTEGER,
    heart_rate             INTEGER,
    respiratory_rate       INTEGER,
    temperature_c          REAL,
    spo2                   INTEGER,
    blood_sugar            REAL,
    sugar_test_type        VARCHAR(10),
    body_weight_kg         REAL,
    height_cm              REAL,
    consciousness          VARCHAR(10),
    symptoms               JSONB,
    notes                  TEXT,
    severity_score         INTEGER NOT NULL DEFAULT 0,
    severity_level         VARCHAR(10) NOT NULL DEFAULT 'green',
    severity_label         VARCHAR(40) NOT NULL DEFAULT '',
    recommendation         TEXT,
    contributing_factors   JSONB,
    created_at             TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_vitals_patient_id ON vitals_records(patient_id);
CREATE INDEX IF NOT EXISTS idx_vitals_created_at ON vitals_records(created_at);
