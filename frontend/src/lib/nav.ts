import { push, location } from "svelte-spa-router";
import { get } from "svelte/store";

export function scrollToId(id: string) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
}

/** Navigate to `path` (if not already there) and smooth-scroll to element `id`. */
export function goToSection(path: string, id: string) {
  if (get(location) === path) {
    scrollToId(id);
    return;
  }
  push(path);
  setTimeout(() => scrollToId(id), 350);
}
