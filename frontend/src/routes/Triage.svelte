<script lang="ts">
  import { onMount } from "svelte";
  import { link, push } from "svelte-spa-router";
  import { t, lang } from "../lib/i18n";
  import { api, ApiError } from "../lib/api";
  import { currentUser, selectedPatientId } from "../lib/stores";
  import SymptomChecklist from "../lib/components/SymptomChecklist.svelte";
  import Icon from "../lib/components/art/Icon.svelte";
  import WorkerBust from "../lib/components/art/WorkerBust.svelte";
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

  // Wizard state: 1 Patient Details · 2 Vital Signs · 3 Symptoms · 4 Review & Submit
  let step = 1;
  const LAST_STEP = 4;

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

  $: patient = patients.find((p) => p.id === patientId) ?? null;

  function genderLabel(g: string | null | undefined): string {
    if (!g) return "";
    const v = g.toLowerCase();
    if (v === "male") return $t.patient.genderMale;
    if (v === "female") return $t.patient.genderFemale;
    return $t.patient.genderOther;
  }

  function consciousLabel(code: string): string {
    if (code === "V") return $t.triage.consciousV;
    if (code === "P") return $t.triage.consciousP;
    if (code === "U") return $t.triage.consciousU;
    return $t.triage.consciousA;
  }

  function next() {
    formError = "";
    if (step === 1 && !patientId) {
      formError = $t.triage.selectPatientFirst;
      return;
    }
    if (step < LAST_STEP) step += 1;
  }

  function back() {
    formError = "";
    if (step > 1) step -= 1;
    else push("/dashboard");
  }

  function goToStep(n: number) {
    if (n < step) {
      formError = "";
      step = n;
    }
  }

  async function handleSubmit(e: Event) {
    e.preventDefault();
    // Pressing Enter on an earlier step should just move forward.
    if (step < LAST_STEP) {
      next();
      return;
    }
    formError = "";
    if (!patientId) {
      formError = $t.triage.selectPatientFirst;
      step = 1;
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

  // Values shown on the review step (only what was actually entered)
  $: vitalRows = [
    [$t.triage.systolic, systolic_bp],
    [$t.triage.diastolic, diastolic_bp],
    [$t.triage.heartRate, heart_rate],
    [$t.triage.respRate, respiratory_rate],
    [$t.triage.temperature, temperature_c],
    [$t.triage.spo2, spo2],
    [$t.triage.bloodSugar, blood_sugar === null ? null : `${blood_sugar} (${sugar_test_type === "fasting" ? $t.triage.sugarFasting : $t.triage.sugarRandom})`],
    [$t.triage.weight, body_weight_kg],
    [$t.triage.height, height_cm],
    [$t.triage.consciousness, consciousLabel(consciousness)],
  ].filter(([, v]) => v !== null && v !== "") as [string, string | number][];
</script>

<div class="triage">
  <ol class="stepper" aria-label={$t.triage.title}>
    {#each $t.ui.triage.steps as label, i}
      {@const n = i + 1}
      <li class:done={n < step} class:current={n === step}>
        <button type="button" class="stepper__dot" disabled={n >= step} on:click={() => goToStep(n)} aria-current={n === step ? "step" : undefined}>
          {#if n < step}<Icon name="check" size={16} strokeWidth={3} />{:else}{n}{/if}
        </button>
        <span class="stepper__label">{label}</span>
      </li>
    {/each}
  </ol>

  <div class="triage__body">
    <form class="card triage__form" on:submit={handleSubmit}>
      {#if formError}
        <p class="alert-error" role="alert">{formError}</p>
      {/if}

      {#if step === 1}
        <h2>{$t.ui.triage.patientDetails}</h2>

        {#if patients.length === 0}
          <p class="muted">{$t.ui.triage.noPatientsYet}</p>
          <a href="#/dashboard" use:link class="btn-outline">{$t.ui.triage.goDashboard}</a>
        {:else}
          <div class="field">
            <label for="patient">{$t.patient.selectPatient} <span class="req">*</span></label>
            <select id="patient" bind:value={patientId}>
              {#each patients as p (p.id)}
                <option value={p.id}>{p.name}{p.age ? ` (${p.age})` : ""}</option>
              {/each}
            </select>
          </div>

          <div class="grid-2">
            <div class="field">
              <label for="pd-name">{$t.ui.triage.name} <span class="req">*</span></label>
              <input id="pd-name" readonly value={patient?.name ?? ""} />
            </div>
            <div class="field">
              <label for="pd-age">{$t.ui.triage.age} <span class="req">*</span></label>
              <input id="pd-age" readonly value={patient?.age ?? ""} />
            </div>
            <div class="field">
              <label for="pd-gender">{$t.ui.triage.gender} <span class="req">*</span></label>
              <input id="pd-gender" readonly value={genderLabel(patient?.gender)} />
            </div>
            <div class="field">
              <label for="pd-mobile">{$t.ui.triage.mobile}</label>
              <input id="pd-mobile" readonly value={patient?.contact_number ?? ""} />
            </div>
          </div>
          <div class="field">
            <label for="pd-address">{$t.ui.triage.address} <span class="opt">{$t.ui.triage.optional}</span></label>
            <textarea id="pd-address" rows="2" readonly>{patient?.village_ward ?? ""}</textarea>
          </div>
        {/if}
      {:else if step === 2}
        <h2>{$t.triage.vitalsSection}</h2>
        <div class="grid-2">
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
      {:else if step === 3}
        <h2>{$t.triage.symptomsSection}</h2>
        <SymptomChecklist bind:selected={symptoms} />
      {:else}
        <h2>{$t.ui.triage.reviewTitle}</h2>
        <p class="muted hint">{$t.ui.triage.reviewHint}</p>

        <div class="review">
          <div class="review__block">
            <h3>{$t.ui.triage.patientDetails}</h3>
            <dl>
              <div><dt>{$t.ui.triage.name}</dt><dd>{patient?.name ?? $t.ui.triage.notProvided}</dd></div>
              <div><dt>{$t.ui.triage.age}</dt><dd>{patient?.age ?? $t.ui.triage.notProvided}</dd></div>
              <div><dt>{$t.ui.triage.gender}</dt><dd>{genderLabel(patient?.gender) || $t.ui.triage.notProvided}</dd></div>
            </dl>
          </div>

          <div class="review__block">
            <h3>{$t.ui.triage.vitalSigns}</h3>
            {#if vitalRows.length === 0}
              <p class="muted">{$t.ui.triage.notProvided}</p>
            {:else}
              <dl>
                {#each vitalRows as [label, value]}
                  <div><dt>{label}</dt><dd>{value}</dd></div>
                {/each}
              </dl>
            {/if}
          </div>

          <div class="review__block">
            <h3>{$t.triage.symptomsSection}</h3>
            {#if symptoms.length === 0}
              <p class="muted">{$t.ui.triage.noneSelected}</p>
            {:else}
              <ul class="tags">
                {#each symptoms as code}<li>{$t.symptoms[code]}</li>{/each}
              </ul>
            {/if}
          </div>
        </div>

        <div class="field notes">
          <label for="notes">{$t.triage.notes} <span class="opt">{$t.ui.triage.optional}</span></label>
          <textarea id="notes" rows="3" bind:value={notes}></textarea>
        </div>
      {/if}

      <div class="triage__actions">
        <button type="button" class="btn-outline" on:click={back}>{$t.ui.triage.back}</button>
        {#if step < LAST_STEP}
          <button type="button" class="btn-primary" on:click={next} disabled={patients.length === 0}>{$t.ui.triage.next}</button>
        {:else}
          <button class="btn-green" type="submit" disabled={submitting}>
            {submitting ? $t.triage.submitting : $t.triage.submit}
          </button>
        {/if}
      </div>
    </form>

    <aside class="help" aria-label={$t.ui.triage.helpTitle}>
      <h3>{$t.ui.triage.helpTitle}</h3>
      <p>{$t.ui.triage.helpBody}</p>
      <div class="help__art" aria-hidden="true"><WorkerBust tablet={false} /></div>
    </aside>
  </div>
</div>

<style lang="scss">
  @use "../styles/variables" as v;

  .triage { display: flex; flex-direction: column; gap: v.$space-5; }

  /* ---------- Stepper ---------- */
  .stepper {
    list-style: none;
    margin: 0;
    padding: 0;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    position: relative;

    li {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      position: relative;
      text-align: center;

      // connector to the next step
      &:not(:last-child)::after {
        content: "";
        position: absolute;
        top: 19px;
        left: calc(50% + 24px);
        right: calc(-50% + 24px);
        height: 3px;
        border-radius: 2px;
        background: v.$color-border;
      }
      &.done:not(:last-child)::after { background: v.$color-green; }
    }
  }
  .stepper__dot {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    border: 0;
    background: #D6E6F5;
    color: v.$color-teal;
    font: inherit;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: default;
    transition: background-color 0.15s ease;
  }
  li.current .stepper__dot { background: v.$color-green; color: #fff; box-shadow: 0 0 0 5px rgba(14, 159, 110, 0.18); }
  li.done .stepper__dot { background: v.$color-green; color: #fff; cursor: pointer; }
  .stepper__label { font-size: 0.8rem; font-weight: 600; color: v.$color-text-muted; }
  li.current .stepper__label { color: v.$color-navy-text; }
  @media (max-width: v.$bp-sm) { .stepper__label { font-size: 0.68rem; } }

  /* ---------- Body ---------- */
  .triage__body {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 260px;
    gap: v.$space-5;
    align-items: start;
    @media (max-width: v.$bp-lg) { grid-template-columns: 1fr; }
  }
  .triage__form {
    padding: v.$space-6;
    @media (max-width: v.$bp-sm) { padding: v.$space-4; }
    h2 { font-size: 1.3rem; margin-bottom: v.$space-5; }
  }
  .muted { color: v.$color-text-muted; }
  .hint { margin-top: -12px; font-size: 0.88rem; }

  .triage__actions {
    display: flex;
    justify-content: space-between;
    gap: v.$space-3;
    margin-top: v.$space-5;
    padding-top: v.$space-4;
    border-top: 1px solid v.$color-border;
    .btn-outline, .btn-primary, .btn-green { min-width: 120px; }
  }

  /* ---------- Review ---------- */
  .review { display: grid; gap: v.$space-4; }
  .review__block {
    background: v.$color-bg-soft;
    border: 1px solid v.$color-border;
    border-radius: v.$radius-md;
    padding: v.$space-4;
    h3 { font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; color: v.$color-teal; margin-bottom: v.$space-3; }
    dl { margin: 0; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px v.$space-4; @media (max-width: v.$bp-sm) { grid-template-columns: 1fr; } }
    dl > div { display: flex; flex-direction: column; gap: 2px; }
    dt { font-size: 0.76rem; color: v.$color-text-muted; }
    dd { margin: 0; font-weight: 600; font-size: 0.92rem; }
    p { margin: 0; }
  }
  .tags {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    li { background: v.$color-teal-light; color: v.$color-teal-dark; font-size: 0.82rem; font-weight: 600; padding: 5px 12px; border-radius: v.$radius-pill; }
  }
  .notes { margin-top: v.$space-4; margin-bottom: 0; }

  /* ---------- Help card ---------- */
  .help {
    background: linear-gradient(180deg, #E6F1FA 0%, #F1F7FC 100%);
    border-radius: v.$radius-lg;
    padding: v.$space-5;
    h3 { font-size: 1rem; margin-bottom: v.$space-2; }
    p { margin: 0; font-size: 0.86rem; color: v.$color-text-muted; }
  }
  .help__art { width: 150px; margin: v.$space-5 0 0 auto; }
  @media (max-width: v.$bp-lg) { .help__art { display: none; } }
</style>
