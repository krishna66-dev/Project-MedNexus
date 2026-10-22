<script lang="ts">
  /** Simple 24-spoke wheel motif (decorative). */
  export let size = 44;
  const spokes = Array.from({ length: 24 }, (_, i) => i * 15);
</script>

<svg width={size} height={size} viewBox="0 0 48 48" aria-hidden="true">
  <circle cx="24" cy="24" r="21" fill="none" stroke="currentColor" stroke-width="2.4" />
  <circle cx="24" cy="24" r="3.2" fill="currentColor" />
  {#each spokes as a}
    <line x1="24" y1="6" x2="24" y2="20.6" stroke="currentColor" stroke-width="1.4" transform="rotate({a} 24 24)" />
  {/each}
</svg>
