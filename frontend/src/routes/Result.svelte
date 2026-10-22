<script lang="ts">
  import { onMount } from "svelte";
  import { link } from "svelte-spa-router";
  import { t, lang } from "../lib/i18n";
  import { api } from "../lib/api";
  import { formatDate, genderShort, displayScore, isEscalated } from "../lib/format";
  import Icon from "../lib/components/art/Icon.svelte";
  import type { Patient, VitalsRecord } from "../lib/types";

  export let params: { id: string } = { id: "" };

  let record: VitalsRecord | null = null;
  let patient: Patient | null = null;
  let loading = true;

  $: plan = record ? record.triage.action_plan[$lang] : null;
  $: level = record ? record.triage.severity_level : "green";

  // 0-100 score that always agrees with the severity level (see lib/format.ts)
  $: score = record ? displayScore(level, record.triage.severity_score) : 0;
  // True when a red-flag symptom raised the level above what the vitals alone would give
  $: escalated = record ? isEscalated(level, record.triage.severity_score) : false;
  $: recommendations = record
    ? [record.triage.recommendation, ...(plan ? plan.immediate_actions : [])].filter(Boolean)
    : [];

  onMount(async () => {
    try {
      const res = await api.get<{ record: VitalsRecord }>(`/records/${params.id}`);
      record = res.record;
      // Patient details for the header strip (best-effort; the result itself doesn't depend on it)
      try {
        const pres = await api.get<{ patient: Patient }>(`/patients/${res.record.patient_id}`);
        patient = pres.patient;
      } catch {
        patient = null;
      }
    } finally {
      loading = false;
    }
  });
</script>

<div class="result">
  {#if loading}
    <p class="muted">{$t.common.loading}</p>
  {:else if !record}
    <p class="alert-error">{$t.common.error}</p>
  {:else}
    <h1>{$t.result.title}</h1>

    <div class="meta">
      {#if patient}
        <span>{$t.ui.result.name}: <strong>{patient.name}</strong></span>
        {#if patient.age != null}<span>{$t.ui.result.age}: <strong>{patient.age}</strong></span>{/if}
        <span>{$t.ui.result.gender}: <strong>{patient.gender ? (genderShort(patient.gender) === "M" ? $t.patient.genderMale : genderShort(patient.gender) === "F" ? $t.patient.genderFemale : $t.patient.genderOther) : $t.ui.result.notSpecified}</strong></span>
      {/if}
      <span>{$t.ui.result.date}: <strong>{formatDate(record.created_at, $lang)}</strong></span>
    </div>

    <section class="banner banner--{level}">
      <div class="banner__main">
        <span class="banner__icon"><Icon name="alert" size={26} /></span>
        <div>
          <h2>{record.triage.severity_label}</h2>
          <p>{$t.ui.result.score}: <strong>{score}</strong><span class="outof">/100</span></p>
          <div class="meter" role="img" aria-label="{$t.ui.result.score} {score}/100"><span style="width:{score}%"></span></div>
          {#if escalated}<p class="banner__note">{$t.ui.result.escalatedNote}</p>{/if}
        </div>
      </div>
      {#if plan}
        <div class="banner__side">
          <span class="banner__side-icon"><Icon name="heart" size={20} /></span>
          <div>
            <strong>{plan.urgency}</strong>
            <small>{plan.title}</small>
          </div>
        </div>
      {/if}
    </section>

    <div class="two-col">
      <section class="card panel">
        <h3>{$t.ui.result.keyFindings}</h3>
        {#if record.triage.contributing_factors.length === 0}
          <p class="muted">{$t.result.noFactors}</p>
        {:else}
          <ul>
            {#each record.triage.contributing_factors as f}<li>{f}</li>{/each}
          </ul>
        {/if}
      </section>

      <section class="card panel">
        <h3>{$t.ui.result.recommendations}</h3>
        <ul>
          {#each recommendations as item}<li>{item}</li>{/each}
        </ul>
      </section>
    </div>

    {#if plan}
      <section class="card care">
        <h3>{$t.ui.result.carePlan}</h3>
        <div class="care__grid">
          <div class="care__item">
            <span class="care__icon"><Icon name="ban" size={22} /></span>
            <div>
              <strong>{$t.ui.result.avoid}</strong>
              <ul>
                {#each plan.avoid as item}<li>{item}</li>{/each}
              </ul>
            </div>
          </div>
          <div class="care__item">
            <span class="care__icon"><Icon name="building" size={22} /></span>
            <div>
              <strong>{$t.result.referral}</strong>
              <p>{plan.referral}</p>
            </div>
          </div>
          <div class="care__item">
            <span class="care__icon"><Icon name="refresh" size={22} /></span>
            <div>
              <strong>{$t.result.followUp}</strong>
              <p>{plan.follow_up}</p>
            </div>
          </div>
        </div>
      </section>
    {/if}

    <p class="disclaimer">{$t.result.disclaimer}</p>

    <div class="actions no-print">
      <a href="#/triage" use:link class="btn-outline">{$t.result.newAssessment}</a>
      <button type="button" class="btn-outline" on:click={() => window.print()}>
        <Icon name="printer" size={16} /> {$t.ui.result.printReport}
      </button>
      <a href="#/history/{record.patient_id}" use:link class="btn-primary">{$t.result.viewHistory}</a>
    </div>
  {/if}
</div>

<style lang="scss">
  @use "../styles/variables" as v;

  .result { display: flex; flex-direction: column; gap: v.$space-4; }
  h1 { font-size: 1.4rem; margin: 0; }
  .muted { color: v.$color-text-muted; margin: 0; }

  .meta {
    display: flex;
    flex-wrap: wrap;
    gap: v.$space-2 v.$space-6;
    font-size: 0.88rem;
    color: v.$color-text-muted;
    strong { color: v.$color-navy-text; margin-left: 4px; }
  }

  /* ---------- Severity banner ---------- */
  .banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: v.$space-4;
    flex-wrap: wrap;
    border-radius: v.$radius-lg;
    padding: v.$space-5;
    border: 1px solid transparent;
    h2 { margin: 0 0 2px; font-size: 1.5rem; }
    p { margin: 0; font-size: 0.9rem; color: v.$color-navy-text; }
  }
  .banner__main { display: flex; align-items: center; gap: v.$space-4; }
  .banner__icon {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    flex-shrink: 0;
  }
  .outof { color: v.$color-text-muted; font-size: 0.8rem; margin-left: 1px; }
  .meter { height: 6px; width: 220px; max-width: 100%; border-radius: 4px; background: rgba(15, 42, 67, 0.12); margin: 8px 0 2px; overflow: hidden; span { display: block; height: 100%; border-radius: 4px; background: currentColor; } }
  .banner--red .meter span { background: v.$color-severity-red; }
  .banner--orange .meter span { background: v.$color-severity-orange; }
  .banner--yellow .meter span { background: #E3A21A; }
  .banner--green .meter span { background: v.$color-severity-green; }
  .banner__note { font-size: 0.8rem !important; color: v.$color-text-muted !important; margin-top: 2px !important; max-width: 460px; }
  .banner__side {
    display: flex;
    align-items: center;
    gap: v.$space-3;
    strong { display: block; font-size: 0.98rem; }
    small { display: block; font-size: 0.8rem; }
  }
  .banner__side-icon {
    width: 40px;
    height: 40px;
    border-radius: v.$radius-md;
    background: #fff;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .banner--red { background: v.$color-sev-red-bg; border-color: #F6C5C5; h2, .banner__side { color: v.$color-severity-red; } .banner__icon { background: v.$color-severity-red; box-shadow: 0 0 0 8px rgba(211, 47, 47, 0.15); } .banner__side-icon { color: v.$color-severity-red; } }
  .banner--orange { background: v.$color-sev-orange-bg; border-color: #F7CDB5; h2, .banner__side { color: v.$color-severity-orange; } .banner__icon { background: v.$color-severity-orange; box-shadow: 0 0 0 8px rgba(232, 89, 12, 0.15); } .banner__side-icon { color: v.$color-severity-orange; } }
  .banner--yellow { background: v.$color-sev-yellow-bg; border-color: #F2DDA6; h2, .banner__side { color: #A86F00; } .banner__icon { background: #E3A21A; box-shadow: 0 0 0 8px rgba(227, 162, 26, 0.18); } .banner__side-icon { color: #A86F00; } }
  .banner--green { background: v.$color-sev-green-bg; border-color: #BFE5CC; h2, .banner__side { color: v.$color-severity-green; } .banner__icon { background: v.$color-severity-green; box-shadow: 0 0 0 8px rgba(30, 142, 62, 0.15); } .banner__side-icon { color: v.$color-severity-green; } }

  /* ---------- Panels ---------- */
  .two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: v.$space-4;
    align-items: start;
    @media (max-width: v.$bp-md) { grid-template-columns: 1fr; }
  }
  .panel, .care {
    h3 { color: v.$color-teal; font-size: 1.05rem; margin-bottom: v.$space-3; }
    ul { margin: 0; padding-left: 20px; li { margin: 8px 0; line-height: 1.5; font-size: 0.9rem; &::marker { color: v.$color-teal; } } }
  }

  .care__grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: v.$space-5;
    @media (max-width: v.$bp-lg) { grid-template-columns: 1fr; gap: v.$space-4; }
  }
  .care__item {
    display: flex;
    gap: v.$space-3;
    & + & { padding-left: v.$space-5; border-left: 1px solid v.$color-border; @media (max-width: v.$bp-lg) { padding-left: 0; border-left: 0; } }
    strong { display: block; color: v.$color-teal-dark; font-size: 0.92rem; margin-bottom: 4px; }
    p { margin: 0; font-size: 0.88rem; color: v.$color-text; line-height: 1.5; }
    ul { padding-left: 18px; li { margin: 4px 0; font-size: 0.86rem; } }
  }
  .care__icon {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: v.$color-teal-light;
    color: v.$color-teal;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .actions { display: flex; justify-content: flex-end; gap: v.$space-3; flex-wrap: wrap; }
</style>
