<script lang="ts">
  import { link } from "svelte-spa-router";
  import { t } from "../lib/i18n";
  import { currentUser } from "../lib/stores";
  import Icon from "../lib/components/art/Icon.svelte";
</script>

<div class="container not-found">
  <div class="art" aria-hidden="true">
    <svg viewBox="0 0 220 200" width="220" height="200">
      <ellipse cx="110" cy="176" rx="86" ry="12" fill="#DDEAF5" />
      <rect x="52" y="30" width="116" height="140" rx="10" fill="#EAF3FA" stroke="#9CC3E2" stroke-width="3" />
      <rect x="86" y="20" width="48" height="22" rx="7" fill="#fff" stroke="#9CC3E2" stroke-width="3" />
      <rect x="68" y="60" width="84" height="10" rx="5" fill="#BBD6EC" />
      <rect x="68" y="80" width="62" height="10" rx="5" fill="#BBD6EC" />
      <rect x="68" y="100" width="44" height="10" rx="5" fill="#BBD6EC" />
      <circle cx="140" cy="124" r="30" fill="#fff" stroke="#0F7C80" stroke-width="6" />
      <path d="M162 146 L184 168" stroke="#0F7C80" stroke-width="9" stroke-linecap="round" />
      <path d="M130 114 q10 -12 20 0 q4 8 -8 14 v6 M142 144 v.01" stroke="#0F7C80" stroke-width="5" fill="none" stroke-linecap="round" />
    </svg>
  </div>
  <h1>{$t.ui.notFound.title}</h1>
  <p>{$t.ui.notFound.body}</p>
  <div class="cta">
    {#if $currentUser}
      <a href="#/dashboard" use:link class="btn-primary">{$t.ui.notFound.toDashboard}</a>
    {/if}
    <a href="#/" use:link class={$currentUser ? "btn-outline" : "btn-primary"}>
      {#if !$currentUser}<Icon name="home" size={16} />{/if}
      {$t.ui.notFound.toHome}
    </a>
  </div>
</div>

<style lang="scss">
  @use "../styles/variables" as v;

  .not-found {
    padding: v.$space-7 0 v.$space-7;
    text-align: center;
    min-height: 60vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    h1 { font-size: 1.8rem; margin: v.$space-4 0 v.$space-2; }
    p { color: v.$color-text-muted; max-width: 420px; margin: 0 0 v.$space-5; }
  }
  .cta { display: flex; gap: v.$space-3; flex-wrap: wrap; justify-content: center; }
</style>
