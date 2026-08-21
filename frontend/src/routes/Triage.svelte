<script lang="ts">
  import { onMount } from "svelte";
  import { push } from "svelte-spa-router";
  import { t, lang } from "../lib/i18n";
  import { api, ApiError } from "../lib/api";
  import { currentUser, selectedPatientId } from "../lib/stores";
  import SymptomChecklist from "../lib/components/SymptomChecklist.svelte";
  import type { Patient, SymptomCode, VitalsRecord } from "../lib/types";

  let patients: Patient[] = [];
  let patientId: string | null = null;

  let systolic_bp: number | null = null;
  let diastolic_bp: number | null = null;
  let heart_rate: number | null = null;
  let respiratory_rate: number | null = null;
  let temperature_c: number | null = null;
  let spo2: number | null = null;
  let blood_sugar: number | null = null;
  let sugar_test_type: "fasting" | "random" = "random";
  let body_weight_kg: number | null = null;
  let height_cm: number | null = null;
  let consciousness = "A";
  let notes = "";
  let symptoms: SymptomCode[] = [];

  let submitting = false;
  let formError = "";

  onMount(async () => {
    if (!$currentUser) {
      push("/login");
      return;
    }
    try {
      const res = await api.get<{ patients: Patient[] }>("/patients");
      patients = res.patients;
      patientId = $selectedPatientId || (patients[0]?.id ?? null);
    } catch {
      patients = [];
    }
  });

  async function handleSubmit(e: Event) {
    e.preventDefault();
    formError = "";
    if (!patientId) {
      formError = $t.triage.selectPatientFirst;
      return;
    }
    submitting = true;
    try {
      const res = await api.post<{ record: VitalsRecord }>("/triage", {
        patient_id: patientId,
        lang: $lang,
        systolic_bp,
        diastolic_bp,
        heart_rate,
        respiratory_rate,
        temperature_c,
        spo2,
        blood_sugar,
        sugar_test_type,
        body_weight_kg,
        height_cm,
        consciousness,
        notes,
        symptoms,
      });
      push(`/result/${res.record.id}`);
    } catch (err) {
      formError = err instanceof ApiError ? err.message : $t.common.error;
    } finally {
      submitting = false;
    }
  }
</script>

<div class="container triage-page">
  <h1>{$t.triage.title}</h1>

  {#if formError}
    <p class="error" role="alert">{formError}</p>
  {/if}

  <form class="card" on:submit={handleSubmit}>
    <div class="field">
      <label for="patient">{$t.patient.selectPatient}</label>
      <select id="patient" bind:value={patientId}>
        {#each patients as p (p.id)}
          <option value={p.id}>{p.name}{p.age ? ` (${p.age})` : ""}</option>
        {/each}
      </select>
    </div>

    <h3>{$t.triage.vitalsSection}</h3>
    <div class="grid-3">
      <div class="field">
        <label for="sbp">{$t.triage.systolic}</label>
        <input id="sbp" type="number" min="0" max="300" bind:value={systolic_bp} />
      </div>
      <div class="field">
        <label for="dbp">{$t.triage.diastolic}</label>
        <input id="dbp" type="number" min="0" max="200" bind:value={diastolic_bp} />
      </div>
      <div class="field">
        <label for="hr">{$t.triage.heartRate}</label>
        <input id="hr" type="number" min="0" max="260" bind:value={heart_rate} />
      </div>
      <div class="field">
        <label for="rr">{$t.triage.respRate}</label>
        <input id="rr" type="number" min="0" max="80" bind:value={respiratory_rate} />
      </div>
      <div class="field">
        <label for="temp">{$t.triage.temperature}</label>
        <input id="temp" type="number" step="0.1" min="25" max="45" bind:value={temperature_c} />
      </div>
      <div class="field">
        <label for="spo2">{$t.triage.spo2}</label>
        <input id="spo2" type="number" min="0" max="100" bind:value={spo2} />
      </div>
      <div class="field">
        <label for="sugar">{$t.triage.bloodSugar}</label>
        <input id="sugar" type="number" step="0.1" min="0" max="700" bind:value={blood_sugar} />
      </div>
      <div class="field">
        <label for="sugarType">{$t.triage.sugarType}</label>
        <select id="sugarType" bind:value={sugar_test_type}>
          <option value="fasting">{$t.triage.sugarFasting}</option>
          <option value="random">{$t.triage.sugarRandom}</option>
        </select>
      </div>
      <div class="field">
        <label for="conscious">{$t.triage.consciousness}</label>
        <select id="conscious" bind:value={consciousness}>
          <option value="A">{$t.triage.consciousA}</option>
          <option value="V">{$t.triage.consciousV}</option>
          <option value="P">{$t.triage.consciousP}</option>
          <option value="U">{$t.triage.consciousU}</option>
        </select>
      </div>
      <div class="field">
        <label for="weight">{$t.triage.weight}</label>
        <input id="weight" type="number" step="0.1" min="0" max="300" bind:value={body_weight_kg} />
      </div>
      <div class="field">
        <label for="height">{$t.triage.height}</label>
        <input id="height" type="number" step="0.1" min="0" max="250" bind:value={height_cm} />
      </div>
    </div>

    <h3>{$t.triage.symptomsSection}</h3>
    <SymptomChecklist bind:selected={symptoms} />

    <h3>{$t.triage.otherSection}</h3>
    <div class="field">
      <label for="notes">{$t.triage.notes}</label>
      <textarea id="notes" rows="3" bind:value={notes}></textarea>
    </div>

    <button class="btn-primary submit-btn" type="submit" disabled={submitting}>
      {submitting ? $t.triage.submitting : $t.triage.submit}
    </button>
  </form>
</div>

<style lang="scss">
  @use "../styles/variables" as v;

  .triage-page { padding: v.$space-6 0; }
  h3 { margin-top: v.$space-5; color: v.$color-navy; font-size: 1rem; text-transform: uppercase; letter-spacing: 0.03em; }
  .submit-btn { width: 100%; margin-top: v.$space-5; padding: 14px; font-size: 1.05rem; }
  .error { background: rgba(211,47,47,.08); color: v.$color-severity-red; padding: v.$space-3; border-radius: v.$radius-sm; font-weight: 600; }
</style>
