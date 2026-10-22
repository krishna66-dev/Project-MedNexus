<script lang="ts">
  import { onMount } from "svelte";
  import { link, push } from "svelte-spa-router";
  import { t, lang } from "../lib/i18n";
  import { api } from "../lib/api";
  import { currentUser, selectedPatientId } from "../lib/stores";
  import { formatDate, ageGender, riskBucket } from "../lib/format";
  import SeverityBadge from "../lib/components/SeverityBadge.svelte";
  import Icon from "../lib/components/art/Icon.svelte";
  import type { Patient, VitalsRecord } from "../lib/types";

  interface Row {
    patient: Patient;
    latest: VitalsRecord | null;
  }

  let patients: Patient[] = [];
  let latestByPatient: Record<string, VitalsRecord | null> = {};
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
    await loadLatestRecords();
  }

  // Latest assessment per patient (drives the risk badges and the stat cards).
  async function loadLatestRecords() {
    const entries = await Promise.all(
      patients.map(async (p) => {
        try {
          const res = await api.get<{ records: VitalsRecord[] }>(`/patients/${p.id}/history`);
          return [p.id, res.records[0] ?? null] as const;
        } catch {
          return [p.id, null] as const;
        }
      })
    );
    latestByPatient = Object.fromEntries(entries);
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

  // Most recently assessed first; never-assessed patients keep their server order after them.
  $: rows = patients
    .map((p): Row => ({ patient: p, latest: latestByPatient[p.id] ?? null }))
    .sort((a, b) => {
      if (a.latest && b.latest) return b.latest.created_at.localeCompare(a.latest.created_at);
      if (a.latest) return -1;
      if (b.latest) return 1;
      return 0;
    });

  $: counts = rows.reduce(
    (acc, r) => {
      if (r.latest) acc[riskBucket(r.latest.triage.severity_level)] += 1;
      return acc;
    },
    { high: 0, medium: 0, low: 0 }
  );
</script>

<div class="dashboard">
  <div class="dashboard__head">
    <div>
      <h1>{$t.dashboard.welcome}, {$currentUser?.name}</h1>
      <p>{$t.ui.dashboard.subtitle}</p>
    </div>
    <a href="#/triage" use:link class="btn-primary dashboard__cta">
      <Icon name="plus" size={16} strokeWidth={2.6} />
      {$t.ui.dashboard.newAssessment}
    </a>
  </div>

  <div class="stats">
    <div class="stat card">
      <span class="stat__icon teal"><Icon name="users" size={22} /></span>
      <div><small>{$t.ui.dashboard.totalPatients}</small><strong class="teal">{patients.length}</strong></div>
    </div>
    <div class="stat card">
      <span class="stat__icon red"><Icon name="heart" size={22} /></span>
      <div><small>{$t.ui.dashboard.highRisk}</small><strong class="red">{counts.high}</strong></div>
    </div>
    <div class="stat card">
      <span class="stat__icon amber"><Icon name="alert" size={22} /></span>
      <div><small>{$t.ui.dashboard.mediumRisk}</small><strong class="amber">{counts.medium}</strong></div>
    </div>
    <div class="stat card">
      <span class="stat__icon green"><Icon name="check-circle" size={22} /></span>
      <div><small>{$t.ui.dashboard.lowRisk}</small><strong class="green">{counts.low}</strong></div>
    </div>
  </div>

  <section class="card patients" id="patients">
    <div class="section-header">
      <h2>{$t.ui.dashboard.recentPatients}</h2>
      {#if $currentUser && $currentUser.role !== "self"}
        <button class="btn-outline" on:click={() => (showAddForm = !showAddForm)}>
          <Icon name="plus" size={15} strokeWidth={2.6} />
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
        <button class="btn-green" type="submit" disabled={saving}>{$t.patient.save}</button>
      </form>
    {/if}

    {#if loading}
      <p class="muted">{$t.common.loading}</p>
    {:else if patients.length === 0}
      <p class="muted">{$t.dashboard.noPatients}</p>
    {:else}
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>{$t.ui.dashboard.colName}</th>
              <th>{$t.ui.dashboard.colAgeGender}</th>
              <th>{$t.ui.dashboard.colDate}</th>
              <th>{$t.ui.dashboard.colRisk}</th>
              <th>{$t.ui.dashboard.colAction}</th>
            </tr>
          </thead>
          <tbody>
            {#each rows as r (r.patient.id)}
              <tr>
                <td data-label={$t.ui.dashboard.colName} class="name">
                  {r.patient.name}
                  {#if r.patient.village_ward}<small>{r.patient.village_ward}</small>{/if}
                </td>
                <td data-label={$t.ui.dashboard.colAgeGender}>{ageGender(r.patient.age, r.patient.gender)}</td>
                <td data-label={$t.ui.dashboard.colDate}>{r.latest ? formatDate(r.latest.created_at, $lang) : "—"}</td>
                <td data-label={$t.ui.dashboard.colRisk}>
                  {#if r.latest}
                    <SeverityBadge short level={r.latest.triage.severity_level} />
                  {:else}
                    <span class="muted small">{$t.ui.dashboard.notAssessed}</span>
                  {/if}
                </td>
                <td data-label={$t.ui.dashboard.colAction} class="actions">
                  {#if r.latest}
                    <a href="#/result/{r.latest.id}" use:link class="chip chip--view">{$t.ui.dashboard.view}</a>
                  {/if}
                  <button type="button" class="chip chip--assess" on:click={() => goAssess(r.patient.id)}>{$t.ui.dashboard.assess}</button>
                  <button type="button" class="chip" on:click={() => goHistory(r.patient.id)}>{$t.ui.dashboard.history}</button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </section>
</div>

<style lang="scss">
  @use "../styles/variables" as v;

  .dashboard { display: flex; flex-direction: column; gap: v.$space-5; }
  .dashboard__head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: v.$space-4;
    flex-wrap: wrap;
    h1 { font-size: 1.6rem; margin-bottom: 4px; }
    p { margin: 0; color: v.$color-text-muted; }
  }
  .dashboard__cta { padding: 12px 22px; }

  .stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: v.$space-4;
    @media (max-width: v.$bp-lg) { grid-template-columns: repeat(2, 1fr); }
    @media (max-width: 420px) { grid-template-columns: 1fr; }
  }
  .stat {
    display: flex;
    align-items: center;
    gap: v.$space-3;
    padding: v.$space-4;
    small { display: block; color: v.$color-text-muted; font-size: 0.8rem; }
    strong { display: block; font-size: 1.7rem; line-height: 1.2; }
  }
  .stat__icon {
    width: 46px;
    height: 46px;
    border-radius: v.$radius-md;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .stat__icon.teal { background: v.$color-teal-light; color: v.$color-teal; }
  .stat__icon.red { background: v.$color-sev-red-bg; color: v.$color-severity-red; }
  .stat__icon.amber { background: v.$color-sev-yellow-bg; color: #C27F00; }
  .stat__icon.green { background: v.$color-sev-green-bg; color: v.$color-severity-green; }
  strong.teal { color: v.$color-teal; }
  strong.red { color: v.$color-severity-red; }
  strong.amber { color: #C27F00; }
  strong.green { color: v.$color-severity-green; }

  .patients { scroll-margin-top: 80px; }
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: v.$space-3;
    flex-wrap: wrap;
    margin-bottom: v.$space-4;
    h2 { margin: 0; font-size: 1.1rem; }
    .btn-outline { padding: 8px 16px; font-size: 0.84rem; }
  }
  .add-patient-form {
    background: v.$color-bg-soft;
    border: 1px solid v.$color-border;
    border-radius: v.$radius-md;
    padding: v.$space-4;
    margin-bottom: v.$space-4;
  }
  .muted { color: v.$color-text-muted; margin: 0; }
  .small { font-size: 0.82rem; }

  .table-wrap { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; }
  thead th {
    text-align: left;
    padding: 12px v.$space-3;
    background: v.$color-bg-soft;
    color: v.$color-text-muted;
    font-size: 0.78rem;
    font-weight: 600;
    &:first-child { border-radius: v.$radius-sm 0 0 v.$radius-sm; }
    &:last-child { border-radius: 0 v.$radius-sm v.$radius-sm 0; }
  }
  tbody td {
    padding: 14px v.$space-3;
    border-bottom: 1px solid v.$color-border;
    font-size: 0.88rem;
    vertical-align: middle;
  }
  tbody tr:last-child td { border-bottom: 0; }
  td.name { font-weight: 600; color: v.$color-navy-text; small { display: block; font-weight: 400; color: v.$color-text-muted; font-size: 0.76rem; } }
  td.actions { display: flex; gap: 6px; flex-wrap: wrap; }

  .chip {
    border: 0;
    background: #EAF3F8;
    color: v.$color-blue-link;
    font: inherit;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 6px 12px;
    border-radius: v.$radius-sm;
    cursor: pointer;
    text-decoration: none;
    &:hover { background: #D8EAF3; text-decoration: none; }
  }
  .chip--assess { background: v.$color-teal-light; color: v.$color-teal; &:hover { background: #CDEBEA; } }

  @media (max-width: v.$bp-md) {
    thead { display: none; }
    table, tbody, tr, td { display: block; width: 100%; }
    tbody tr { padding: v.$space-3 0; border-bottom: 1px solid v.$color-border; &:last-child { border-bottom: 0; } }
    tbody td { border: 0; padding: 5px 0; display: flex; justify-content: space-between; gap: v.$space-3; align-items: center; }
    tbody td::before { content: attr(data-label); color: v.$color-text-muted; font-size: 0.76rem; font-weight: 600; }
    td.name { display: block; &::before { display: none; } }
    td.actions { justify-content: flex-start; &::before { display: none; } }
  }
</style>
