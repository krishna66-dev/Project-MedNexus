<script lang="ts">
  import { link } from "svelte-spa-router";
  import { t } from "../lib/i18n";
</script>

<div class="container not-found">
  <h1>404</h1>
  <p>{$t.common.error}</p>
  <a href="#/" use:link class="btn-primary">{$t.nav.home}</a>
</div>

<style lang="scss">
  @use "../styles/variables" as v;
  .not-found { padding: v.$space-7 0; text-align: center; }
</style>
