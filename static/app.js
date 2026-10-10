/* AI Scooty Assistant - front end (no libraries needed) */
(function () {
  "use strict";

  var LS_CHAT = "aiscooty.chat.v1";     // the chat is remembered here, so a refresh keeps it
  var LS_THEME = "aiscooty.theme.v1";   // theme + accent color
  var MAX_SAVED = 80;                   // how many messages we keep
  var HISTORY_SENT = 6;                 // how many earlier messages the server sees (follow-ups)

  var BOLT = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13 2 5 14h6l-1 8 9-13h-6z"/></svg>';

  var $ = function (id) { return document.getElementById(id); };
  var el = {
    win: $("win"), messages: $("messages"), chips: $("chips"), form: $("composer"),
    input: $("input"), send: $("send"), settings: $("settings"), btnSettings: $("btnSettings"),
    taskChat: $("taskChat"), title: $("brandTitle")
  };

  var messages = [];                    // [{role, text, kind, suggestions, time}]
  var config = { brand: "AI Scooty", support_phone: "", starters: [] };
  var busy = false;

  /* ---------------------------------------------------------- storage helpers */
  function readJSON(key, fallback) {
    try { var raw = localStorage.getItem(key); return raw ? JSON.parse(raw) : fallback; }
    catch (e) { return fallback; }
  }
  function writeJSON(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) { /* private mode: ignore */ }
  }
  function saveChat() { writeJSON(LS_CHAT, messages.slice(-MAX_SAVED)); }

  /* ---------------------------------------------------------- theme */
  function applyTheme(theme) {
    document.documentElement.setAttribute("data-mode", theme.mode);
    document.documentElement.setAttribute("data-accent", theme.accent);
    var m = document.querySelector('input[name="mode"][value="' + theme.mode + '"]');
    var a = document.querySelector('input[name="accent"][value="' + theme.accent + '"]');
    if (m) m.checked = true;
    if (a) a.checked = true;
  }
  var theme = readJSON(LS_THEME, { mode: "system", accent: "blue" });
  applyTheme(theme);
  document.querySelectorAll('input[name="mode"], input[name="accent"]').forEach(function (inp) {
    inp.addEventListener("change", function () {
      theme[inp.name] = inp.value;
      applyTheme(theme);
      writeJSON(LS_THEME, theme);
    });
  });

  /* ---------------------------------------------------------- rendering */
  function timeLabel(ts) {
    return new Date(ts).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  }

  function pill(text) {
    var b = document.createElement("button");
    b.type = "button"; b.className = "pill"; b.textContent = text;
    b.addEventListener("click", function () { ask(text); });
    return b;
  }

  function renderMessage(m) {
    var row = document.createElement("div");
    row.className = "msg " + (m.role === "user" ? "user" : "bot") + (m.kind === "fallback" ? " fallback" : "");

    if (m.role !== "user") {
      var av = document.createElement("div");
      av.className = "avatar"; av.innerHTML = BOLT;
      row.appendChild(av);
    }
    var wrap = document.createElement("div");
    wrap.className = "bubble-wrap";
    var bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = m.text;            // textContent = safe, no HTML injection
    wrap.appendChild(bubble);

    if (m.suggestions && m.suggestions.length) {
      var box = document.createElement("div");
      box.className = "suggest";
      m.suggestions.forEach(function (s) { box.appendChild(pill(s)); });
      wrap.appendChild(box);
    }
    var t = document.createElement("div");
    t.className = "time"; t.textContent = timeLabel(m.time);
    wrap.appendChild(t);

    row.appendChild(wrap);
    el.messages.appendChild(row);
    return row;
  }

  function scrollDown() { el.messages.scrollTop = el.messages.scrollHeight; }

  function renderChips() {
    el.chips.innerHTML = "";
    var userSpoke = messages.some(function (m) { return m.role === "user"; });
    if (userSpoke) return;
    (config.starters || []).forEach(function (q) { el.chips.appendChild(pill(q)); });
  }

  function renderAll() {
    el.messages.innerHTML = "";
    messages.forEach(renderMessage);
    renderChips();
    scrollDown();
  }

  function addMessage(m) {
    m.time = Date.now();
    messages.push(m);
    renderMessage(m);
    saveChat();
    renderChips();
    scrollDown();
  }

  function showTyping() {
    var row = document.createElement("div");
    row.className = "msg bot typing";
    row.innerHTML = '<div class="avatar">' + BOLT + '</div><div class="bubble-wrap"><div class="bubble">' +
      '<span class="dot"></span><span class="dot"></span><span class="dot"></span></div></div>';
    el.messages.appendChild(row);
    scrollDown();
    return row;
  }

  function welcome() {
    addMessage({
      role: "bot", kind: "smalltalk",
      text: "Hello! I'm the " + config.brand + " Assistant. Ask me anything about " + config.brand + "."
    });
  }

  /* ---------------------------------------------------------- talking to the server */
  async function ask(text) {
    text = (text || "").trim();
    if (!text || busy) return;
    busy = true; el.send.disabled = true;

    var history = messages.slice(-HISTORY_SENT).map(function (m) {
      return { role: m.role === "user" ? "user" : "assistant", content: String(m.text).slice(0, 500) };
    });
    addMessage({ role: "user", text: text });
    el.input.value = "";
    var typing = showTyping();

    try {
      var res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, history: history })
      });
      if (!res.ok) throw new Error("HTTP " + res.status);
      var data = await res.json();
      typing.remove();
      addMessage({ role: "bot", text: data.answer, kind: data.kind, suggestions: data.suggestions });
    } catch (err) {
      typing.remove();
      var phone = config.support_phone ? " Or call our customer support directly: " + config.support_phone : "";
      addMessage({ role: "bot", kind: "fallback", text: "I can't reach the server right now. Please try again in a moment." + phone });
    } finally {
      busy = false; el.send.disabled = false; el.input.focus();
    }
  }

  el.form.addEventListener("submit", function (e) { e.preventDefault(); ask(el.input.value); });

  /* ---------------------------------------------------------- clear chat */
  function clearChat() {
    if (messages.length > 1 && !window.confirm("Clear this chat?")) return;
    messages = [];
    saveChat();
    el.messages.innerHTML = "";
    welcome();
  }
  $("btnClear").addEventListener("click", clearChat);
  $("btnClear2").addEventListener("click", function () { clearChat(); });

  /* ---------------------------------------------------------- window buttons */
  function setSettings(open) {
    el.settings.hidden = !open;
    el.btnSettings.setAttribute("aria-expanded", String(open));
  }
  function showWindow() {
    el.win.classList.remove("minimized");
    el.taskChat.classList.remove("is-min");
    el.input.focus();
  }
  function hideWindow() {
    el.win.classList.add("minimized");
    el.taskChat.classList.add("is-min");
  }
  el.btnSettings.addEventListener("click", function () { setSettings(el.settings.hidden); });
  $("taskSettings").addEventListener("click", function () { showWindow(); setSettings(el.settings.hidden); });
  $("btnMin").addEventListener("click", hideWindow);
  $("btnClose").addEventListener("click", hideWindow);
  $("btnMax").addEventListener("click", function () { el.win.classList.toggle("maximized"); });
  el.taskChat.addEventListener("click", function () {
    if (el.win.classList.contains("minimized")) showWindow(); else hideWindow();
  });
  $("deskIcon").addEventListener("click", showWindow);
  $("taskStart").addEventListener("click", showWindow);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !el.settings.hidden) setSettings(false);
  });

  /* ---------------------------------------------------------- clock */
  function tick() {
    var now = new Date();
    $("clockTime").textContent = now.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
    $("clockDate").textContent = now.toLocaleDateString();
  }
  tick(); setInterval(tick, 20000);

  /* ---------------------------------------------------------- start */
  async function start() {
    try {
      var res = await fetch("/api/config");
      if (res.ok) config = await res.json();
    } catch (e) { /* the page still works, just without starter questions */ }
    document.title = config.brand + " Assistant";
    el.title.textContent = config.brand + " Assistant";

    messages = readJSON(LS_CHAT, []);
    if (!Array.isArray(messages)) messages = [];
    if (messages.length) renderAll(); else welcome();
    el.input.focus();
  }
  start();
})();
