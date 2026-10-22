<script lang="ts">
  import { t } from "../i18n";
  import { SYMPTOM_CODES, type SymptomCode } from "../types";
  import Icon from "./art/Icon.svelte";

  export let selected: SymptomCode[] = [];

  function toggle(code: SymptomCode) {
    if (selected.includes(code)) {
      selected = selected.filter((c) => c !== code);
    } else {
      selected = [...selected, code];
    }
  }

  const redFlags = new Set([
    "severe_breathlessness",
    "chest_pain",
    "unconscious",
    "seizure",
    "severe_bleeding",
    "blue_lips_face",
    "stroke_signs",
  ]);
</script>

<div class="symptom-grid" role="group" aria-label={$t.triage.symptomsSection}>
  {#each SYMPTOM_CODES as code}
    <label class="symptom-pill" class:checked={selected.includes(code)} class:redflag={redFlags.has(code)}>
      <input
        type="checkbox"
        checked={selected.includes(code)}
        on:change={() => toggle(code)}
      />
      <span class="tick" aria-hidden="true">
        {#if selected.includes(code)}<Icon name="check" size={13} strokeWidth={3} />{/if}
      </span>
      {$t.symptoms[code]}
    </label>
  {/each}
</div>

<style lang="scss">
  @use "../../styles/variables" as v;

  .symptom-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: v.$space-2 v.$space-3;
    @media (max-width: v.$bp-sm) { grid-template-columns: 1fr; }
  }
  .symptom-pill {
    position: relative;
    display: flex;
    align-items: center;
    gap: 10px;
    border: 1.5px solid v.$color-border;
    border-radius: v.$radius-md;
    padding: 11px 14px;
    font-size: 0.88rem;
    font-weight: 500;
    cursor: pointer;
    background: v.$color-white;
    color: v.$color-text;
    transition: all 0.12s ease;

    input { position: absolute; opacity: 0; pointer-events: none; }

    .tick {
      width: 20px;
      height: 20px;
      border-radius: 6px;
      border: 1.5px solid v.$color-border-strong;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      flex-shrink: 0;
      background: v.$color-white;
    }

    &:hover { border-color: v.$color-teal; }
    input:focus-visible ~ .tick { outline: 3px solid rgba(15, 124, 128, 0.35); outline-offset: 2px; }

    &.checked {
      background: v.$color-teal-light;
      border-color: v.$color-teal;
      color: v.$color-navy-text;
      .tick { background: v.$color-teal; border-color: v.$color-teal; }
    }
    &.redflag.checked {
      background: v.$color-sev-red-bg;
      border-color: v.$color-severity-red;
      color: v.$color-severity-red;
      .tick { background: v.$color-severity-red; border-color: v.$color-severity-red; }
    }
  }
</style>
