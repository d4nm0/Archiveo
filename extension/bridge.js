// Pont entre la page Archivéo et l'extension.
// Ne s'active que sur une page qui porte <meta name="archiveo" content="site">.
(() => {
  if (!document.querySelector('meta[name="archiveo"][content="site"]')) return;

  const say = (msg) => window.postMessage({ archiveo: true, ...msg }, "*");

  // Signale la présence de l'extension à la page.
  say({ type: "ready", version: chrome.runtime.getManifest().version });

  // La page demande une recherche : on relaie au service worker.
  window.addEventListener("message", (ev) => {
    if (ev.source !== window || !ev.data || !ev.data.archiveo) return;
    if (ev.data.type === "search") {
      chrome.runtime.sendMessage({ type: "search", id: ev.data.id, sources: ev.data.sources });
    }
    if (ev.data.type === "ping") say({ type: "ready", version: chrome.runtime.getManifest().version });
  });

  // Résultats renvoyés par le service worker → page.
  chrome.runtime.onMessage.addListener((msg) => {
    if (msg && (msg.type === "result" || msg.type === "done")) say(msg);
  });
})();
