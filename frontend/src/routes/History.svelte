<script lang="ts">
  import { onMount } from "svelte";
  import { link } from "svelte-spa-router";
  import { t } from "../lib/i18n";
  import { api } from "../lib/api";
  import SeverityBadge from "../lib/components/SeverityBadge.svelte";
  import type { VitalsRecord } from "../lib/types";

  export let params: { patientId: string } = { patientId: "" };

  let records: VitalsRecord[] = [];
  let loading = true;

  onMount(async () => {
    try {
      const res = await api.get<{ records: VitalsRecord[] }>(`/patients/${params.patientId}/history`);
      records = res.records;
    } finally {
      loading = false;
    }
  });

  function formatDate(iso: string) {
    return new Date(iso).toLocaleString();
  }
</script>

<div class="container history-page">
  <h1>{$t.history.title}</h1>

  {#if loading}
    <p>{$t.common.loading}</p>
  {:else if records.length === 0}
    <p>{$t.dashboard.noRecords}</p>
  {:else}
    <div class="card">
      <table>
        <thead>
          <tr>
            <th>{$t.history.date}</th>
            <th>{$t.history.severity}</th>
            <th>{$t.history.score}</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {#each records as r (r.id)}
            <tr>
              <td>{formatDate(r.created_at)}</td>
              <td><SeverityBadge level={r.triage.severity_level} label={r.triage.severity_label} /></td>
              <td>{r.triage.severity_score}</td>
              <td><a href="#/result/{r.id}" use:link>{$t.history.view}</a></td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

<style lang="scss">
  @use "../styles/variables" as v;

  .history-page { padding: v.$space-6 0; }
  table { width: 100%; border-collapse: collapse; }
  th, td { text-align: left; padding: v.$space-3; border-bottom: 1px solid v.$color-border; font-size: 0.92rem; }
  th { color: v.$color-text-muted; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.04em; }
</style>
