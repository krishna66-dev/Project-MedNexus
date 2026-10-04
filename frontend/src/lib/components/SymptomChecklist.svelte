<script lang="ts">
  import { t } from "../i18n";
  import { SYMPTOM_CODES, type SymptomCode } from "../types";

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
      {$t.symptoms[code]}
    </label>
  {/each}
</div>

<style lang="scss">
  @use "../../styles/variables" as v;

  .symptom-grid {
    display: flex;
    flex-wrap: wrap;
    gap: v.$space-2;
  }
  .symptom-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border: 1.5px solid v.$color-border;
    border-radius: 999px;
    padding: 7px 14px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    background: v.$color-white;
    color: v.$color-text;
    transition: all 0.12s ease;

    input { accent-color: v.$color-navy; }

    &:hover { border-color: v.$color-blue; }
    &.checked {
      background: v.$color-blue-light;
      border-color: v.$color-blue;
      color: v.$color-navy-dark;
    }
    &.redflag.checked {
      background: rgba(211,47,47,.1);
      border-color: v.$color-severity-red;
      color: v.$color-severity-red;
    }
  }
</style>
