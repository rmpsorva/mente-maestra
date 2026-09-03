const feed = document.getElementById("feed");
const form = document.getElementById("composer");
const box = document.getElementById("box");
const send = document.getElementById("send");
const status = document.getElementById("status");
const nuevo = document.getElementById("nuevo");

function add(role, text, meta) {
  const row = document.createElement("article");
  row.className = "row " + role;
  if (role === "bot") {
    const img = document.createElement("img");
    img.className = "ava";
    img.src = "/static/avatar.svg";
    img.alt = "Mente Maestra";
    row.appendChild(img);
  }
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  if (meta) {
    const m = document.createElement("div");
    m.className = "meta";
    m.textContent = meta;
    bubble.appendChild(m);
  }
  row.appendChild(bubble);
  feed.appendChild(row);
  feed.scrollTop = feed.scrollHeight;
  return bubble;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const texto = box.value.trim();
  if (!texto) return;
  add("user", texto);
  box.value = "";
  send.disabled = true;
  status.textContent = "pensando…";
  const wait = add("bot", "Percibiendo, planeando y recogiendo evidencia…");
  try {
    const res = await fetch("/pensar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto }),
    });
    if (!res.ok) throw new Error("HTTP " + res.status);
    const data = await res.json();
    wait.textContent = data.respuesta || data.tesis || "Sin respuesta";
    const meta = document.createElement("div");
    meta.className = "meta";
    meta.textContent = `confianza ${data.confianza} · ${ (data.intenciones || []).join(", ") } · memoria ${data.memoria_n}`;
    wait.appendChild(meta);
    status.textContent = "lista";
  } catch (err) {
    wait.textContent = "No pude completar el ciclo. Revisa que el servidor esté arriba.\n" + err;
    status.textContent = "error";
  } finally {
    send.disabled = false;
    box.focus();
    feed.scrollTop = feed.scrollHeight;
  }
});

box.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});

nuevo.addEventListener("click", () => location.reload());
