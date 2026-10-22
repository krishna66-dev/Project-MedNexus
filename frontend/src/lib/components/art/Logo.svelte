<script lang="ts">
  /** MedNexus heart-and-cross mark with optional wordmark. */
  export let size = 34;
  export let showText = true;
  export let light = false; // light text for dark backgrounds
  export let textSize = "1.25rem";
</script>

<span class="logo" class:light>
  <svg width={size} height={size} viewBox="0 0 48 48" aria-hidden="true">
    <path
      d="M24 42 C10 31 4 24 4 16.5 C4 10.7 8.5 6.5 14 6.5 C18 6.5 21.7 8.7 24 12.2 C26.3 8.7 30 6.5 34 6.5 C39.5 6.5 44 10.7 44 16.5 C44 24 38 31 24 42 Z"
      fill="none"
      stroke="#17A598"
      stroke-width="4.2"
      stroke-linejoin="round"
    />
    <path d="M24 17 V30 M17.5 23.5 H30.5" stroke="#17A598" stroke-width="4" stroke-linecap="round" />
  </svg>
  {#if showText}
    <span class="word" style="font-size:{textSize}">MedNexus</span>
  {/if}
</span>

<style lang="scss">
  @use "../../../styles/variables" as v;

  .logo { display: inline-flex; align-items: center; gap: 10px; line-height: 1; }
  .word { font-weight: 700; color: v.$color-navy-text; letter-spacing: 0.005em; }
  .light .word { color: v.$color-white; }
</style>
