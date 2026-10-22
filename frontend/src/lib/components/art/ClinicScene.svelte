<script lang="ts">
  /** Rural primary-health-centre scene used at the bottom of the auth side panel. */
  export let sign = "आरोग्य केंद्र";
</script>

<svg viewBox="0 0 420 220" preserveAspectRatio="xMidYMax slice" role="img" aria-label="Primary health centre" class="scene">
  <!-- far trees -->
  <g fill="#14392F" opacity="0.75">
    <circle cx="40" cy="120" r="34" /><circle cx="86" cy="106" r="28" />
    <circle cx="330" cy="112" r="30" /><circle cx="384" cy="124" r="34" />
  </g>
  <!-- ground -->
  <rect x="0" y="188" width="420" height="32" fill="#C9B48C" opacity="0.9" />
  <!-- building -->
  <rect x="70" y="112" width="280" height="80" fill="#D9C9A5" />
  <polygon points="58,114 362,114 336,92 84,92" fill="#8C5B45" />
  <rect x="150" y="100" width="120" height="30" rx="3" fill="#F4EEDC" stroke="#A89466" stroke-width="2" />
  <text x="210" y="121" text-anchor="middle" font-size="17" font-weight="700" fill="#2B3A4A" font-family="Noto Sans Devanagari, sans-serif">{sign}</text>
  <!-- pillars + door -->
  <g fill="#EFE6CD">
    <rect x="124" y="130" width="12" height="62" /><rect x="284" y="130" width="12" height="62" />
  </g>
  <rect x="192" y="140" width="36" height="52" rx="2" fill="#2E4E6B" />
  <rect x="86" y="144" width="26" height="30" rx="2" fill="#3A6EA5" />
  <rect x="308" y="144" width="26" height="30" rx="2" fill="#3A6EA5" />
  <!-- foreground tree -->
  <rect x="14" y="140" width="9" height="52" fill="#4A3A2C" />
  <circle cx="18" cy="124" r="30" fill="#1D5A45" />
</svg>

<style>
  .scene { width: 100%; height: 100%; display: block; }
</style>
