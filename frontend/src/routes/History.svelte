<script lang="ts">
  import { onMount } from "svelte";
  import { link } from "svelte-spa-router";
  import { t, lang } from "../lib/i18n";
  import { api } from "../lib/api";
  import { formatDateTime, ageGender, toDateKey } from "../lib/format";
  import SeverityBadge from "../lib/components/SeverityBadge.svelte";
  import Icon from "../lib/components/art/Icon.svelte";
  import type { Patient, VitalsRecord } from "../lib/types";

  // `/history/<patientId>` shows one patient; `/history/all` shows every patient's assessments.
  export let params: { patientId: string } = { patientId: "" };

  const PAGE_SIZE = 8;

  let records: VitalsRecord[] = [];
  let patients: Patient[] = [];
  let loading = true;

  let search = "";
  let from = "";
  let to = "";
  // Filters are applied when the user presses "Filter" (or Enter in the search box).
  let applied = { search: "", from: "", to: "" };
  let page = 1;

  $: scopedPatientId = params.patientId && params.patientId !== "all" ? params.patientId : null;
  $: patientById = Object.fromEntries(patients.map((p) => [p.id, p])) as Record<string, Patient>;
  $: scopedPatient = scopedPatientId ? patientById[scopedPatientId] ?? null : null;

  onMount(async () => {
    try {
      try {
        const pres = await api.get<{ patients: Patient[] }>("/patients");
        patients = pres.patients;
      } catch {
        patients = [];
      }

      if (scopedPatientId) {
        const res = await api.get<{ records: VitalsRecord[] }>(`/patients/${scopedPatientId}/history`);
        records = res.records;
      } else {
        const lists = await Promise.all(
          patients.map(async (p) => {
            try {
              const res = await api.get<{ records: VitalsRecord[] }>(`/patients/${p.id}/history`);
              return res.records;
            } catch {
              return [] as VitalsRecord[];
            }
          })
        );
        records = lists.flat().sort((a, b) => b.created_at.localeCompare(a.created_at));
      }
    } finally {
      loading = false;
    }
  });

  function applyFilters(e?: Event) {
    e?.preventDefault();
    applied = { search: search.trim().toLowerCase(), from, to };
    page = 1;
  }

  function clearFilters() {
    search = from = to = "";
    applied = { search: "", from: "", to: "" };
    page = 1;
  }

  $: filtered = records.filter((r) => {
    const name = (patientById[r.patient_id]?.name ?? "").toLowerCase();
    if (applied.search && !name.includes(applied.search)) return false;
    const day = toDateKey(r.created_at);
    if (applied.from && day < applied.from) return false;
    if (applied.to && day > applied.to) return false;
    return true;
  });
  $: pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  $: if (page > pageCount) page = pageCount;
  $: visible = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  $: hasFilters = !!(applied.search || applied.from || applied.to);
</script>

<div class="history">
  <h1>{$t.history.title}</h1>

  {#if scopedPatient}
    <p class="scope">
      {$t.ui.history.showingFor} <strong>{scopedPatient.name}</strong>
      <a href="#/history/all" use:link>{$t.ui.history.allPatients}</a>
    </p>
  {/if}

  <form class="filters card" on:submit={applyFilters}>
    <div class="filters__search">
      <Icon name="search" size={18} />
      <input type="search" bind:value={search} placeholder={$t.ui.history.searchPh} aria-label={$t.ui.history.searchPh} />
    </div>
    <div class="filters__dates">
      <label>
        <span>{$t.ui.history.from}</span>
        <input type="date" bind:value={from} aria-label={$t.ui.history.from} />
      </label>
      <label>
        <span>{$t.ui.history.to}</span>
        <input type="date" bind:value={to} aria-label={$t.ui.history.to} />
      </label>
    </div>
    <div class="filters__btns">
      <button type="submit" class="btn-primary">{$t.ui.history.filter}</button>
      {#if hasFilters || search || from || to}
        <button type="button" class="btn-outline" on:click={clearFilters}>{$t.ui.history.clear}</button>
      {/if}
    </div>
  </form>

  {#if loading}
    <p class="muted">{$t.common.loading}</p>
  {:else if records.length === 0}
    <p class="muted">{$t.dashboard.noRecords}</p>
  {:else if filtered.length === 0}
    <p class="muted">{$t.ui.history.noMatches}</p>
  {:else}
    <div class="card table-card">
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>{$t.ui.history.colDateTime}</th>
              <th>{$t.ui.history.colPatient}</th>
              <th>{$t.ui.history.colAgeGender}</th>
              <th>{$t.ui.history.colRisk}</th>
              <th>{$t.ui.history.colAction}</th>
            </tr>
          </thead>
          <tbody>
            {#each visible as r (r.id)}
              {@const p = patientById[r.patient_id]}
              <tr>
                <td data-label={$t.ui.history.colDateTime}>{formatDateTime(r.created_at, $lang)}</td>
                <td data-label={$t.ui.history.colPatient} class="name">{p?.name ?? "—"}</td>
                <td data-label={$t.ui.history.colAgeGender}>{ageGender(p?.age, p?.gender)}</td>
                <td data-label={$t.ui.history.colRisk}>
                  <SeverityBadge short level={r.triage.severity_level} label={r.triage.severity_label} />
                </td>
                <td data-label={$t.ui.history.colAction}><a href="#/result/{r.id}" use:link class="chip">{$t.history.view}</a></td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>

      {#if pageCount > 1}
        <nav class="pager" aria-label="Pagination">
          <button type="button" aria-label={$t.ui.history.prev} disabled={page === 1} on:click={() => (page -= 1)}>
            <Icon name="chevron-left" size={16} />
          </button>
          {#each Array.from({ length: pageCount }, (_, i) => i + 1) as n}
            <button type="button" class:active={n === page} aria-current={n === page ? "page" : undefined} on:click={() => (page = n)}>{n}</button>
          {/each}
          <button type="button" aria-label={$t.ui.history.next} disabled={page === pageCount} on:click={() => (page += 1)}>
            <Icon name="chevron-right" size={16} />
          </button>
        </nav>
      {/if}
    </div>
  {/if}
</div>

<style lang="scss">
  @use "../styles/variables" as v;

  .history { display: flex; flex-direction: column; gap: v.$space-4; }
  h1 { font-size: 1.4rem; margin: 0; }
  .muted { color: v.$color-text-muted; margin: 0; }
  .scope { margin: 0; font-size: 0.88rem; color: v.$color-text-muted; strong { color: v.$color-navy-text; } a { margin-left: v.$space-3; font-weight: 600; } }

  .filters {
    display: flex;
    align-items: flex-end;
    gap: v.$space-4;
    flex-wrap: wrap;
    padding: v.$space-4;
  }
  .filters__search {
    flex: 1 1 260px;
    display: flex;
    align-items: center;
    gap: 10px;
    border: 1.5px solid v.$color-border;
    border-radius: v.$radius-md;
    padding: 0 14px;
    background: #fff;
    color: v.$color-text-muted;
    &:focus-within { border-color: v.$color-teal; box-shadow: 0 0 0 3px rgba(15, 124, 128, 0.12); }
    input { flex: 1; border: 0; outline: 0; padding: 12px 0; font: inherit; font-size: 0.92rem; background: transparent; min-width: 0; }
  }
  .filters__dates {
    display: flex;
    gap: v.$space-3;
    flex-wrap: wrap;
    label { display: flex; flex-direction: column; gap: 4px; font-size: 0.76rem; font-weight: 600; color: v.$color-text-muted; }
    input { font: inherit; font-size: 0.88rem; padding: 9px 12px; border: 1.5px solid v.$color-border; border-radius: v.$radius-md; background: #fff; color: v.$color-text; &:focus { outline: 0; border-color: v.$color-teal; } }
  }
  .filters__btns { display: flex; gap: v.$space-2; .btn-primary, .btn-outline { padding: 10px 22px; } }

  .table-card { padding: v.$space-3 v.$space-4 v.$space-4; }
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
  tbody td { padding: 14px v.$space-3; border-bottom: 1px solid v.$color-border; font-size: 0.88rem; }
  tbody tr:last-child td { border-bottom: 0; }
  td.name { font-weight: 600; color: v.$color-navy-text; }
  .chip {
    background: #EAF3F8;
    color: v.$color-blue-link;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: v.$radius-sm;
    text-decoration: none;
    &:hover { background: #D8EAF3; text-decoration: none; }
  }

  .pager {
    display: flex;
    justify-content: flex-end;
    gap: 6px;
    margin-top: v.$space-4;
    button {
      min-width: 34px;
      height: 34px;
      border: 1px solid v.$color-border;
      background: #fff;
      border-radius: v.$radius-sm;
      font: inherit;
      font-size: 0.84rem;
      font-weight: 600;
      color: v.$color-navy-text;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      &:hover:not(:disabled) { border-color: v.$color-teal; }
      &:disabled { opacity: 0.45; cursor: not-allowed; }
      &.active { background: v.$color-teal; border-color: v.$color-teal; color: #fff; }
    }
  }

  @media (max-width: v.$bp-md) {
    thead { display: none; }
    table, tbody, tr, td { display: block; width: 100%; }
    tbody tr { padding: v.$space-3 0; border-bottom: 1px solid v.$color-border; &:last-child { border-bottom: 0; } }
    tbody td { border: 0; padding: 5px 0; display: flex; justify-content: space-between; align-items: center; gap: v.$space-3; }
    tbody td::before { content: attr(data-label); color: v.$color-text-muted; font-size: 0.76rem; font-weight: 600; }
  }
</style>
