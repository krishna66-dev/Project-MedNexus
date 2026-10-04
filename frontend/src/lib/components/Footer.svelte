<script lang="ts">
  import { t } from "../i18n";
</script>

<footer class="footer">
  <div class="tricolour-strip" aria-hidden="true"></div>
  <div class="footer__inner container">
    <p class="footer__text">{$t.footer.text}</p>
    <p class="footer__disclaimer">{$t.footer.disclaimer}</p>
    <p class="gov-emblem-note">MedNexus \u00b7 {$t.brand.ministry}</p>
  </div>
</footer>

<style lang="scss">
  @use "../../styles/variables" as v;

  .footer {
    margin-top: auto;
    background: v.$color-navy-dark;
    color: rgba(255,255,255,0.85);
  }
  .footer__inner {
    padding: v.$space-5 v.$space-5;
    text-align: center;
  }
  .footer__text { margin: 0 0 4px; font-weight: 600; }
  .footer__disclaimer { font-size: 0.8rem; color: rgba(255,255,255,0.65); margin: 0 0 8px; }
  .gov-emblem-note { color: rgba(255,255,255,0.45); }
</style>
