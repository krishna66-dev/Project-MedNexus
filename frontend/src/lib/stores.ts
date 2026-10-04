import { writable } from "svelte/store";

export interface User {
  id: string;
  name: string;
  dob: string;
  age: number;
  email: string;
  role: "self" | "asha" | "anm" | "admin";
  region: string | null;
  phone: string | null;
  preferred_language: "en" | "hi";
  created_at: string;
}

function getStoredToken(): string | null {
  return typeof localStorage !== "undefined" ? localStorage.getItem("mednexus_token") : null;
}

function getStoredUser(): User | null {
  if (typeof localStorage === "undefined") return null;
  const raw = localStorage.getItem("mednexus_user");
  return raw ? (JSON.parse(raw) as User) : null;
}

export const token = writable<string | null>(getStoredToken());
export const currentUser = writable<User | null>(getStoredUser());

export function setSession(newToken: string, user: User) {
  localStorage.setItem("mednexus_token", newToken);
  localStorage.setItem("mednexus_user", JSON.stringify(user));
  token.set(newToken);
  currentUser.set(user);
}

export function clearSession() {
  localStorage.removeItem("mednexus_token");
  localStorage.removeItem("mednexus_user");
  token.set(null);
  currentUser.set(null);
}

// Currently active patient for the triage flow (esp. for ASHA/ANM with many patients)
export const selectedPatientId = writable<string | null>(null);
