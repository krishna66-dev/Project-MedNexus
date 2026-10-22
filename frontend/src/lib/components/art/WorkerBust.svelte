<script lang="ts">
  /** Friendly ASHA-worker illustration (head & shoulders holding a tablet). */
  export let sari = "#3F8FD0";
  export let tablet = true;
</script>

<svg viewBox="0 0 220 240" role="img" aria-label="Community health worker" class="bust">
  <!-- body -->
  <path d="M14 240 C14 184 56 152 110 152 C164 152 206 184 206 240 Z" fill={sari} />
  <path d="M84 153 L110 196 L136 153 Z" fill="#F4F8FB" />
  <path d="M150 156 C176 168 198 192 204 240 L168 240 C168 204 160 176 150 156 Z" fill="#ffffff" opacity="0.85" />
  <!-- neck -->
  <rect x="96" y="126" width="28" height="32" rx="10" fill="#E4A074" />
  <!-- lanyard + id -->
  <path d="M92 156 L104 214 M128 156 L116 214" stroke="#1F2933" stroke-width="2.2" fill="none" />
  <rect x="100" y="210" width="20" height="24" rx="3" fill="#ffffff" stroke="#CBD5DF" />
  <rect x="104" y="214" width="12" height="7" rx="1.5" fill="#9DB8D2" />
  <!-- head -->
  <ellipse cx="110" cy="94" rx="37" ry="43" fill="#EDB187" />
  <!-- hair -->
  <path d="M71 94 C66 52 88 38 112 38 C140 38 156 58 149 94 C142 72 128 62 110 62 C92 62 78 74 71 94 Z" fill="#1F2933" />
  <circle cx="82" cy="54" r="15" fill="#1F2933" />
  <!-- face -->
  <ellipse cx="96" cy="98" rx="3.6" ry="4.6" fill="#1F2933" />
  <ellipse cx="124" cy="98" rx="3.6" ry="4.6" fill="#1F2933" />
  <path d="M89 88 Q96 84 103 88 M117 88 Q124 84 131 88" stroke="#1F2933" stroke-width="2" fill="none" stroke-linecap="round" />
  <path d="M98 116 Q110 126 122 116" stroke="#B8552F" stroke-width="3" fill="none" stroke-linecap="round" />
  <circle cx="86" cy="110" r="6" fill="#F19A7B" opacity="0.45" />
  <circle cx="134" cy="110" r="6" fill="#F19A7B" opacity="0.45" />
  {#if tablet}
    <g transform="rotate(-14 150 206)">
      <rect x="112" y="178" width="84" height="58" rx="7" fill="#16314D" />
      <rect x="118" y="184" width="72" height="46" rx="3" fill="#2B6194" />
      <rect x="124" y="192" width="30" height="4" rx="2" fill="#9CC5EA" />
      <rect x="124" y="201" width="44" height="4" rx="2" fill="#9CC5EA" opacity="0.7" />
    </g>
    <ellipse cx="116" cy="222" rx="12" ry="9" fill="#EDB187" />
    <ellipse cx="186" cy="204" rx="8" ry="10" fill="#EDB187" />
  {/if}
</svg>

<style>
  .bust { width: 100%; height: auto; display: block; }
</style>
