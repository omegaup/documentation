/* Reset Material/Zensical chrome after search (?h=), drawer, or bfcache — applies site-wide. */
(function () {
  function resetChromeState() {
    var root = document.documentElement;
    root.classList.remove("no-js");
    root.classList.add("js");
    var search = document.getElementById("__search");
    if (search) search.checked = false;
    var drawer = document.getElementById("__drawer");
    if (drawer) drawer.checked = false;
  }
  function schedule() {
    requestAnimationFrame(function () {
      requestAnimationFrame(resetChromeState);
    });
    setTimeout(resetChromeState, 0);
    setTimeout(resetChromeState, 120);
    setTimeout(resetChromeState, 400);
  }
  schedule();
  document.addEventListener("DOMContentLoaded", schedule);
  window.addEventListener("load", schedule);
  window.addEventListener("pageshow", function (ev) {
    schedule();
    if (ev.persisted) schedule();
  });
  window.addEventListener("popstate", schedule);
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "visible") schedule();
  });
})();
