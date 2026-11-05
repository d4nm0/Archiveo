// Service worker : ouvre chaque source dans un onglet en arrière-plan, injecte counter.js, renvoie le résultat.
const PARALLELE = 3;        // onglets simultanés
const TIMEOUT_MS = 25000;   // par source

chrome.runtime.onMessage.addListener((msg, sender) => {
  if (msg && msg.type === "search" && sender.tab) {
    lancer(msg, sender.tab.id, sender.frameId);
  }
});

async function lancer({ id, sources }, siteTabId, frameId) {
  const { fermer = true } = await chrome.storage.local.get("fermer");
  const file = [...sources];
  const resultats = [];
  const envoyer = (m) => chrome.tabs.sendMessage(siteTabId, m, { frameId }).catch(() => {});

  async function worker() {
    while (file.length) {
      const src = file.shift();
      const r = await compter(src, fermer);
      resultats.push(r);
      envoyer({ type: "result", id, ...r });
    }
  }
  await Promise.all(Array.from({ length: PARALLELE }, worker));
  await chrome.storage.local.set({ dernier: { id, quand: Date.now(), resultats } });
  envoyer({ type: "done", id, total: resultats.length });
}

function attendreChargement(tabId) {
  return new Promise((resolve) => {
    const fin = (tid, info) => {
      if (tid === tabId && info.status === "complete") { chrome.tabs.onUpdated.removeListener(fin); resolve(); }
    };
    chrome.tabs.onUpdated.addListener(fin);
    setTimeout(() => { chrome.tabs.onUpdated.removeListener(fin); resolve(); }, 15000);
  });
}

async function compter(src, fermer) {
  let tab;
  try {
    tab = await chrome.tabs.create({ url: src.url, active: false });
    await attendreChargement(tab.id);
    const injection = chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ["counter.js"] });
    const garde = new Promise((r) => setTimeout(() => r([{ result: { count: null, status: "délai dépassé" } }]), TIMEOUT_MS));
    const [{ result }] = await Promise.race([injection, garde]);
    return { nom: src.nom, url: src.url, ...(result || { count: null, status: "sans réponse" }) };
  } catch (e) {
    return { nom: src.nom, url: src.url, count: null, status: "erreur : " + (e.message || e) };
  } finally {
    if (tab && fermer) chrome.tabs.remove(tab.id).catch(() => {});
  }
}
