<script lang="ts">
  import { link } from "svelte-spa-router";
  import { t } from "../i18n";
  import { goToSection } from "../nav";
  import Logo from "./art/Logo.svelte";
  import Chakra from "./art/Chakra.svelte";

  const year = new Date().getFullYear();
</script>

<footer class="footer" id="contact">
  <div class="container">
    <div class="footer__card">
      <div class="footer__brand">
        <Logo light size={36} textSize="1.3rem" />
        <p>{$t.ui.footer.tagline}</p>
      </div>

      <div class="footer__col">
        <h4>{$t.ui.footer.quickLinks}</h4>
        <ul>
          <li><a href="#/" use:link>{$t.nav.home}</a></li>
          <li><button type="button" on:click={() => goToSection("/", "about")}>{$t.ui.nav.about}</button></li>
          <li><button type="button" on:click={() => goToSection("/", "features")}>{$t.ui.nav.features}</button></li>
          <li><a href="#/login" use:link>{$t.nav.login}</a></li>
        </ul>
      </div>

      <div class="footer__col">
        <h4>{$t.ui.footer.support}</h4>
        <ul>
          <li class="plain">{$t.ui.footer.ambulance}</li>
          <li><a href="#/register" use:link>{$t.nav.register}</a></li>
        </ul>
      </div>

      <div class="footer__gov">
        <Chakra size={46} />
        <p class="footer__gov-text">{$t.brand.ministry}</p>
        <p class="footer__gov-sub">{$t.ui.footer.stepTowards}</p>
      </div>
    </div>

    <div class="footer__bottom">
      <span>© {year} MedNexus. {$t.ui.footer.rights}</span>
      <span class="footer__disclaimer">{$t.footer.disclaimer}</span>
    </div>
  </div>
</footer>

<style lang="scss">
  @use "../../styles/variables" as v;

  .footer {
    margin-top: auto;
    padding: v.$space-6 0 v.$space-5;
  }
  .footer__card {
    background: v.$color-navy;
    color: rgba(255, 255, 255, 0.85);
    border-radius: v.$radius-lg;
    padding: v.$space-6;
    display: grid;
    grid-template-columns: 1.5fr 1fr 1fr 1.3fr;
    gap: v.$space-5 v.$space-6;
    @media (max-width: v.$bp-lg) { grid-template-columns: 1fr 1fr; }
    @media (max-width: v.$bp-sm) { grid-template-columns: 1fr; padding: v.$space-5; }
  }
  .footer__brand p { margin: v.$space-3 0 0; font-size: 0.86rem; color: rgba(255, 255, 255, 0.7); max-width: 280px; }
  .footer__col {
    h4 { color: #fff; font-size: 0.92rem; margin-bottom: v.$space-3; }
    ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 10px; }
    a, button {
      background: none;
      border: 0;
      padding: 0;
      font: inherit;
      font-size: 0.86rem;
      color: rgba(255, 255, 255, 0.78);
      cursor: pointer;
      text-align: left;
      &:hover { color: #fff; text-decoration: underline; }
    }
    .plain { font-size: 0.86rem; color: rgba(255, 255, 255, 0.78); }
  }
  .footer__gov {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding-left: v.$space-5;
    border-left: 1px solid rgba(255, 255, 255, 0.15);
    color: rgba(255, 255, 255, 0.9);
    @media (max-width: v.$bp-lg) { border-left: 0; padding-left: 0; }
  }
  .footer__gov-text { margin: 0; font-weight: 600; font-size: 0.88rem; }
  .footer__gov-sub { margin: 0; font-size: 0.8rem; color: rgba(255, 255, 255, 0.65); }
  .footer__bottom {
    display: flex;
    justify-content: space-between;
    gap: v.$space-4;
    flex-wrap: wrap;
    padding: v.$space-4 v.$space-2 0;
    font-size: 0.76rem;
    color: v.$color-text-muted;
  }
  .footer__disclaimer { max-width: 620px; }
</style>
