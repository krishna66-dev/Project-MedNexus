<script lang="ts">
  import { lang, toggleLang } from "../i18n";

  /** "light" = for white backgrounds, "dark" = for navy backgrounds */
  export let variant: "light" | "dark" = "light";
</script>

<button
  class="lang-toggle {variant}"
  on:click={toggleLang}
  aria-label="Switch language / भाषा बदलें"
  title="English / हिन्दी"
>
  <span class:active={$lang === "en"}>EN</span>
  <span class="sep">|</span>
  <span class:active={$lang === "hi"}>हिन्दी</span>
</button>

<style lang="scss">
  @use "../../styles/variables" as v;

  .lang-toggle {
    background: transparent;
    border: 0;
    border-radius: v.$radius-pill;
    font-family: v.$font-family-base;
    font-weight: 600;
    font-size: 0.82rem;
    padding: 6px 10px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: background-color 0.15s ease;

    span { opacity: 0.6; transition: opacity 0.15s ease; }
    span.active { opacity: 1; font-weight: 700; }
    .sep { opacity: 0.35; }

    &.light { color: v.$color-navy-text; &:hover { background: v.$color-bg; } span.active { color: v.$color-teal; } }
    &.dark  { color: rgba(255, 255, 255, 0.9); &:hover { background: rgba(255, 255, 255, 0.1); } span.active { color: #fff; } }
  }
</style>
