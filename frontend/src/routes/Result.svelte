<script lang="ts">
  import { onMount } from "svelte";
  import { link } from "svelte-spa-router";
  import { t } from "../lib/i18n";
  import { api } from "../lib/api";
  import SeverityBadge from "../lib/components/SeverityBadge.svelte";
  import type { VitalsRecord } from "../lib/types";

  export let params: { id: string } = { id: "" };

  let record: VitalsRecord | null = null;
  let loading = true;

  onMount(async () => {
    try {
      const res = await api.get<{ record: VitalsRecord }>(`/records/${params.id}`);
      record = res.record;
    } finally {
      loading = false;
    }
  });
</script>

<div class="container result-page">
  {#if loading}
    <p>{$t.common.loading}</p>
  {:else if !record}
    <p>{$t.common.error}</p>
  {:else}
    <div class="card result-card severity-{record.triage.severity_level}">
      <p class="result-eyebrow">{$t.result.title}</p>
      <SeverityBadge level={record.triage.severity_level} label={record.triage.severity_label} size="lg" />

      <div class="result-score">
        <span class="result-score__label">{$t.result.score}</span>
        <span class="result-score__value">{record.triage.severity_score}</span>
      </div>

      <div class="result-block">
        <h3>{$t.result.recommendation}</h3>
        <p>{record.triage.recommendation}</p>
      </div>

      <div class="result-block">
        <h3>{$t.result.factors}</h3>
        {#if record.triage.contributing_factors.length === 0}
          <p class="muted">{$t.result.noFactors}</p>
        {:else}
          <ul>
            {#each record.triage.contributing_factors as f}
              <li>{f}</li>
            {/each}
          </ul>
        {/if}
      </div>

      <p class="disclaimer">{$t.result.disclaimer}</p>

      <div class="result-actions">
        <a href="#/triage" use:link class="btn-primary">{$t.result.newAssessment}</a>
        <a href="#/history/{record.patient_id}" use:link class="btn-outline">{$t.result.viewHistory}</a>
      </div>
    </div>
  {/if}
</div>

<style lang="scss">
  @use "../styles/variables" as v;

  .result-page { padding: v.$space-6 0; display: flex; justify-content: center; }
  .result-card {
    max-width: 560px;
    width: 100%;
    border-top: 6px solid v.$color-border;

    &.severity-green  { border-top-color: v.$color-severity-green; }
    &.severity-yellow { border-top-color: v.$color-severity-yellow; }
    &.severity-orange { border-top-color: v.$color-severity-orange; }
    &.severity-red    { border-top-color: v.$color-severity-red; }
  }
  .result-eyebrow { color: v.$color-text-muted; font-weight: 700; text-transform: uppercase; font-size: 0.78rem; letter-spacing: 0.05em; margin-bottom: v.$space-2; }
  .result-score {
    display: flex;
    align-items: baseline;
    gap: v.$space-2;
    margin: v.$space-4 0;
  }
  .result-score__label { color: v.$color-text-muted; font-weight: 600; }
  .result-score__value { font-size: 2rem; font-weight: 800; color: v.$color-navy-dark; }
  .result-block { margin: v.$space-4 0; }
  .result-block h3 { font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.03em; color: v.$color-navy; }
  .result-block ul { margin: 0; padding-left: 20px; }
  .muted { color: v.$color-text-muted; }
  .disclaimer { margin: v.$space-4 0; }
  .result-actions { display: flex; gap: v.$space-3; flex-wrap: wrap; }
</style>
