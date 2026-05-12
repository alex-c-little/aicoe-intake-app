/*
 * Optional progressive enhancement layer.
 *
 * The app is fully functional without this file. Disable it by setting
 * ENABLE_JS_ENHANCEMENTS=false in .env, or just delete this file.
 *
 * What it adds:
 *   1. Drag-and-drop between kanban columns (calls /usecase/<id>/status)
 *   2. Live search filter as you type
 *   3. Async detail-pane swap on card click (no full page reload)
 *   4. Async status update on the detail-pane form
 */
(function () {
  "use strict";

  // ---------- 1. Drag and drop ----------
  function initDragDrop() {
    const cards = document.querySelectorAll("[data-card]");
    const zones = document.querySelectorAll("[data-drop-zone]");

    cards.forEach((card) => {
      card.addEventListener("dragstart", (e) => {
        e.dataTransfer.setData("text/plain", card.dataset.id);
        e.dataTransfer.effectAllowed = "move";
        card.classList.add("dragging");
      });
      card.addEventListener("dragend", () => card.classList.remove("dragging"));
    });

    zones.forEach((zone) => {
      zone.addEventListener("dragover", (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = "move";
        zone.classList.add("drag-over");
      });
      zone.addEventListener("dragleave", () => zone.classList.remove("drag-over"));
      zone.addEventListener("drop", async (e) => {
        e.preventDefault();
        zone.classList.remove("drag-over");
        const id = e.dataTransfer.getData("text/plain");
        const newStatus = zone.closest("[data-status]").dataset.status;
        const card = document.querySelector(`[data-card][data-id="${id}"]`);
        if (!card || !newStatus) return;
        if (card.dataset.status === newStatus) return;

        // optimistic move
        zone.appendChild(card);
        card.dataset.status = newStatus;
        updateColumnCounts();

        try {
          const resp = await fetch(`/usecase/${id}/status`, {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-Requested-With": "fetch" },
            body: JSON.stringify({ status: newStatus }),
          });
          if (!resp.ok) throw new Error("status update failed");
        } catch (err) {
          console.error(err);
          alert("Failed to update status — reloading.");
          window.location.reload();
        }
      });
    });
  }

  function updateColumnCounts() {
    document.querySelectorAll(".board-column").forEach((col) => {
      const n = col.querySelectorAll("[data-card]").length;
      const badge = col.querySelector(".board-column__count");
      if (badge) badge.textContent = n;
    });
  }

  // ---------- 2. Live search filter ----------
  function initLiveFilter() {
    const input = document.querySelector("[data-live-filter]");
    if (!input) return;

    let timer;
    input.addEventListener("input", () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        const q = input.value.toLowerCase().trim();
        document.querySelectorAll("[data-card]").forEach((card) => {
          const text = card.textContent.toLowerCase();
          card.style.display = !q || text.includes(q) ? "" : "none";
        });
        updateColumnCounts();
      }, 100);
    });
  }

  // ---------- 3. Async detail pane swap ----------
  function initDetailPaneSwap() {
    document.addEventListener("click", async (e) => {
      const card = e.target.closest("[data-card]");
      if (!card) return;
      if (e.metaKey || e.ctrlKey || e.shiftKey) return;
      e.preventDefault();

      const id = card.dataset.id;
      const boardPage = document.querySelector(".board-page");
      const url = new URL(window.location.href);
      url.searchParams.set("selected", id);
      window.history.pushState({}, "", url);

      try {
        const resp = await fetch(`/usecase/${id}/fragment`);
        if (!resp.ok) throw new Error("fragment fetch failed");
        const html = await resp.text();

        let pane = document.querySelector("[data-detail-pane]");
        if (!pane) {
          pane = document.createElement("aside");
          pane.className = "detail-pane";
          pane.dataset.detailPane = "";
          boardPage.appendChild(pane);
          boardPage.classList.add("board-page--with-detail");
        }
        pane.innerHTML = html;

        document.querySelectorAll("[data-card]").forEach((c) => c.classList.remove("card--selected"));
        card.classList.add("card--selected");
      } catch (err) {
        console.error(err);
        window.location.href = card.href;
      }
    });

    document.addEventListener("click", (e) => {
      const close = e.target.closest(".detail__close");
      if (!close) return;
      e.preventDefault();
      const pane = document.querySelector("[data-detail-pane]");
      if (pane) pane.remove();
      document.querySelector(".board-page")?.classList.remove("board-page--with-detail");
      document.querySelectorAll("[data-card]").forEach((c) => c.classList.remove("card--selected"));
      const url = new URL(window.location.href);
      url.searchParams.delete("selected");
      window.history.pushState({}, "", url);
    });
  }

  // ---------- 4. Async status form submit ----------
  function initStatusFormSwap() {
    document.addEventListener("submit", async (e) => {
      const form = e.target.closest("[data-status-form]");
      if (!form) return;
      e.preventDefault();

      const action = form.getAttribute("action");
      const status = form.querySelector("select[name=status]").value;
      const resp = await fetch(action, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Requested-With": "fetch" },
        body: JSON.stringify({ status }),
      });
      if (!resp.ok) {
        alert("Status update failed.");
        return;
      }
      const id = action.match(/\/usecase\/([^/]+)\//)[1];
      const card = document.querySelector(`[data-card][data-id="${id}"]`);
      const targetZone = document.querySelector(`.board-column[data-status="${status}"] [data-drop-zone]`);
      if (card && targetZone) {
        targetZone.appendChild(card);
        card.dataset.status = status;
        updateColumnCounts();
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initDragDrop();
    initLiveFilter();
    initDetailPaneSwap();
    initStatusFormSwap();
  });

  window.addEventListener("popstate", () => window.location.reload());
})();
