<script lang="ts">
  /** Home hero illustration: health worker with tablet, two villagers, village health centre. */
</script>

<svg viewBox="0 0 620 400" role="img" aria-label="Health worker assisting a family outside a health centre" class="hero-scene">
  <defs>
    <linearGradient id="hs-sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#DCEBF7" />
      <stop offset="1" stop-color="#F3F9FD" />
    </linearGradient>
  </defs>
  <rect width="620" height="400" fill="url(#hs-sky)" opacity="0" />
  <!-- clouds -->
  <g fill="#ffffff" opacity="0.9">
    <ellipse cx="150" cy="60" rx="42" ry="14" /><ellipse cx="178" cy="52" rx="26" ry="12" />
    <ellipse cx="500" cy="38" rx="46" ry="14" /><ellipse cx="530" cy="30" rx="26" ry="11" />
  </g>
  <!-- hills -->
  <path d="M0 300 C90 250 180 262 260 290 C330 250 430 240 620 280 L620 400 L0 400 Z" fill="#CFE5D2" opacity="0.75" />
  <!-- ground -->
  <path d="M0 340 C150 322 420 322 620 340 L620 400 L0 400 Z" fill="#EAD9B7" />

  <!-- health centre -->
  <g>
    <rect x="388" y="190" width="214" height="150" fill="#F1E4CC" />
    <polygon points="372,196 618,196 590,152 400,152" fill="#2F78B8" />
    <polygon points="400,152 590,152 584,160 406,160" fill="#245F93" />
    <rect x="470" y="206" width="56" height="56" rx="4" fill="#ffffff" stroke="#C9B691" />
    <path d="M498 214 V254 M478 234 H518" stroke="#D93C3C" stroke-width="12" />
    <g fill="#E8DBBD"><rect x="418" y="270" width="12" height="70" /><rect x="566" y="270" width="12" height="70" /></g>
    <rect x="474" y="282" width="48" height="58" rx="2" fill="#6B8CAE" />
    <rect x="474" y="282" width="24" height="58" fill="#7FA0C2" />
    <rect x="404" y="232" width="34" height="32" rx="2" fill="#7FA6CC" />
    <rect x="558" y="232" width="34" height="32" rx="2" fill="#7FA6CC" />
  </g>

  <!-- tree -->
  <rect x="62" y="206" width="12" height="136" fill="#7A5B3E" />
  <ellipse cx="66" cy="168" rx="52" ry="78" fill="#6FA35A" />
  <ellipse cx="50" cy="196" rx="32" ry="50" fill="#5C9249" opacity="0.8" />
  <ellipse cx="86" cy="150" rx="30" ry="44" fill="#86B96E" opacity="0.8" />

  <!-- villager woman (yellow sari) -->
  <g>
    <path d="M436 342 L444 262 C448 246 478 246 484 262 L492 342 Z" fill="#E6B34A" />
    <path d="M444 262 C452 276 470 280 484 262 L488 300 C470 296 452 296 440 300 Z" fill="#3F9A9A" />
    <rect x="456" y="226" width="12" height="22" rx="5" fill="#C98A5B" />
    <ellipse cx="462" cy="214" rx="16" ry="19" fill="#D79A68" />
    <path d="M446 214 C440 190 460 184 468 188 C482 194 480 206 478 218 C474 204 462 198 446 214 Z" fill="#2D2420" />
    <path d="M444 216 C438 196 456 182 470 186 C486 190 484 214 478 232 L470 214 Z" fill="#3F9A9A" opacity="0.9" />
  </g>
  <!-- villager man (maroon shirt) -->
  <g>
    <rect x="504" y="272" width="20" height="70" fill="#4A3A33" />
    <path d="M496 280 C494 246 530 244 534 280 L534 312 L496 312 Z" fill="#A34A4A" />
    <rect x="508" y="226" width="12" height="22" rx="5" fill="#C98A5B" />
    <ellipse cx="514" cy="214" rx="15" ry="18" fill="#D79A68" />
    <path d="M500 212 C500 190 528 188 530 212 C522 202 508 202 500 212 Z" fill="#241C18" />
  </g>

  <!-- ASHA worker -->
  <g>
    <path d="M190 344 C186 296 192 264 204 250 L296 250 C308 264 314 296 310 344 Z" fill="#2F78B8" />
    <path d="M226 250 L250 290 L274 250 Z" fill="#F4F8FB" />
    <path d="M196 262 L186 318 C190 330 204 330 208 318 L216 262 Z" fill="#F4F8FB" />
    <path d="M304 262 L316 318 C312 330 298 330 294 318 L286 262 Z" fill="#F4F8FB" />
    <rect x="236" y="222" width="28" height="32" rx="10" fill="#E4A074" />
    <path d="M232 252 L244 304 M268 252 L256 304" stroke="#1F2933" stroke-width="2.4" fill="none" />
    <rect x="241" y="300" width="18" height="22" rx="3" fill="#ffffff" stroke="#BFCBD6" />
    <ellipse cx="250" cy="190" rx="37" ry="44" fill="#EDB187" />
    <path d="M211 192 C204 148 228 132 252 132 C282 132 298 152 289 192 C282 170 268 160 250 160 C232 160 218 172 211 192 Z" fill="#1F2933" />
    <circle cx="222" cy="150" r="17" fill="#1F2933" />
    <ellipse cx="238" cy="196" rx="3.6" ry="4.6" fill="#1F2933" />
    <ellipse cx="264" cy="196" rx="3.6" ry="4.6" fill="#1F2933" />
    <path d="M231 186 Q238 182 245 186 M257 186 Q264 182 271 186" stroke="#1F2933" stroke-width="2" fill="none" stroke-linecap="round" />
    <path d="M239 212 Q251 220 263 212" stroke="#B8552F" stroke-width="3" fill="none" stroke-linecap="round" />
    <g transform="rotate(-12 300 296)">
      <rect x="262" y="262" width="88" height="62" rx="7" fill="#16314D" />
      <rect x="268" y="268" width="76" height="50" rx="3" fill="#2B6194" />
      <rect x="276" y="277" width="32" height="4" rx="2" fill="#9CC5EA" />
      <rect x="276" y="286" width="48" height="4" rx="2" fill="#9CC5EA" opacity="0.7" />
    </g>
    <ellipse cx="262" cy="310" rx="12" ry="9" fill="#EDB187" />
    <ellipse cx="342" cy="288" rx="8" ry="10" fill="#EDB187" />
  </g>
</svg>

<style>
  .hero-scene { width: 100%; height: auto; display: block; }
</style>
