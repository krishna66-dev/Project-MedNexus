<script lang="ts">
  import { lang, toggleLang } from "../i18n";
</script>

<button
  class="lang-toggle"
  on:click={toggleLang}
  aria-label="Switch language / \u092d\u093e\u0937\u093e \u092c\u0926\u0932\u0947\u0902"
  title="English / \u0939\u093f\u0902\u0926\u0940"
>
  <span class:active={$lang === "en"}>EN</span>
  <span class="sep">|</span>
  <span class:active={$lang === "hi"}>\u0939\u093f</span>
</button>

<style lang="scss">
  @use "../../styles/variables" as v;

  .lang-toggle {
    background: rgba(255,255,255,0.1);
    border: 1.5px solid rgba(255,255,255,0.4);
    border-radius: 999px;
    color: v.$color-white;
    font-weight: 700;
    font-size: 0.8rem;
    padding: 6px 12px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 4px;

    span { opacity: 0.55; }
    span.active { opacity: 1; color: v.$color-saffron; }
    .sep { opacity: 0.4; }

    &:hover { background: rgba(255,255,255,0.18); }
  }
</style>
