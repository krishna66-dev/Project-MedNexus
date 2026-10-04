<script lang="ts">
  import { onMount } from "svelte";
  import { link, push } from "svelte-spa-router";
  import { t } from "../lib/i18n";
  import { api } from "../lib/api";
  import { currentUser, selectedPatientId } from "../lib/stores";
  import type { Patient } from "../lib/types";

  let patients: Patient[] = [];
  let loading = true;

  // New patient form (ASHA/ANM only)
  let showAddForm = false;
  let newName = "";
  let newDob = "";
  let newGender = "";
  let newVillage = "";
  let newContact = "";
  let saving = false;

  onMount(async () => {
    if (!$currentUser) {
      push("/login");
      return;
    }
    await loadPatients();
  });

  async function loadPatients() {
    loading = true;
    try {
      const res = await api.get<{ patients: Patient[] }>("/patients");
      patients = res.patients;
    } catch {
      patients = [];
    } finally {
      loading = false;
    }
  }

  async function addPatient(e: Event) {
    e.preventDefault();
    saving = true;
    try {
      await api.post("/patients", {
        name: newName,
        dob: newDob || undefined,
        gender: newGender || undefined,
        village_ward: newVillage || undefined,
        contact_number: newContact || undefined,
      });
      newName = newDob = newGender = newVillage = newContact = "";
      showAddForm = false;
      await loadPatients();
    } finally {
      saving = false;
    }
  }

  function goAssess(patientId: string) {
    selectedPatientId.set(patientId);
    push("/triage");
  }

  function goHistory(patientId: string) {
    push(`/history/${patientId}`);
  }
</script>

<div class="container dashboard">
  <h1>{$t.dashboard.welcome}, {$currentUser?.name}</h1>

  <div class="dashboard__actions">
    <a href="#/triage" use:link class="btn-primary">{$t.dashboard.quickAction}</a>
  </div>

  <section class="card">
    <div class="section-header">
      <h2>{$t.dashboard.myPatients}</h2>
      {#if $currentUser && $currentUser.role !== "self"}
        <button class="btn-outline" on:click={() => (showAddForm = !showAddForm)}>
          {$t.dashboard.addPatient}
        </button>
      {/if}
    </div>

    {#if showAddForm}
      <form class="add-patient-form" on:submit={addPatient}>
        <div class="grid-3">
          <div class="field">
            <label for="pname">{$t.patient.name}</label>
            <input id="pname" required bind:value={newName} />
          </div>
          <div class="field">
            <label for="pdob">{$t.patient.dob}</label>
            <input id="pdob" type="date" bind:value={newDob} max={new Date().toISOString().split("T")[0]} />
          </div>
          <div class="field">
            <label for="pgender">{$t.patient.gender}</label>
            <select id="pgender" bind:value={newGender}>
              <option value="">-</option>
              <option value="male">{$t.patient.genderMale}</option>
              <option value="female">{$t.patient.genderFemale}</option>
              <option value="other">{$t.patient.genderOther}</option>
            </select>
          </div>
        </div>
        <div class="grid-2">
          <div class="field">
            <label for="pvillage">{$t.patient.village}</label>
            <input id="pvillage" bind:value={newVillage} />
          </div>
          <div class="field">
            <label for="pcontact">{$t.patient.contact}</label>
            <input id="pcontact" type="tel" bind:value={newContact} />
          </div>
        </div>
        <button class="btn-primary" type="submit" disabled={saving}>{$t.patient.save}</button>
      </form>
    {/if}

    {#if loading}
      <p>{$t.common.loading}</p>
    {:else if patients.length === 0}
      <p>{$t.dashboard.noPatients}</p>
    {:else}
      <ul class="patient-list">
        {#each patients as p (p.id)}
          <li class="patient-row">
            <div>
              <strong>{p.name}</strong>
              <span class="muted">
                {p.age ? `\u00b7 ${p.age}` : ""} {p.village_ward ? `\u00b7 ${p.village_ward}` : ""}
              </span>
            </div>
            <div class="patient-row__actions">
              <button class="btn-saffron" on:click={() => goAssess(p.id)}>{$t.nav.newAssessment}</button>
              <button class="btn-outline" on:click={() => goHistory(p.id)}>{$t.nav.history}</button>
            </div>
          </li>
        {/each}
      </ul>
    {/if}
  </section>
</div>

<style lang="scss">
  @use "../styles/variables" as v;

  .dashboard { padding: v.$space-6 0; display: flex; flex-direction: column; gap: v.$space-5; }
  .dashboard__actions { margin-bottom: v.$space-2; }
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: v.$space-4;
  }
  .add-patient-form {
    background: v.$color-blue-light;
    border-radius: v.$radius-md;
    padding: v.$space-4;
    margin-bottom: v.$space-4;
  }
  .patient-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: v.$space-2; }
  .patient-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: v.$space-3;
    border: 1px solid v.$color-border;
    border-radius: v.$radius-md;
    flex-wrap: wrap;
    gap: v.$space-2;
  }
  .patient-row__actions { display: flex; gap: v.$space-2; }
  .muted { color: v.$color-text-muted; font-size: 0.85rem; margin-left: 6px; }
</style>
