<script lang="ts">
  import { link, push } from "svelte-spa-router";
  import { t } from "../lib/i18n";
  import { api, ApiError } from "../lib/api";
  import { setSession, type User } from "../lib/stores";

  let email = "";
  let password = "";
  let loading = false;
  let formError = "";

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

<div class="auth-page container">
  <form class="card auth-card" on:submit={handleSubmit}>
    <h2>{$t.auth.loginTitle}</h2>

    {#if formError}
      <p class="error" role="alert">{formError}</p>
    {/if}

    <div class="field">
      <label for="email">{$t.auth.email}</label>
      <input id="email" type="email" required bind:value={email} autocomplete="email" />
    </div>

    <div class="field">
      <label for="password">{$t.auth.password}</label>
      <input id="password" type="password" required bind:value={password} autocomplete="current-password" />
    </div>

    <button class="btn-primary auth-submit" type="submit" disabled={loading}>
      {loading ? $t.common.loading : $t.auth.loginBtn}
    </button>

    <p class="auth-switch">
      {$t.auth.noAccount}
      <a href="#/register" use:link>{$t.auth.registerLink}</a>
    </p>
  </form>
</div>

<style lang="scss">
  @use "../styles/variables" as v;

  .auth-page {
    display: flex;
    justify-content: center;
    padding: v.$space-7 v.$space-4;
  }
  .auth-card {
    width: 100%;
    max-width: 420px;
  }
  .auth-submit { width: 100%; margin-top: v.$space-2; }
  .auth-switch { text-align: center; margin-top: v.$space-4; font-size: 0.9rem; color: v.$color-text-muted; }
  .error { background: rgba(211,47,47,.08); color: v.$color-severity-red; padding: v.$space-2 v.$space-3; border-radius: v.$radius-sm; font-size: 0.88rem; font-weight: 600; }
</style>
