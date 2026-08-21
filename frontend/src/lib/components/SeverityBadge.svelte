<script lang="ts">
  import type { SeverityLevel } from "../types";
  export let level: SeverityLevel;
  export let label: string;
  export let size: "sm" | "lg" = "sm";
</script>

<span class="badge badge-{level}" class:lg={size === "lg"}>
  <span class="dot" aria-hidden="true"></span>
  {label}
</span>

<style lang="scss">
  .badge {
    .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: currentColor;
      display: inline-block;
    }
    &.lg {
      font-size: 1rem;
      padding: 10px 20px;
      .dot { width: 11px; height: 11px; }
    }
  }
</style>
