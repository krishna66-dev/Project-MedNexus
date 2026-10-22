<script lang="ts">
  import { link } from "svelte-spa-router";
  import { t } from "../lib/i18n";
  import { currentUser } from "../lib/stores";
  import { scrollToId } from "../lib/nav";
  import HeroScene from "../lib/components/art/HeroScene.svelte";
  import Icon from "../lib/components/art/Icon.svelte";
  import Logo from "../lib/components/art/Logo.svelte";
</script>

<section class="hero" id="top">
  <div class="container hero__inner">
    <div class="hero__copy" id="about">
      <h1>
        {$t.ui.home.titleA}<br />
        {$t.ui.home.titleB}
      </h1>
      <p class="hero__subtitle">{$t.ui.home.body}</p>
      <div class="hero__ctas">
        {#if $currentUser}
          <a href="#/dashboard" use:link class="btn-green hero__btn">{$t.nav.dashboard}</a>
        {:else}
          <a href="#/register" use:link class="btn-green hero__btn">{$t.ui.home.getStarted}</a>
        {/if}
        <button type="button" class="btn-outline hero__btn" on:click={() => scrollToId("features")}>
          <Icon name="play" size={14} strokeWidth={2.4} />
          {$t.ui.home.learnMore}
        </button>
      </div>
    </div>
    <div class="hero__art">
      <HeroScene />
    </div>
  </div>
</section>

<section class="features-wrap" id="features">
  <div class="container">
    <div class="features card">
      <div class="feature">
        <span class="feature__icon"><Icon name="clipboard-plus" size={26} /></span>
        <div>
          <h3>{$t.ui.home.f1Title}</h3>
          <p>{$t.ui.home.f1Body}</p>
        </div>
      </div>
      <div class="feature">
        <span class="feature__icon"><Icon name="activity" size={26} /></span>
        <div>
          <h3>{$t.ui.home.f2Title}</h3>
          <p>{$t.ui.home.f2Body}</p>
        </div>
      </div>
      <div class="feature">
        <span class="feature__icon"><Icon name="heart" size={26} /></span>
        <div>
          <h3>{$t.ui.home.f3Title}</h3>
          <p>{$t.ui.home.f3Body}</p>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="container motto-wrap">
  <div class="motto">
    <p class="motto__text">
      <span>{$t.ui.home.motto1}</span>
      <i aria-hidden="true"></i>
      <span>{$t.ui.home.motto2}</span>
      <i aria-hidden="true"></i>
      <span>{$t.ui.home.motto3}</span>
    </p>
    <div class="motto__brand">
      <Logo size={26} textSize="1rem" />
      <small>{$t.ui.home.poweredBy}</small>
    </div>
  </div>
  <p class="disclaimer">{$t.result.disclaimer}</p>
</section>

<style lang="scss">
  @use "../styles/variables" as v;

  section[id] { scroll-margin-top: 80px; }

  .hero {
    background: linear-gradient(135deg, #E4F0FA 0%, #F4F9FD 60%, #fff 100%);
    padding: v.$space-6 0 0;
    overflow: hidden;
  }
  .hero__inner {
    display: grid;
    grid-template-columns: 1fr 1.1fr;
    align-items: center;
    gap: v.$space-5;
    @media (max-width: v.$bp-lg) { grid-template-columns: 1fr; }
  }
  .hero__copy {
    padding: v.$space-5 0 v.$space-6;
    h1 { font-size: clamp(2rem, 4.2vw, 2.9rem); line-height: 1.15; font-weight: 800; color: v.$color-navy-text; margin-bottom: v.$space-4; }
  }
  .hero__subtitle { color: v.$color-text; font-size: 1.02rem; max-width: 520px; }
  .hero__ctas { display: flex; gap: v.$space-3; margin-top: v.$space-5; flex-wrap: wrap; }
  .hero__btn { padding: 13px 28px; font-size: 0.95rem; }
  .hero__art {
    align-self: end;
    @media (max-width: v.$bp-lg) { max-width: 560px; margin: 0 auto; }
  }

  .features-wrap { margin-top: -1px; background: linear-gradient(180deg, #fff 0%, v.$color-bg-soft 100%); padding: v.$space-5 0; }
  .features {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    padding: v.$space-5 v.$space-3;
    @media (max-width: v.$bp-md) { grid-template-columns: 1fr; gap: v.$space-4; padding: v.$space-5; }
  }
  .feature {
    display: flex;
    align-items: center;
    gap: v.$space-4;
    padding: 0 v.$space-5;
    & + & { border-left: 1px solid v.$color-border; }
    @media (max-width: v.$bp-md) { padding: 0; & + & { border-left: 0; } }
    h3 { font-size: 1rem; margin: 0 0 2px; }
    p { margin: 0; font-size: 0.84rem; color: v.$color-text-muted; line-height: 1.4; }
  }
  .feature__icon {
    width: 54px;
    height: 54px;
    border-radius: v.$radius-md;
    background: v.$color-teal-light;
    color: v.$color-teal;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .motto-wrap { padding-top: v.$space-4; padding-bottom: v.$space-4; }
  .motto {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: v.$space-4;
    flex-wrap: wrap;
    padding: v.$space-4 v.$space-2;
  }
  .motto__text {
    display: flex;
    align-items: center;
    gap: v.$space-4;
    margin: 0;
    font-size: 1.15rem;
    font-weight: 600;
    color: v.$color-navy-text;
    flex-wrap: wrap;
    i { width: 1px; height: 22px; background: v.$color-border-strong; }
  }
  .motto__brand {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 4px;
    small { color: v.$color-text-muted; font-size: 0.75rem; }
  }
</style>
