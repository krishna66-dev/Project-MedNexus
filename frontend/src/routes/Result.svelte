<script lang="ts">
  import { onMount } from "svelte";
  import { link } from "svelte-spa-router";
  import { t, lang } from "../lib/i18n";
  import { api } from "../lib/api";
  import SeverityBadge from "../lib/components/SeverityBadge.svelte";
  import type { VitalsRecord } from "../lib/types";

  export let params: { id: string } = { id: "" };

  let record: VitalsRecord | null = null;
  let loading = true;

  $: plan = record ? record.triage.action_plan[$lang] : null;

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

      <div class="result-block recommendation">
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

      {#if plan}
        <section class="care-plan severity-{record.triage.severity_level}">
          <div class="care-plan__header">
            <div>
              <p class="care-plan__eyebrow">{$t.result.ashaPlan}</p>
              <h2>{plan.title}</h2>
            </div>
            <span class="urgency">{plan.urgency}</span>
          </div>

          <div class="plan-section">
            <h3>🩺 {$t.result.whatToDo}</h3>
            <ol>
              {#each plan.immediate_actions as action}
                <li>{action}</li>
              {/each}
            </ol>
          </div>

          <div class="plan-section avoid">
            <h3>⚠️ {$t.result.whatToAvoid}</h3>
            <ul>
              {#each plan.avoid as item}
                <li>{item}</li>
              {/each}
            </ul>
          </div>

          <div class="plan-section referral">
            <h3>🏥 {$t.result.referral}</h3>
            <p>{plan.referral}</p>
          </div>

          <div class="plan-section follow-up">
            <h3>🔄 {$t.result.followUp}</h3>
            <p>{plan.follow_up}</p>
          </div>
        </section>
      {/if}

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

  .recommendation {
    background: rgba(16, 55, 92, .045);
    border-radius: v.$radius-md;
    padding: v.$space-4;
  }
  .care-plan {
    margin: v.$space-6 0;
    padding: v.$space-5;
    border-radius: v.$radius-md;
    border: 1px solid v.$color-border;
    background: #fff;
    box-shadow: 0 8px 24px rgba(15, 23, 42, .06);
  }
  .care-plan.severity-green { border-left: 5px solid v.$color-severity-green; }
  .care-plan.severity-yellow { border-left: 5px solid v.$color-severity-yellow; }
  .care-plan.severity-orange { border-left: 5px solid v.$color-severity-orange; }
  .care-plan.severity-red { border-left: 5px solid v.$color-severity-red; }
  .care-plan__header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: v.$space-4;
    margin-bottom: v.$space-5;
  }
  .care-plan__eyebrow {
    margin: 0 0 v.$space-1;
    color: v.$color-text-muted;
    font-size: .72rem;
    font-weight: 800;
    letter-spacing: .08em;
    text-transform: uppercase;
  }
  .care-plan h2 { margin: 0; font-size: 1.25rem; color: v.$color-navy-dark; }
  .urgency {
    flex: 0 0 auto;
    padding: 7px 10px;
    border-radius: 999px;
    background: rgba(16, 55, 92, .08);
    color: v.$color-navy;
    font-size: .78rem;
    font-weight: 800;
  }
  .plan-section {
    padding: v.$space-4 0;
    border-top: 1px solid v.$color-border;
  }
  .plan-section h3 { margin: 0 0 v.$space-2; font-size: .92rem; text-transform: none; letter-spacing: 0; }
  .plan-section ol, .plan-section ul { margin: 0; padding-left: 22px; }
  .plan-section li { margin: 7px 0; line-height: 1.5; }
  .plan-section p { margin: 0; line-height: 1.55; }
  .avoid { background: rgba(211,47,47,.035); margin: 0 -10px; padding-left: 10px; padding-right: 10px; }
  .referral { background: rgba(232,89,12,.045); margin: 0 -10px; padding-left: 10px; padding-right: 10px; }
  .follow-up { background: rgba(30,142,62,.045); margin: 0 -10px; padding-left: 10px; padding-right: 10px; }
  @media (max-width: 560px) {
    .care-plan { padding: v.$space-4; }
    .care-plan__header { flex-direction: column; }
    .urgency { align-self: flex-start; }
  }

</style>
