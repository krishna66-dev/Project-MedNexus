<script lang="ts">
  import { link, location, push } from "svelte-spa-router";
  import { t } from "../i18n";
  import { currentUser, clearSession } from "../stores";
  import { goToSection } from "../nav";
  import { initials } from "../format";
  import LanguageToggle from "./LanguageToggle.svelte";
  import Logo from "./art/Logo.svelte";
  import Icon from "./art/Icon.svelte";

  /** Text shown in the top bar (e.g. "New Assessment"). Empty = no title / back arrow. */
  export let title = "";

  let drawerOpen = false;
  let accountOpen = false;

  $: path = $location;

  function roleLabel(role: string): string {
    if (role === "asha") return $t.ui.shell.roleAsha;
    if (role === "anm") return $t.ui.shell.roleAnm;
    if (role === "admin") return $t.ui.shell.roleAdmin;
    return $t.ui.shell.roleSelf;
  }

  function handleLogout() {
    clearSession();
    drawerOpen = false;
    accountOpen = false;
    push("/");
  }

  function patientsSection() {
    drawerOpen = false;
    goToSection("/dashboard", "patients");
  }

  function goBack() {
    if (window.history.length > 1) window.history.back();
    else push("/dashboard");
  }
</script>

<svelte:window on:click={() => (accountOpen = false)} />

<div class="shell">
  {#if drawerOpen}
    <button class="shell__scrim no-print" aria-label={$t.ui.nav.closeMenu} on:click={() => (drawerOpen = false)}></button>
  {/if}

  <aside class="sidebar no-print" class:open={drawerOpen} aria-label="Primary">
    <a href="#/dashboard" use:link class="sidebar__brand" on:click={() => (drawerOpen = false)}>
      <Logo light size={32} textSize="1.2rem" />
    </a>

    <nav class="sidebar__nav">
      <a href="#/dashboard" use:link class:active={path === "/dashboard"} on:click={() => (drawerOpen = false)}>
        <Icon name="home" size={18} /> {$t.ui.shell.dashboard}
      </a>
      <a href="#/triage" use:link class:active={path === "/triage"} on:click={() => (drawerOpen = false)}>
        <Icon name="clipboard-plus" size={18} /> {$t.ui.shell.newAssessment}
      </a>
      <button type="button" on:click={patientsSection}>
        <Icon name="users" size={18} /> {$t.ui.shell.patients}
      </button>
      <a href="#/history/all" use:link class:active={path.startsWith("/history") || path.startsWith("/result")} on:click={() => (drawerOpen = false)}>
        <Icon name="history" size={18} /> {$t.ui.shell.history}
      </a>
    </nav>

    <div class="sidebar__foot">
      <div class="sidebar__lang">
        <Icon name="globe" size={18} />
        <LanguageToggle variant="dark" />
      </div>
      <button type="button" class="sidebar__logout" on:click={handleLogout}>
        <Icon name="logout" size={18} /> {$t.ui.shell.logout}
      </button>
    </div>
  </aside>

  <div class="shell__main">
    <header class="topbar no-print">
      <button
        type="button"
        class="topbar__burger"
        aria-label={$t.ui.nav.menu}
        aria-expanded={drawerOpen}
        on:click|stopPropagation={() => (drawerOpen = !drawerOpen)}
      >
        <Icon name="menu" size={22} />
      </button>

      {#if title}
        <button type="button" class="topbar__back" on:click={goBack} aria-label={$t.ui.triage.back}>
          <Icon name="arrow-left" size={20} />
        </button>
        <h2 class="topbar__title">{title}</h2>
      {/if}

      <div class="topbar__right">
        {#if $currentUser}
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
        {/if}
      </div>
    </header>

    <main id="main-content" class="shell__content">
      <slot />
    </main>
  </div>
</div>

<style lang="scss">
  @use "../../styles/variables" as v;

  .shell {
    display: flex;
    min-height: 100vh;
    background: linear-gradient(180deg, #F3F8FC 0%, v.$color-bg 100%);
  }

  /* ---------- Sidebar ---------- */
  .sidebar {
    width: v.$sidebar-width;
    flex-shrink: 0;
    background: linear-gradient(180deg, v.$color-navy 0%, v.$color-navy-dark 100%);
    color: #fff;
    display: flex;
    flex-direction: column;
    padding: v.$space-5 v.$space-3 v.$space-4;
    position: sticky;
    top: 0;
    height: 100vh;
    z-index: 40;
  }
  .sidebar__brand {
    padding: 0 v.$space-3 v.$space-5;
    text-decoration: none;
    &:hover { text-decoration: none; }
  }
  .sidebar__nav {
    display: flex;
    flex-direction: column;
    gap: 4px;

    a, button {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 11px 14px;
      border-radius: v.$radius-md;
      color: rgba(255, 255, 255, 0.82);
      font: inherit;
      font-size: 0.9rem;
      font-weight: 500;
      background: none;
      border: 0;
      cursor: pointer;
      text-align: left;
      text-decoration: none;
      transition: background-color 0.15s ease, color 0.15s ease;
      &:hover { background: rgba(255, 255, 255, 0.08); color: #fff; text-decoration: none; }
      &.active {
        background: linear-gradient(90deg, v.$color-teal 0%, #14999A 100%);
        color: #fff;
        font-weight: 600;
        box-shadow: 0 6px 16px rgba(15, 124, 128, 0.35);
      }
    }
  }
  .sidebar__foot {
    margin-top: auto;
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding-top: v.$space-4;
  }
  .sidebar__lang {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 14px;
    color: rgba(255, 255, 255, 0.82);
  }
  .sidebar__logout {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 11px 14px;
    border-radius: v.$radius-md;
    color: rgba(255, 255, 255, 0.82);
    background: none;
    border: 0;
    font: inherit;
    font-size: 0.9rem;
    cursor: pointer;
    &:hover { background: rgba(255, 255, 255, 0.08); color: #fff; }
  }

  /* ---------- Main column ---------- */
  .shell__main {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
  }
  .topbar {
    height: v.$topbar-height;
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid v.$color-border;
    display: flex;
    align-items: center;
    gap: v.$space-3;
    padding: 0 v.$space-5;
    position: sticky;
    top: 0;
    z-index: 30;
  }
  .topbar__burger, .topbar__back {
    background: none;
    border: 0;
    color: v.$color-navy-text;
    cursor: pointer;
    padding: 6px;
    border-radius: v.$radius-sm;
    display: inline-flex;
    &:hover { background: v.$color-bg; }
  }
  .topbar__burger { display: none; }
  .topbar__title { margin: 0; font-size: 1.05rem; font-weight: 700; }
  .topbar__right { margin-left: auto; display: flex; align-items: center; gap: v.$space-3; }

  .account { position: relative; }
  .account__btn {
    display: flex;
    align-items: center;
    gap: 10px;
    background: none;
    border: 0;
    color: v.$color-navy-text;
    cursor: pointer;
    padding: 6px 8px;
    border-radius: v.$radius-md;
    font-family: v.$font-family-base;
    &:hover { background: v.$color-bg; }
  }
  .avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #2FC6B4, v.$color-teal);
    color: #fff;
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
    strong { font-size: 0.86rem; max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    small { font-size: 0.72rem; color: v.$color-text-muted; }
  }
  .account__menu {
    position: absolute;
    right: 0;
    top: calc(100% + 6px);
    min-width: 160px;
    background: #fff;
    border: 1px solid v.$color-border;
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

  .shell__content {
    flex: 1;
    padding: v.$space-6 v.$space-6 v.$space-7;
    width: 100%;
    max-width: 1180px;
    margin: 0 auto;
  }

  .shell__scrim { display: none; }

  /* ---------- Mobile: sidebar becomes a drawer ---------- */
  @media (max-width: 900px) {
    .sidebar {
      position: fixed;
      left: 0;
      top: 0;
      bottom: 0;
      transform: translateX(-100%);
      transition: transform 0.2s ease;
      box-shadow: v.$shadow-elevated;
      &.open { transform: none; }
    }
    .shell__scrim {
      display: block;
      position: fixed;
      inset: 0;
      background: rgba(8, 40, 65, 0.45);
      border: 0;
      z-index: 35;
    }
    .topbar { padding: 0 v.$space-4; }
    .topbar__burger { display: inline-flex; }
    .account__text { display: none; }
    .shell__content { padding: v.$space-5 v.$space-4 v.$space-6; }
  }

  @media print {
    .shell { display: block; background: #fff; }
    .shell__content { padding: 0; max-width: none; }
  }
</style>
