<script lang="ts">
  import { link, push } from "svelte-spa-router";
  import { t, lang } from "../lib/i18n";
  import { api, ApiError } from "../lib/api";
  import { setSession, type User } from "../lib/stores";

  let name = "";
  let dob = "";
  let email = "";
  let password = "";
  let confirmPassword = "";
  let role: "self" | "asha" | "anm" = "self";
  let region = "";
  let phone = "";

  let loading = false;
  let formError = "";
  let fieldErrors: Record<string, string> = {};

  async function handleSubmit(e: Event) {
    e.preventDefault();
    formError = "";
    fieldErrors = {};

    if (password !== confirmPassword) {
      fieldErrors.confirmPassword = $t.common.required + ": " + $t.auth.password;
      return;
    }

    loading = true;
    try {
      const res = await api.post<{ token: string; user: User }>("/auth/register", {
        name,
        dob,
        email,
        password,
        role,
        region: region || undefined,
        phone: phone || undefined,
        preferred_language: $lang,
      });
      setSession(res.token, res.user);
      push("/dashboard");
    } catch (err) {
      if (err instanceof ApiError) {
        formError = err.message;
        if (err.errors) fieldErrors = err.errors;
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
    <h2>{$t.auth.registerTitle}</h2>

    {#if formError}
      <p class="error" role="alert">{formError}</p>
    {/if}

    <div class="field">
      <label for="name">{$t.auth.name}</label>
      <input id="name" type="text" required bind:value={name} autocomplete="name" />
      {#if fieldErrors.name}<span class="hint error">{fieldErrors.name}</span>{/if}
    </div>

    <div class="grid-2">
      <div class="field">
        <label for="dob">{$t.auth.dob}</label>
        <input id="dob" type="date" required bind:value={dob} max={new Date().toISOString().split("T")[0]} />
        {#if fieldErrors.dob}<span class="hint error">{fieldErrors.dob}</span>{/if}
      </div>

      <div class="field">
        <label for="role">{$t.auth.role}</label>
        <select id="role" bind:value={role}>
          <option value="self">{$t.auth.roleSelf}</option>
          <option value="asha">{$t.auth.roleAsha}</option>
          <option value="anm">{$t.auth.roleAnm}</option>
        </select>
      </div>
    </div>

    <div class="field">
      <label for="email">{$t.auth.email}</label>
      <input id="email" type="email" required bind:value={email} autocomplete="email" />
      {#if fieldErrors.email}<span class="hint error">{fieldErrors.email}</span>{/if}
    </div>

    {#if role !== "self"}
      <div class="field">
        <label for="region">{$t.auth.region}</label>
        <input id="region" type="text" bind:value={region} />
      </div>
    {/if}

    <div class="field">
      <label for="phone">{$t.auth.phone}</label>
      <input id="phone" type="tel" bind:value={phone} autocomplete="tel" />
    </div>

    <div class="grid-2">
      <div class="field">
        <label for="password">{$t.auth.password}</label>
        <input id="password" type="password" required minlength="8" bind:value={password} autocomplete="new-password" />
        {#if fieldErrors.password}<span class="hint error">{fieldErrors.password}</span>{/if}
      </div>
      <div class="field">
        <label for="confirmPassword">{$t.auth.confirmPassword}</label>
        <input id="confirmPassword" type="password" required bind:value={confirmPassword} autocomplete="new-password" />
        {#if fieldErrors.confirmPassword}<span class="hint error">{fieldErrors.confirmPassword}</span>{/if}
      </div>
    </div>

    <button class="btn-primary auth-submit" type="submit" disabled={loading}>
      {loading ? $t.common.loading : $t.auth.registerBtn}
    </button>

    <p class="auth-switch">
      {$t.auth.haveAccount}
      <a href="#/login" use:link>{$t.auth.loginLink}</a>
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
  .auth-card { width: 100%; max-width: 480px; }
  .auth-submit { width: 100%; margin-top: v.$space-2; }
  .auth-switch { text-align: center; margin-top: v.$space-4; font-size: 0.9rem; color: v.$color-text-muted; }
  .error { background: rgba(211,47,47,.08); color: v.$color-severity-red; padding: v.$space-2 v.$space-3; border-radius: v.$radius-sm; font-size: 0.88rem; font-weight: 600; }
</style>
