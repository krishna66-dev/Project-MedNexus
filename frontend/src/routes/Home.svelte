<script lang="ts">
  import { link } from "svelte-spa-router";
  import { t } from "../lib/i18n";
  import { currentUser } from "../lib/stores";
</script>

<section class="hero">
  <div class="container hero__inner">
    <div class="hero__copy">
      <h1>{$t.home.heroTitle}</h1>
      <p class="hero__subtitle">{$t.home.heroSubtitle}</p>
      <div class="hero__ctas">
        {#if $currentUser}
          <a href="#/dashboard" use:link class="btn-primary">{$t.nav.dashboard}</a>
        {:else}
          <a href="#/register" use:link class="btn-saffron">{$t.home.ctaRegister}</a>
          <a href="#/login" use:link class="btn-outline">{$t.home.ctaLogin}</a>
        {/if}
      </div>
    </div>
    <div class="hero__badges" aria-hidden="true">
      <span class="badge badge-green">{$t.severity.green}</span>
      <span class="badge badge-yellow">{$t.severity.yellow}</span>
      <span class="badge badge-orange">{$t.severity.orange}</span>
      <span class="badge badge-red">{$t.severity.red}</span>
    </div>
  </div>
</section>

<section class="container features">
  <div class="card feature">
    <h3>{$t.home.feature1Title}</h3>
    <p>{$t.home.feature1Body}</p>
  </div>
  <div class="card feature">
    <h3>{$t.home.feature2Title}</h3>
    <p>{$t.home.feature2Body}</p>
  </div>
  <div class="card feature">
    <h3>{$t.home.feature3Title}</h3>
    <p>{$t.home.feature3Body}</p>
  </div>
</section>

<section class="container">
  <p class="disclaimer">{$t.result.disclaimer}</p>
</section>

<style lang="scss">
  @use "../styles/variables" as v;

  .hero {
    background: linear-gradient(135deg, v.$color-blue-light 0%, #fff 70%);
    padding: v.$space-7 0;
    border-bottom: 1px solid v.$color-border;
  }
  .hero__inner {
    display: flex;
    flex-direction: column;
    gap: v.$space-5;
  }
  .hero__copy {
    max-width: 720px;
    h1 { font-size: 2.1rem; }
  }
  .hero__subtitle { color: v.$color-text-muted; font-size: 1.05rem; }
  .hero__ctas { display: flex; gap: v.$space-3; margin-top: v.$space-4; flex-wrap: wrap; }
  .hero__badges { display: flex; gap: v.$space-2; flex-wrap: wrap; }

  .features {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: v.$space-4;
    padding: v.$space-6 0;
    @media (max-width: v.$bp-md) { grid-template-columns: 1fr; }
  }
  .feature h3 { color: v.$color-navy; font-size: 1.05rem; }
  .feature p { color: v.$color-text-muted; margin: 0; }
</style>
