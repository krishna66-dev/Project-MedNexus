<script lang="ts">
  import Router from "svelte-spa-router";
  import Navbar from "./lib/components/Navbar.svelte";
  import Footer from "./lib/components/Footer.svelte";
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
</script>

<a href="#main-content" class="skip-link">Skip to main content</a>
<div class="tricolour-strip" aria-hidden="true"></div>
<Navbar />
<main id="main-content">
  <Router {routes} />
</main>
<Footer />
