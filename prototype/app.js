(() => {
  "use strict";

  const STRINGS = window.SFERI_I18N;
  const LANGS = Object.keys(STRINGS);
  const DEFAULT_LANG = "me"; // the company is in Montenegro
  const STORE_KEY = "sferi-lang";
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  let lang = pickLanguage();

  // ---------- language ----------

  function pickLanguage() {
    const fromUrl = new URLSearchParams(location.search).get("lang");
    if (LANGS.includes(fromUrl)) return fromUrl;
    try {
      const saved = localStorage.getItem(STORE_KEY);
      if (LANGS.includes(saved)) return saved;
    } catch (_) { /* storage blocked: fall through */ }
    for (const tag of navigator.languages || [navigator.language]) {
      const base = String(tag).toLowerCase().split("-")[0];
      if (base === "ru" || base === "uk" || base === "be") return "ru";
      if (["sr", "me", "cnr", "hr", "bs"].includes(base)) return "me";
      if (base === "en") return "en";
    }
    return DEFAULT_LANG;
  }

  function t(key) {
    const table = STRINGS[lang];
    return key in table ? table[key] : STRINGS.ru[key];
  }

  // Line-break hygiene per language: a dash never starts a line, a range like
  // 3–5 and a number with its unit stay together, short prepositions and
  // conjunctions stay with the next word (Russian and Montenegrin rules).
  const NBSP = "\u00A0";
  const SHORT = {
    ru: /(^|[\s\u00A0(])(в|во|на|и|с|со|к|ко|о|об|у|из|за|до|от|по|не|а|но|что|для|без|при)\s/gi,
    me: /(^|[\s\u00A0(])(i|u|na|za|od|do|sa|s|k|o|a|ni|po|iz|bez|pri|je|se)\s/gi,
    en: /(^|[\s\u00A0(])(a|an|the|of|in|on|to|by|for|and|or|no)\s/gi,
  };
  function typeset(text) {
    let out = String(text)
      .replace(/ —/g, NBSP + "—")
      .replace(/(\d)–(\d)/g, "$1–\u2060$2")
      .replace(/(\d) (\d{3})\b/g, "$1" + NBSP + "$2")
      .replace(/(\d) (?=[^\s\d—–])/g, "$1" + NBSP)
      .replace(/≈ /g, "≈" + NBSP)
      .replace(/e-mail/g, "e-\u2060mail")
      .replace(/\?demo=error/g, "?\u2060demo\u2060=\u2060error");
    const rule = SHORT[lang];
    if (rule) out = out.replace(rule, "$1$2" + NBSP).replace(rule, "$1$2" + NBSP);
    return out;
  }

  function applyLanguage(next) {
    lang = next;
    const table = STRINGS[lang];
    document.documentElement.lang = table.htmlLang;
    document.title = table.title;
    document.querySelector('meta[name="description"]').setAttribute("content", table.description);

    document.querySelectorAll("[data-i18n]").forEach((el) => {
      el.textContent = typeset(t(el.dataset.i18n));
    });
    document.querySelectorAll("[data-i18n-aria]").forEach((el) => {
      el.setAttribute("aria-label", t(el.dataset.i18nAria));
    });
    document.querySelectorAll("[data-lang]").forEach((btn) => {
      btn.setAttribute("aria-pressed", String(btn.dataset.lang === lang));
    });

    syncProtoToggle();
    refreshVisibleErrors();
    try { localStorage.setItem(STORE_KEY, lang); } catch (_) { /* per-viewer convenience only */ }
  }

  document.querySelectorAll("[data-lang]").forEach((btn) => {
    btn.addEventListener("click", () => applyLanguage(btn.dataset.lang));
  });

  // ---------- header ----------

  const header = document.getElementById("header");
  const menu = document.getElementById("menu");
  const menuBtn = header.querySelector(".menu-btn");

  function setMenu(open) {
    menu.hidden = !open;
    menuBtn.setAttribute("aria-expanded", String(open));
    const label = menuBtn.querySelector("[data-i18n]");
    label.dataset.i18n = open ? "nav.close" : "nav.menu";
    label.textContent = t(label.dataset.i18n);
  }
  menuBtn.addEventListener("click", () => setMenu(menu.hidden));
  menu.addEventListener("click", (e) => { if (e.target.closest("a")) setMenu(false); });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !menu.hidden) { setMenu(false); menuBtn.focus(); }
  });
  window.matchMedia("(min-width: 68.0625rem)").addEventListener("change", (e) => { if (e.matches) setMenu(false); });

  const onScroll = () => header.classList.toggle("is-scrolled", window.scrollY > 8);
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // wayfinding: the link for the section in view is marked current
  const navLinks = [...document.querySelectorAll('.nav__list a, .menu__list a')];
  const sections = [...new Set(navLinks.map((a) => a.getAttribute("href")))]
    .map((href) => document.querySelector(href)).filter(Boolean)
    .concat(document.getElementById("top")); // back on the hero: nothing is current
  if ("IntersectionObserver" in window) {
    const spy = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        const id = "#" + entry.target.id;
        navLinks.forEach((a) => {
          if (a.getAttribute("href") === id) a.setAttribute("aria-current", "true");
          else a.removeAttribute("aria-current");
        });
      }
    }, { rootMargin: "-40% 0px -55% 0px" });
    sections.forEach((sec) => spy.observe(sec));
  }

  // ---------- hero: the wall opens into its layers, once ----------

  const wall = document.getElementById("wall");
  const figure = wall.querySelector(".wall-figure");
  if (figure && !reduceMotion) {
    figure.classList.add("is-assembled");
    requestAnimationFrame(() => requestAnimationFrame(() => {
      figure.classList.add("is-opening");
      figure.classList.remove("is-assembled");
    }));
  }

  // pointing at a layer name (or the layer itself) isolates it in the drawing
  const setActive = (name) => { if (name) wall.dataset.active = name; else delete wall.dataset.active; };
  wall.querySelectorAll(".wall__legend li, .wall-layer").forEach((el) => {
    el.addEventListener("pointerenter", () => setActive(el.dataset.layer));
    el.addEventListener("pointerleave", () => setActive(null));
  });

  // ---------- project price pills preset the floors field ----------

  document.querySelectorAll("[data-floors]").forEach((a) => {
    a.addEventListener("click", () => {
      const radio = document.getElementById("f-fl-" + a.dataset.floors);
      if (radio) radio.checked = true;
    });
  });

  // ---------- prototype notes toggle ----------

  const protoToggle = document.getElementById("proto-toggle");
  function syncProtoToggle() {
    const hidden = document.body.classList.contains("hide-proto");
    protoToggle.setAttribute("aria-pressed", String(hidden));
    protoToggle.dataset.i18n = hidden ? "proto.show" : "proto.hide";
    protoToggle.textContent = t(protoToggle.dataset.i18n);
  }
  protoToggle.addEventListener("click", () => {
    document.body.classList.toggle("hide-proto");
    syncProtoToggle();
  });

  // ---------- request form ----------

  const form = document.getElementById("request-form");
  const summary = document.getElementById("form-summary");
  const serverError = document.getElementById("form-server-error");
  const submit = document.getElementById("form-submit");
  const success = document.getElementById("form-success");
  const errors = {}; // field name -> i18n key of its current error

  const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const PHONE = /^\+?[\d\s()\-]{7,}$/;

  function validate() {
    const data = new FormData(form);
    const found = {};
    const name = String(data.get("name") || "").trim();
    const contact = String(data.get("contact") || "").trim();
    const area = String(data.get("area") || "").trim().replace(",", ".");

    if (!name) found.name = "form.errName";
    if (!contact) found.contact = "form.errContact";
    else if (!EMAIL.test(contact) && !PHONE.test(contact)) found.contact = "form.errContactFormat";
    if (area) {
      const n = Number(area);
      if (!Number.isFinite(n) || n < 20 || n > 1000) found.area = "form.errArea";
    }
    return found;
  }

  function showErrors(found) {
    for (const field of ["name", "contact", "area"]) {
      const wrap = form.querySelector(`[data-field="${field}"]`);
      const msg = wrap.querySelector(".field__error");
      const input = wrap.querySelector("input");
      if (found[field]) {
        errors[field] = found[field];
        wrap.classList.add("has-error");
        input.setAttribute("aria-invalid", "true");
        msg.querySelector("span").textContent = typeset(t(found[field]));
        msg.classList.add("is-shown");
      } else {
        delete errors[field];
        wrap.classList.remove("has-error");
        input.removeAttribute("aria-invalid");
        msg.classList.remove("is-shown");
        msg.querySelector("span").textContent = "";
      }
    }
    summary.hidden = Object.keys(found).length === 0;
  }

  function refreshVisibleErrors() {
    for (const [field, key] of Object.entries(errors)) {
      const span = form.querySelector(`[data-field="${field}"] .field__error span`);
      if (span) span.textContent = typeset(t(key));
    }
  }

  // once a field has shown an error, re-check it as the visitor fixes it
  form.addEventListener("input", (e) => {
    const field = e.target.closest("[data-field]");
    if (!field || !errors[field.dataset.field]) return;
    const found = validate();
    const keep = {};
    for (const f of Object.keys(errors)) if (found[f]) keep[f] = found[f];
    showErrors(keep);
  });

  function setSending(on) {
    submit.disabled = on;
    submit.setAttribute("aria-busy", String(on));
    submit.querySelector(".spinner").hidden = !on;
    const label = submit.querySelector(".btn__label");
    label.dataset.i18n = on ? "form.sending" : "form.submit";
    label.textContent = t(label.dataset.i18n);
  }

  // Prototype transport: nothing leaves the page. ?demo=error shows the failure path.
  function send() {
    const fail = new URLSearchParams(location.search).get("demo") === "error";
    return new Promise((resolve, reject) => setTimeout(fail ? reject : resolve, 1200));
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    serverError.hidden = true;
    const found = validate();
    showErrors(found);
    const first = Object.keys(found)[0];
    if (first) {
      // bring the summary into view below the sticky header, then focus the first bad field
      summary.scrollIntoView({ block: "start", behavior: reduceMotion ? "auto" : "smooth" });
      form.querySelector(`[name="${first}"]`).focus({ preventScroll: true });
      return;
    }

    setSending(true);
    try {
      await send();
      form.hidden = true;
      success.hidden = false;
      success.focus();
    } catch (_) {
      serverError.hidden = false;
      submit.focus();
    } finally {
      setSending(false);
    }
  });

  document.getElementById("form-again").addEventListener("click", () => {
    form.reset();
    success.hidden = true;
    form.hidden = false;
    form.querySelector("#f-name").focus();
  });

  applyLanguage(lang);
})();
