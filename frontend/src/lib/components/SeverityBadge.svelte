<script lang="ts">
  import { t } from "../i18n";
  import type { SeverityLevel } from "../types";

  export let level: SeverityLevel;
  /** Full label from the backend. Optional when `short` is used. */
  export let label: string = "";
  export let size: "sm" | "lg" = "sm";
  /** Show the compact Low / Medium / High / Emergency wording used in tables. */
  export let short = false;

  $: text = short || !label ? $t.ui.risk[level] : label;
</script>

<span class="badge badge-{level}" class:lg={size === "lg"}>
  <span class="dot" aria-hidden="true"></span>
  {text}
</span>

<style lang="scss">
  .badge {
    .dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: currentColor;
      display: inline-block;
    }
    &.lg {
      font-size: 1rem;
      padding: 10px 20px;
      .dot { width: 10px; height: 10px; }
    }
  }
</style>
