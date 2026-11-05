// Injecté dans chaque onglet de source : lit le nombre de résultats affiché.
// Extraction générique : cherche « N résultats / fiches / actes / individus… » dans le texte visible.
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const MOTS = "l[ée]gionnaires?|r[ée]sultats?|results?|fiches?|actes?|individus?|personnes?|notices?|documents?|occurrences?|enregistrements?|records?|matches?|entries|hits|d[ée]c[èe]s";
  const RE_N = new RegExp("(\\d[\\d\\s\\u00a0\\u202f.,]{0,12})\\s*(?:" + MOTS + ")\\b", "i");
  const RE_OF = new RegExp("(?:sur|of|de|parmi)\\s+(\\d[\\d\\s\\u00a0\\u202f.,]{0,12})\\s*(?:" + MOTS + ")?", "i");
  const RE_ZERO = /aucun(e)?\s+(r[ée]sultat|fiche|acte|individu|document|personne|l[ée]gionnaire)|no results?|0\s+r[ée]sultat|pas de r[ée]sultat/i;

  const toInt = (s) => parseInt(String(s).replace(/[\s  .,]/g, ""), 10);

  // Priorité des formulations : « N résultats » > « N … trouvés » > « 1-20 sur N » > autres mots.
  const PRIO = [
    [new RegExp("(\\d[\\d\\s\\u00a0\\u202f.,]{0,12})\\s*r[ée]sultats?\\b", "gi"), 3],
    [new RegExp("(\\d[\\d\\s\\u00a0\\u202f.,]{0,12})\\s*(?:" + MOTS + ")\\s+trouv[ée]e?s?", "gi"), 3],
    [new RegExp("(?:sur|of|parmi)\\s+(\\d[\\d\\s\\u00a0\\u202f.,]{0,12})(?:\\s*(?:" + MOTS + "))?", "gi"), 2],
    [new RegExp("(\\d[\\d\\s\\u00a0\\u202f.,]{0,12})\\s*(?:" + MOTS + ")\\b", "gi"), 1],
  ];
  function lire() {
    const txt = (document.body && document.body.innerText || "").slice(0, 30000);
    let best = null;
    for (const [re, prio] of PRIO) {
      for (const m of txt.matchAll(re)) {
        const n = toInt(m[1]); if (isNaN(n)) continue;
        // à priorité égale, on garde le plus grand nombre (le total plutôt que la taille de page)
        if (!best || prio > best.prio || (prio === best.prio && n > best.count)) best = { count: n, snippet: m[0].trim(), prio };
      }
      if (best) break;
    }
    if (best) return best;
    if (RE_ZERO.test(txt)) return { count: 0, snippet: (txt.match(RE_ZERO) || [""])[0] };
    return null;
  }

  // ---- Règles propres à certains sites ----
  // Base Léonore (Angular) : aucune URL de recherche ; on saisit le nom dans la barre et on valide.
  if (location.hostname.includes("leonore.archives-nationales")) {
    const nom = new URLSearchParams(location.search).get("q") || "";
    let input = null;
    for (let i = 0; i < 10 && !input; i++) { await sleep(600); input = document.querySelector('input[formcontrolname="text"]'); }
    if (input && nom) {
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
      setter.call(input, nom);
      input.dispatchEvent(new Event("input", { bubbles: true }));
      input.dispatchEvent(new KeyboardEvent("keyup", { key: "Enter", code: "Enter", keyCode: 13, bubbles: true }));
      const form = input.closest("form"); if (form) form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
    }
    // On attend l'apparition du compteur propre au site : « N légionnaires trouvés » / « aucun légionnaire trouvé ».
    for (let i = 0; i < 12; i++) {
      await sleep(1000);
      const t = document.body.innerText || "";
      const m = t.match(/(\d[\d\s\u00a0\u202f]*)\s*l[ée]gionnaires?\s+trouv[ée]s?/i);
      if (m) return { title: document.title, url: location.href, count: toInt(m[1]), status: "ok", snippet: m[0].trim() };
      if (/aucun l[ée]gionnaire trouv[ée]/i.test(t)) return { title: document.title, url: location.href, count: 0, status: "ok", snippet: "aucun légionnaire trouvé" };
    }
    return { title: document.title, url: location.href, count: null, status: "compteur non trouvé (Léonore)" };
  }

  // Les pages à rendu JavaScript mettent un moment : 4 essais espacés.
  let res = null;
  for (let i = 0; i < 4 && !res; i++) { await sleep(i === 0 ? 1500 : 2000); res = lire(); }

  const page = { title: document.title, url: location.href };
  if (!res) {
    const t = (document.body && document.body.innerText || "").toLowerCase();
    if (/connexion|se connecter|identifiez-vous|log in|sign in/.test(t) && !/d[ée]connexion|logout/.test(t)) {
      return { ...page, count: null, status: "connexion requise" };
    }
    if (/just a moment|vérification|verify you are human|captcha/.test(t)) {
      return { ...page, count: null, status: "vérification anti-robot" };
    }
    return { ...page, count: null, status: "nombre non trouvé" };
  }
  return { ...page, count: res.count, status: "ok", snippet: res.snippet };
})();
