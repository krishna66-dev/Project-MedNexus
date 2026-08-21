import { writable, derived } from "svelte/store";
import { en } from "./en";
import { hi } from "./hi";
import type { TranslationSchema } from "./en";

export type Lang = "en" | "hi";

const dictionaries: Record<Lang, TranslationSchema> = { en, hi };

function getInitialLang(): Lang {
  const saved = typeof localStorage !== "undefined" ? localStorage.getItem("mednexus_lang") : null;
  if (saved === "en" || saved === "hi") return saved;
  return "en";
}

export const lang = writable<Lang>(getInitialLang());

lang.subscribe((value) => {
  if (typeof localStorage !== "undefined") {
    localStorage.setItem("mednexus_lang", value);
  }
  if (typeof document !== "undefined") {
    document.documentElement.setAttribute("lang", value);
  }
});

export function toggleLang() {
  lang.update((cur) => (cur === "en" ? "hi" : "en"));
}

export function setLang(l: Lang) {
  lang.set(l);
}

// `t` is a derived store: subscribe to it (or use `$t.nav.home` in Svelte) to
// get the full translation object for the currently-selected language.
export const t = derived(lang, ($lang) => dictionaries[$lang]);
