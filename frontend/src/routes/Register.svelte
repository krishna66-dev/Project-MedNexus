<script lang="ts">
  import { link, push } from "svelte-spa-router";
  import { t, lang } from "../lib/i18n";
  import { api, ApiError } from "../lib/api";
  import { setSession, type User } from "../lib/stores";
  import Logo from "../lib/components/art/Logo.svelte";
  import Icon from "../lib/components/art/Icon.svelte";
  import ClinicScene from "../lib/components/art/ClinicScene.svelte";
  import WorkerBust from "../lib/components/art/WorkerBust.svelte";

  let name = "";
  let dob = "";
  let email = "";
  let password = "";
  let confirmPassword = "";
  let role: "self" | "asha" | "anm" = "self";
  let region = "";
  let phone = "";
  let gender = "";
  let agreed = false;

  let tab: "worker" | "individual" = "individual";
  let showPassword = false;
  let showConfirm = false;

  let loading = false;
  let formError = "";
  let fieldErrors: Record<string, string> = {};

  function setTab(next: "worker" | "individual") {
    tab = next;
    if (next === "individual") {
      role = "self";
    } else if (role === "self") {
      role = "asha";
    }
  }

  async function handleSubmit(e: Event) {
    e.preventDefault();
    formError = "";
    fieldErrors = {};

    if (password !== confirmPassword) {
      fieldErrors.confirmPassword = $t.ui.auth.passwordMismatch;
      return;
    }
    if (!agreed) {
      formError = $t.ui.auth.agreeRequired;
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
        gender: gender || undefined,
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

<div class="auth">
  <aside class="auth__side">
    <div class="auth__side-top">
      <Logo light size={34} textSize="1.4rem" />
      <h2>{$t.ui.auth.joinTitle}</h2>
      <p class="sub">{$t.ui.auth.joinSub}</p>

      <ul class="perks">
        <li>
          <span class="perk__icon"><Icon name="users" size={22} /></span>
          <span><strong>{$t.ui.auth.perkWorkerTitle}</strong><small>{$t.ui.auth.perkWorkerSub}</small></span>
        </li>
        <li>
          <span class="perk__icon"><Icon name="heart" size={22} /></span>
          <span><strong>{$t.ui.auth.perkIndTitle}</strong><small>{$t.ui.auth.perkIndSub}</small></span>
        </li>
        <li>
          <span class="perk__icon"><Icon name="shield" size={22} /></span>
          <span><strong>{$t.ui.auth.perkSecureTitle}</strong><small>{$t.ui.auth.perkSecureSub}</small></span>
        </li>
      </ul>
    </div>

    <div class="auth__scene" aria-hidden="true">
      <div class="scene-bg"><ClinicScene sign="" /></div>
      <div class="scene-worker"><WorkerBust /></div>
    </div>
  </aside>

  <section class="auth__panel">
    <form class="card auth-card" on:submit={handleSubmit}>
      <div class="tabs" role="tablist" aria-label={$t.auth.role}>
        <button type="button" role="tab" aria-selected={tab === "worker"} class:active={tab === "worker"} on:click={() => setTab("worker")}>
          {$t.ui.auth.tabWorker}
        </button>
        <button type="button" role="tab" aria-selected={tab === "individual"} class:active={tab === "individual"} on:click={() => setTab("individual")}>
          {$t.ui.auth.tabIndividual}
        </button>
      </div>

      {#if formError}
        <p class="alert-error" role="alert">{formError}</p>
      {/if}

      <div class="field">
        <label for="name">{$t.auth.name}</label>
        <input id="name" type="text" required bind:value={name} autocomplete="name" placeholder={$t.ui.auth.namePh} />
        {#if fieldErrors.name}<span class="error">{fieldErrors.name}</span>{/if}
      </div>

      <div class="grid-2">
        <div class="field">
          <label for="phone">{$t.auth.phone}</label>
          <input id="phone" type="tel" bind:value={phone} autocomplete="tel" placeholder={$t.ui.auth.phonePh} />
        </div>
        <div class="field">
          <label for="dob">{$t.auth.dob}</label>
          <input id="dob" type="date" required bind:value={dob} max={new Date().toISOString().split("T")[0]} />
          {#if fieldErrors.dob}<span class="error">{fieldErrors.dob}</span>{/if}
        </div>
      </div>

      <div class="field">
        <label for="gender">{$t.patient.gender}</label>
        <select id="gender" bind:value={gender}>
          <option value="">{$t.ui.auth.selectGender}</option>
          <option value="male">{$t.patient.genderMale}</option>
          <option value="female">{$t.patient.genderFemale}</option>
          <option value="other">{$t.patient.genderOther}</option>
        </select>
      </div>

      <div class="field">
        <label for="email">{$t.auth.email}</label>
        <input id="email" type="email" required bind:value={email} autocomplete="email" placeholder={$t.ui.auth.emailPh} />
        {#if fieldErrors.email}<span class="error">{fieldErrors.email}</span>{/if}
      </div>

      {#if tab === "worker"}
        <div class="grid-2">
          <div class="field">
            <label for="role">{$t.ui.auth.workerType}</label>
            <select id="role" bind:value={role}>
              <option value="asha">{$t.auth.roleAsha}</option>
              <option value="anm">{$t.auth.roleAnm}</option>
            </select>
            {#if fieldErrors.role}<span class="error">{fieldErrors.role}</span>{/if}
          </div>
          <div class="field">
            <label for="region">{$t.auth.region}</label>
            <input id="region" type="text" bind:value={region} placeholder={$t.ui.auth.regionPh} />
          </div>
        </div>
      {/if}

      <div class="field">
        <label for="password">{$t.auth.password}</label>
        <div class="pw">
          {#if showPassword}
            <input id="password" type="text" required minlength="8" bind:value={password} autocomplete="new-password" placeholder={$t.ui.auth.createPasswordPh} />
          {:else}
            <input id="password" type="password" required minlength="8" bind:value={password} autocomplete="new-password" placeholder={$t.ui.auth.createPasswordPh} />
          {/if}
          <button type="button" class="pw__toggle" aria-label={showPassword ? $t.ui.auth.hidePassword : $t.ui.auth.showPassword} on:click={() => (showPassword = !showPassword)}>
            <Icon name={showPassword ? "eye-off" : "eye"} size={18} />
          </button>
        </div>
        {#if fieldErrors.password}<span class="error">{fieldErrors.password}</span>{/if}
      </div>

      <div class="field">
        <label for="confirmPassword">{$t.auth.confirmPassword}</label>
        <div class="pw">
          {#if showConfirm}
            <input id="confirmPassword" type="text" required bind:value={confirmPassword} autocomplete="new-password" placeholder={$t.ui.auth.confirmPh} />
          {:else}
            <input id="confirmPassword" type="password" required bind:value={confirmPassword} autocomplete="new-password" placeholder={$t.ui.auth.confirmPh} />
          {/if}
          <button type="button" class="pw__toggle" aria-label={showConfirm ? $t.ui.auth.hidePassword : $t.ui.auth.showPassword} on:click={() => (showConfirm = !showConfirm)}>
            <Icon name={showConfirm ? "eye-off" : "eye"} size={18} />
          </button>
        </div>
        {#if fieldErrors.confirmPassword}<span class="error">{fieldErrors.confirmPassword}</span>{/if}
      </div>

      <label class="agree">
        <input type="checkbox" bind:checked={agreed} required />
        <span class="box" aria-hidden="true">{#if agreed}<Icon name="check" size={13} strokeWidth={3} />{/if}</span>
        <span>
          {$t.ui.auth.agreePrefix}
          <strong>{$t.ui.auth.terms}</strong>
          {$t.ui.auth.and}
          <strong>{$t.ui.auth.privacy}</strong>
        </span>
      </label>

      <button class="btn-green auth-submit" type="submit" disabled={loading}>
        {loading ? $t.common.loading : $t.auth.registerBtn}
      </button>

      <p class="auth-switch">
        {$t.auth.haveAccount}
        <a href="#/login" use:link>{$t.auth.loginLink}</a>
      </p>
    </form>
  </section>
</div>

<style lang="scss">
  @use "../styles/variables" as v;

  .auth {
    display: grid;
    grid-template-columns: minmax(300px, 0.85fr) 1.15fr;
    min-height: calc(100vh - 68px);
    @media (max-width: v.$bp-md) { grid-template-columns: 1fr; }
  }
  .auth__side {
    background: linear-gradient(180deg, v.$color-navy 0%, #0E4A66 70%, #15564F 100%);
    color: #fff;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
    @media (max-width: v.$bp-md) { .auth__scene { display: none; } }
  }
  .auth__side-top {
    padding: v.$space-6 v.$space-6 0;
    h2 { color: #fff; font-size: 1.7rem; font-weight: 700; margin: v.$space-5 0 6px; }
    .sub { margin: 0 0 v.$space-5; color: rgba(255, 255, 255, 0.85); }
  }
  .perks {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: v.$space-4;

    li { display: flex; align-items: center; gap: v.$space-3; }
    strong { display: block; font-size: 0.92rem; font-weight: 600; }
    small { display: block; font-size: 0.78rem; color: rgba(255, 255, 255, 0.7); }
  }
  .perk__icon {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: rgba(47, 198, 180, 0.18);
    border: 1px solid rgba(47, 198, 180, 0.35);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #7FE3D6;
    flex-shrink: 0;
  }
  .auth__scene {
    position: relative;
    height: 260px;
    margin-top: v.$space-4;
  }
  .scene-bg { position: absolute; inset: 0; opacity: 0.85; }
  .scene-worker { position: absolute; left: 12%; bottom: 0; width: 190px; }

  .auth__panel {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: v.$space-6 v.$space-4;
    background: linear-gradient(180deg, #F6FAFD, #EAF2F8);
  }
  .auth-card { width: 100%; max-width: 520px; padding: v.$space-5 v.$space-6 v.$space-6; @media (max-width: v.$bp-sm) { padding: v.$space-4; } }

  .tabs {
    display: grid;
    grid-template-columns: 1fr 1fr;
    background: v.$color-bg;
    border-radius: v.$radius-md;
    padding: 4px;
    margin-bottom: v.$space-5;
    button {
      border: 0;
      background: transparent;
      padding: 10px;
      border-radius: v.$radius-sm;
      font: inherit;
      font-size: 0.88rem;
      font-weight: 600;
      color: v.$color-navy-text;
      cursor: pointer;
      &.active { background: v.$color-teal; color: #fff; box-shadow: 0 4px 10px rgba(15, 124, 128, 0.25); }
    }
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

  .agree {
    position: relative;
    display: flex;
    align-items: flex-start;
    gap: 10px;
    font-size: 0.84rem;
    color: v.$color-text-muted;
    margin: v.$space-2 0 v.$space-4;
    cursor: pointer;
    input { position: absolute; opacity: 0; width: 20px; height: 20px; margin: 0; cursor: pointer; }
    strong { color: v.$color-blue-link; font-weight: 600; }
    .box {
      width: 20px;
      height: 20px;
      border-radius: 6px;
      border: 1.5px solid v.$color-border-strong;
      background: #fff;
      color: #fff;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      margin-top: 1px;
    }
    input:checked ~ .box { background: v.$color-teal; border-color: v.$color-teal; }
    input:focus-visible ~ .box { outline: 3px solid rgba(15, 124, 128, 0.35); outline-offset: 2px; }
  }

  .auth-submit { width: 100%; padding: 13px; font-size: 0.98rem; }
  .auth-switch { text-align: center; margin: v.$space-4 0 0; font-size: 0.88rem; color: v.$color-text-muted; a { font-weight: 600; text-decoration: underline; } }
</style>
