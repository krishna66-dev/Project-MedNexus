<script lang="ts">
  import { link, location } from "svelte-spa-router";
  import { t } from "../i18n";
  import { currentUser, clearSession } from "../stores";
  import LanguageToggle from "./LanguageToggle.svelte";

  function handleLogout() {
    clearSession();
    window.location.hash = "#/";
  }
</script>

<header class="navbar">
  <div class="navbar__inner container">
    <a href="#/" use:link class="navbar__brand">
      <span class="navbar__emblem">
        <img src="/logo.png" alt="MedNexus" width="40" height="40" />
      </span>
      <span class="navbar__brand-text">
        <strong>{$t.brand.name}</strong>
        <small>{$t.brand.tagline}</small>
      </span>
    </a>

    <nav class="navbar__links" aria-label="Primary">
      {#if $currentUser}
        <a href="#/dashboard" use:link class:active={$location === "/dashboard"}>{$t.nav.dashboard}</a>
        <a href="#/triage" use:link class:active={$location === "/triage"}>{$t.nav.newAssessment}</a>
        <button class="btn-outline navbar__logout" on:click={handleLogout}>{$t.nav.logout}</button>
      {:else}
        <a href="#/login" use:link class:active={$location === "/login"}>{$t.nav.login}</a>
        <a href="#/register" use:link class="btn-saffron navbar__cta">{$t.nav.register}</a>
      {/if}
      <LanguageToggle />
    </nav>
  </div>
</header>

<style lang="scss">
  @use "../../styles/variables" as v;

  .navbar {
    background: v.$color-navy;
    border-bottom: 3px solid v.$color-saffron;
    position: sticky;
    top: 0;
    z-index: 50;
  }
  .navbar__inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: v.$space-3;
    padding-bottom: v.$space-3;
    gap: v.$space-4;
    flex-wrap: wrap;
  }
  .navbar__brand {
    display: flex;
    align-items: center;
    gap: v.$space-3;
    color: v.$color-white;
    text-decoration: none;
    &:hover { text-decoration: none; }
  }
  .navbar__emblem {
    display: inline-flex;
    border-radius: 50%;
    overflow: hidden;
    flex-shrink: 0;
    box-shadow: 0 0 0 2px v.$color-saffron;
    img {
      display: block;
      width: 40px;
      height: 40px;
      object-fit: cover;
    }
  }
  .navbar__brand-text {
    display: flex;
    flex-direction: column;
    line-height: 1.15;
    strong { font-size: 1.15rem; letter-spacing: 0.01em; }
    small { font-size: 0.68rem; color: rgba(255,255,255,0.75); font-weight: 500; }
  }
  .navbar__links {
    display: flex;
    align-items: center;
    gap: v.$space-4;
    a {
      color: rgba(255,255,255,0.88);
      font-weight: 600;
      font-size: 0.92rem;
      &.active { color: v.$color-saffron; }
      &:hover { color: v.$color-white; text-decoration: none; }
    }
  }
  .navbar__cta {
    padding: 8px 16px;
    &:hover { text-decoration: none; }
  }
  .navbar__logout {
    border-color: rgba(255,255,255,0.6);
    color: v.$color-white;
    &:hover { background: rgba(255,255,255,0.1); }
  }
</style>
