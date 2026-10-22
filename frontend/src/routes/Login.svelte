<script lang="ts">
  import { link, push } from "svelte-spa-router";
  import { t } from "../lib/i18n";
  import { api, ApiError } from "../lib/api";
  import { setSession, type User } from "../lib/stores";
  import Logo from "../lib/components/art/Logo.svelte";
  import Icon from "../lib/components/art/Icon.svelte";
  import ClinicScene from "../lib/components/art/ClinicScene.svelte";

  let email = "";
  let password = "";
  let loading = false;
  let formError = "";
  let showPassword = false;

  async function handleSubmit(e: Event) {
    e.preventDefault();
    formError = "";
    loading = true;
    try {
      const res = await api.post<{ token: string; user: User }>("/auth/login", { email, password });
      setSession(res.token, res.user);
      push("/dashboard");
    } catch (err) {
      if (err instanceof ApiError) {
        formError = err.message;
      } else {
        formError = $t.common.error;
      }
    } finally {
      loading = false;
    }
  }
</script>

<div class="auth">
  <aside class="auth__side">
    <div class="auth__side-top">
      <Logo light size={38} textSize="1.6rem" />
      <h2>{$t.ui.auth.sideTitle}</h2>
      <p class="quote">{$t.ui.auth.sideQuote}</p>
    </div>
    <div class="auth__scene" aria-hidden="true"><ClinicScene /></div>
  </aside>

  <section class="auth__panel">
    <form class="card auth-card" on:submit={handleSubmit}>
      <h1>{$t.ui.auth.welcomeBack}</h1>
      <p class="sub">{$t.ui.auth.loginSub}</p>

      {#if formError}
        <p class="alert-error" role="alert">{formError}</p>
      {/if}

      <div class="field">
        <label for="email">{$t.auth.email}</label>
        <input id="email" type="email" required bind:value={email} autocomplete="email" placeholder={$t.ui.auth.emailPh} />
      </div>

      <div class="field">
        <label for="password">{$t.auth.password}</label>
        <div class="pw">
          {#if showPassword}
            <input id="password" type="text" required bind:value={password} autocomplete="current-password" placeholder={$t.ui.auth.passwordPh} />
          {:else}
            <input id="password" type="password" required bind:value={password} autocomplete="current-password" placeholder={$t.ui.auth.passwordPh} />
          {/if}
          <button
            type="button"
            class="pw__toggle"
            aria-label={showPassword ? $t.ui.auth.hidePassword : $t.ui.auth.showPassword}
            on:click={() => (showPassword = !showPassword)}
          >
            <Icon name={showPassword ? "eye-off" : "eye"} size={18} />
          </button>
        </div>
      </div>

      <button class="btn-primary auth-submit" type="submit" disabled={loading}>
        {loading ? $t.common.loading : $t.auth.loginBtn}
      </button>

      <p class="auth-switch">
        {$t.auth.noAccount}
        <a href="#/register" use:link>{$t.auth.registerLink}</a>
      </p>
    </form>
  </section>
</div>

<style lang="scss">
  @use "../styles/variables" as v;

  .auth {
    display: grid;
    grid-template-columns: minmax(300px, 0.9fr) 1.1fr;
    min-height: calc(100vh - 68px);
    @media (max-width: v.$bp-md) { grid-template-columns: 1fr; }
  }
  .auth__side {
    background: linear-gradient(180deg, v.$color-navy 0%, #0E4A66 70%, #15564F 100%);
    color: #fff;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
    @media (max-width: v.$bp-md) { min-height: 280px; }
  }
  .auth__side-top {
    padding: v.$space-6 v.$space-6 0;
    h2 { color: #fff; font-size: 1.25rem; font-weight: 600; margin: v.$space-6 0 v.$space-4; max-width: 320px; }
    .quote { color: rgba(255, 255, 255, 0.78); font-size: 0.92rem; max-width: 280px; margin: 0; }
  }
  .auth__scene {
    height: 220px;
    margin-top: v.$space-5;
    @media (max-width: v.$bp-md) { height: 150px; }
  }

  .auth__panel {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: v.$space-6 v.$space-4;
    background: linear-gradient(180deg, #F6FAFD, #EAF2F8);
  }
  .auth-card {
    width: 100%;
    max-width: 460px;
    padding: v.$space-6;
    h1 { font-size: 1.6rem; font-weight: 700; margin-bottom: 6px; }
    .sub { margin: 0 0 v.$space-5; color: v.$color-text-muted; font-size: 0.9rem; }
  }
  .pw { position: relative; }
  .pw input { padding-right: 46px; }
  .pw__toggle {
    position: absolute;
    right: 6px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: 0;
    color: v.$color-text-muted;
    padding: 8px;
    border-radius: v.$radius-sm;
    cursor: pointer;
    &:hover { color: v.$color-teal; }
  }
  .auth-submit { width: 100%; margin-top: v.$space-2; padding: 13px; font-size: 0.98rem; }
  .auth-switch { text-align: center; margin: v.$space-5 0 0; font-size: 0.88rem; color: v.$color-text-muted; a { font-weight: 600; text-decoration: underline; } }
</style>
