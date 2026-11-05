const cb = document.getElementById("fermer");
chrome.storage.local.get(["fermer", "dernier"]).then(({ fermer = true, dernier }) => {
  cb.checked = fermer;
  if (dernier) {
    const d = new Date(dernier.quand);
    let h = `<div class="m">Dernière recherche : ${d.toLocaleString("fr-FR")}</div><table>`;
    for (const r of dernier.resultats) h += `<tr><td>${r.nom}</td><td>${r.count === null ? r.status : r.count.toLocaleString("fr-FR")}</td></tr>`;
    document.getElementById("dernier").innerHTML = h + "</table>";
  }
});
cb.addEventListener("change", () => chrome.storage.local.set({ fermer: cb.checked }));
