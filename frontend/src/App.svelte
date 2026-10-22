<script lang="ts">
  import Router, { location } from "svelte-spa-router";
  import { t } from "./lib/i18n";
  import { currentUser } from "./lib/stores";
  import Navbar from "./lib/components/Navbar.svelte";
  import Footer from "./lib/components/Footer.svelte";
  import AppShell from "./lib/components/AppShell.svelte";
  import Home from "./routes/Home.svelte";
  import Login from "./routes/Login.svelte";
  import Register from "./routes/Register.svelte";
  import Dashboard from "./routes/Dashboard.svelte";
  import Triage from "./routes/Triage.svelte";
  import Result from "./routes/Result.svelte";
  import History from "./routes/History.svelte";
  import NotFound from "./routes/NotFound.svelte";

  const routes = {
    "/": Home,
    "/login": Login,
    "/register": Register,
    "/dashboard": Dashboard,
    "/triage": Triage,
    "/result/:id": Result,
    "/history/:patientId": History,
    "*": NotFound,
  };

  // Signed-in app pages use the sidebar layout; everything else uses navbar + footer.
  $: isAppPage = !!$currentUser && /^\/(dashboard|triage|result|history)(\/|$)/.test($location);
  $: shellTitle = $location === "/triage" ? $t.nav.newAssessment : "";
</script>

<a href="#main-content" class="skip-link">Skip to main content</a>

{#if isAppPage}
  <AppShell title={shellTitle}>
    <Router {routes} />
  </AppShell>
{:else}
  <Navbar />
  <main id="main-content">
    <Router {routes} />
  </main>
  <Footer />
{/if}
