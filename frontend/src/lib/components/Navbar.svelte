<script lang="ts">
  import { link, location, push } from "svelte-spa-router";
  import { t } from "../i18n";
  import { currentUser, clearSession } from "../stores";
  import { goToSection } from "../nav";
  import { initials } from "../format";
  import LanguageToggle from "./LanguageToggle.svelte";
  import Logo from "./art/Logo.svelte";
  import Icon from "./art/Icon.svelte";

  let menuOpen = false;
  let accountOpen = false;

  function handleLogout() {
    clearSession();
    accountOpen = false;
    menuOpen = false;
    push("/");
  }

  function section(id: string) {
    menuOpen = false;
    goToSection("/", id);
  }

  function roleLabel(role: string): string {
    if (role === "asha") return $t.ui.shell.roleAsha;
    if (role === "anm") return $t.ui.shell.roleAnm;
    if (role === "admin") return $t.ui.shell.roleAdmin;
    return $t.ui.shell.roleSelf;
  }

  $: path = $location;
</script>

<svelte:window on:click={() => (accountOpen = false)} />

{#if $currentUser}
  <!-- Signed-in navbar (dark) -->
  <header class="navbar navbar--dark">
    <div class="navbar__inner container">
      <a href="#/" use:link class="navbar__brand" aria-label="MedNexus">
        <Logo light size={32} textSize="1.2rem" />
      </a>

      <nav class="navbar__links" class:open={menuOpen} aria-label="Primary">
        <a href="#/" use:link class:active={path === "/"} on:click={() => (menuOpen = false)}>{$t.nav.home}</a>
        <a href="#/dashboard" use:link class:active={path === "/dashboard"} on:click={() => (menuOpen = false)}>{$t.nav.dashboard}</a>
        <button type="button" on:click={() => { menuOpen = false; goToSection("/dashboard", "patients"); }}>{$t.nav.patients}</button>
        <a href="#/history/all" use:link class:active={path.startsWith("/history")} on:click={() => (menuOpen = false)}>{$t.nav.history}</a>
      </nav>

      <div class="navbar__right">
        <LanguageToggle variant="dark" />
        <div class="account">
          <button
            type="button"
            class="account__btn"
            aria-haspopup="menu"
            aria-expanded={accountOpen}
            aria-label={$t.ui.nav.account}
            on:click|stopPropagation={() => (accountOpen = !accountOpen)}
          >
            <span class="avatar">{initials($currentUser.name)}</span>
            <span class="account__text">
              <strong>{$currentUser.name}</strong>
              <small>{roleLabel($currentUser.role)}</small>
            </span>
            <Icon name="chevron-down" size={16} />
          </button>
          {#if accountOpen}
            <div class="account__menu" role="menu">
              <button type="button" role="menuitem" on:click={handleLogout}>
                <Icon name="logout" size={16} /> {$t.nav.logout}
              </button>
            </div>
          {/if}
        </div>
        <button
          type="button"
          class="navbar__burger"
          aria-label={menuOpen ? $t.ui.nav.closeMenu : $t.ui.nav.menu}
          aria-expanded={menuOpen}
          on:click|stopPropagation={() => (menuOpen = !menuOpen)}
        >
          <Icon name={menuOpen ? "x" : "menu"} size={22} />
        </button>
      </div>
    </div>
  </header>
{:else}
  <!-- Public navbar (light) -->
  <header class="navbar navbar--light">
    <div class="navbar__inner container">
      <a href="#/" use:link class="navbar__brand" aria-label="MedNexus">
        <Logo size={32} textSize="1.2rem" />
      </a>

      <nav class="navbar__links" class:open={menuOpen} aria-label="Primary">
        <button type="button" class:active={path === "/"} on:click={() => section("top")}>{$t.nav.home}</button>
        <button type="button" on:click={() => section("about")}>{$t.ui.nav.about}</button>
        <button type="button" on:click={() => section("features")}>{$t.ui.nav.features}</button>
        <button type="button" on:click={() => section("contact")}>{$t.ui.nav.contact}</button>
      </nav>

      <div class="navbar__right">
        <LanguageToggle />
        <a href="#/login" use:link class="btn-outline navbar__btn" class:current={path === "/login"}>{$t.nav.login}</a>
        <a href="#/register" use:link class="btn-green navbar__btn">{$t.nav.register}</a>
        <button
          type="button"
          class="navbar__burger"
          aria-label={menuOpen ? $t.ui.nav.closeMenu : $t.ui.nav.menu}
          aria-expanded={menuOpen}
          on:click|stopPropagation={() => (menuOpen = !menuOpen)}
        >
          <Icon name={menuOpen ? "x" : "menu"} size={22} />
        </button>
      </div>
    </div>
  </header>
{/if}

<style lang="scss">
  @use "../../styles/variables" as v;

  .navbar {
    position: sticky;
    top: 0;
    z-index: 50;
  }
  .navbar--light {
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid v.$color-border;
  }
  .navbar--dark {
    background: v.$color-navy;
    color: #fff;
  }
  .navbar__inner {
    display: flex;
    align-items: center;
    gap: v.$space-5;
    min-height: 68px;
  }
  .navbar__brand {
    display: inline-flex;
    align-items: center;
    text-decoration: none;
    &:hover { text-decoration: none; }
  }
  .navbar__links {
    display: flex;
    align-items: center;
    gap: v.$space-5;
    margin-left: v.$space-5;

    a, button {
      background: none;
      border: 0;
      padding: 22px 0 19px;
      font: inherit;
      font-size: 0.88rem;
      font-weight: 600;
      cursor: pointer;
      border-bottom: 3px solid transparent;
      text-decoration: none;
      transition: color 0.15s ease, border-color 0.15s ease;
    }
  }
  .navbar--light .navbar__links {
    a, button {
      color: v.$color-navy-text;
      &:hover { color: v.$color-teal; }
      &.active { color: v.$color-teal; border-bottom-color: v.$color-teal; }
    }
  }
  .navbar--dark .navbar__links {
    a, button {
      color: rgba(255, 255, 255, 0.82);
      &:hover { color: #fff; }
      &.active { color: #fff; border-bottom-color: #2FC6B4; }
    }
  }
  .navbar__right {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: v.$space-3;
  }
  .navbar__btn {
    padding: 8px 20px;
    font-size: 0.86rem;
    box-shadow: none;
  }
  .navbar__burger {
    display: none;
    background: none;
    border: 0;
    cursor: pointer;
    padding: 6px;
    border-radius: v.$radius-sm;
  }
  .navbar--light .navbar__burger { color: v.$color-navy-text; }
  .navbar--dark .navbar__burger { color: #fff; }

  .account { position: relative; }
  .account__btn {
    display: flex;
    align-items: center;
    gap: 10px;
    background: none;
    border: 0;
    color: inherit;
    cursor: pointer;
    padding: 6px 8px;
    border-radius: v.$radius-md;
    font-family: v.$font-family-base;
    &:hover { background: rgba(255, 255, 255, 0.08); }
  }
  .avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: #2FC6B4;
    color: v.$color-navy-dark;
    font-weight: 700;
    font-size: 0.82rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .account__text {
    display: flex;
    flex-direction: column;
    text-align: left;
    line-height: 1.2;
    strong { font-size: 0.84rem; max-width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    small { font-size: 0.72rem; color: rgba(255, 255, 255, 0.65); }
  }
  .account__menu {
    position: absolute;
    right: 0;
    top: calc(100% + 6px);
    min-width: 160px;
    background: #fff;
    border-radius: v.$radius-md;
    box-shadow: v.$shadow-elevated;
    padding: 6px;
    z-index: 60;
    button {
      width: 100%;
      display: flex;
      align-items: center;
      gap: 10px;
      background: none;
      border: 0;
      padding: 10px 12px;
      border-radius: v.$radius-sm;
      font: inherit;
      font-size: 0.88rem;
      font-weight: 600;
      color: v.$color-navy-text;
      cursor: pointer;
      &:hover { background: v.$color-bg; }
    }
  }

  @media (max-width: v.$bp-md) {
    .navbar__inner { gap: v.$space-3; min-height: 60px; }
    .navbar__burger { display: inline-flex; }
    .navbar__btn { padding: 7px 14px; }
    .account__text { display: none; }
    .navbar__links {
      display: none;
      position: absolute;
      top: 100%;
      left: 0;
      right: 0;
      margin: 0;
      flex-direction: column;
      align-items: stretch;
      gap: 0;
      padding: v.$space-2 v.$space-4 v.$space-4;
      box-shadow: v.$shadow-elevated;

      &.open { display: flex; }
      a, button { padding: 14px 4px; text-align: left; border-bottom: 1px solid rgba(128, 150, 170, 0.25); }
    }
    .navbar--light .navbar__links { background: #fff; }
    .navbar--dark .navbar__links { background: v.$color-navy; }
  }
  @media (max-width: v.$bp-sm) {
    .navbar__btn.current { display: none; }
  }
</style>
