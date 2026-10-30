// CareerTrack front-end helpers
document.addEventListener("DOMContentLoaded", () => {
    console.log("CareerTrack dashboard loaded successfully!");

    // Auto-dismiss flash messages after 4s
    document.querySelectorAll(".flash").forEach((el) => {
        setTimeout(() => {
            el.style.transition = "opacity 0.4s ease";
            el.style.opacity = "0";
            setTimeout(() => el.remove(), 400);
        }, 4000);
    });
});
/* ================= DARK MODE ================= */
(function initTheme() {
    const saved = localStorage.getItem("theme");
    if (saved === "dark") {
        document.documentElement.setAttribute("data-theme", "dark");
    } else if (saved === "light") {
        document.documentElement.removeAttribute("data-theme");
    } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
        // first visit: follow OS preference
        document.documentElement.setAttribute("data-theme", "dark");
    }
})();

function toggleTheme() {
    const html = document.documentElement;
    const isDark = html.getAttribute("data-theme") === "dark";
    if (isDark) {
        html.removeAttribute("data-theme");
        localStorage.setItem("theme", "light");
    } else {
        html.setAttribute("data-theme", "dark");
        localStorage.setItem("theme", "dark");
    }
    syncThemeIcon();
}

function syncThemeIcon() {
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    document.querySelectorAll(".theme-toggle i").forEach((el) => {
        el.className = isDark ? "fa-solid fa-sun" : "fa-solid fa-moon";
    });
}

document.addEventListener("DOMContentLoaded", syncThemeIcon);
/* ================= ANIMATED COUNTERS ================= */
function animateCounters() {
    document.querySelectorAll(".stat-card h2").forEach((el) => {
        const target = parseInt(el.textContent.trim(), 10);
        if (isNaN(target) || target === 0) return;

        const duration = 900;
        const start = performance.now();
        const startVal = 0;

        function step(now) {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
            el.textContent = Math.round(startVal + (target - startVal) * eased);
            if (progress < 1) requestAnimationFrame(step);
            else el.textContent = target;
        }
        el.textContent = "0";
        requestAnimationFrame(step);
    });
}

document.addEventListener("DOMContentLoaded", animateCounters);
/* ================= TABLE SEARCH / FILTER / SORT ================= */
(function initTableControls() {
    const searchInput = document.getElementById("searchInput");
    const statusFilter = document.getElementById("statusFilter");
    const sortSelect = document.getElementById("sortSelect");
    const tbody = document.querySelector("#recentApplications, .applications-table tbody");

    if (!searchInput || !statusFilter || !sortSelect || !tbody) return;

    const originalRows = Array.from(tbody.querySelectorAll("tr[data-company]"));
    if (originalRows.length === 0) return;

    const noResultsRow = document.createElement("tr");
    noResultsRow.className = "no-results-row";
    noResultsRow.innerHTML = `
        <td colspan="4" class="no-results">
            <i class="fa-solid fa-magnifying-glass"></i>
            <p>No applications match your filters</p>
            <span>Try changing the search or status filter.</span>
        </td>`;
    noResultsRow.style.display = "none";

    function applyFilters() {
        const q = searchInput.value.toLowerCase().trim();
        const status = statusFilter.value;
        const sortMode = sortSelect.value;

        let visible = originalRows.filter((row) => {
            const company = (row.dataset.company || "").toLowerCase();
            const role = (row.dataset.role || "").toLowerCase();
            const rowStatus = row.dataset.status || "";
            const matchesQuery = !q || company.includes(q) || role.includes(q);
            const matchesStatus = !status || rowStatus === status;
            return matchesQuery && matchesStatus;
        });

        visible.sort((a, b) => {
            switch (sortMode) {
                case "date-asc":
                    return a.dataset.date.localeCompare(b.dataset.date);
                case "company-asc":
                    return a.dataset.company.localeCompare(b.dataset.company);
                case "company-desc":
                    return b.dataset.company.localeCompare(a.dataset.company);
                case "status":
                    return a.dataset.status.localeCompare(b.dataset.status);
                case "date-desc":
                default:
                    return b.dataset.date.localeCompare(a.dataset.date);
            }
        });

        // Remove everything except the no-results row
        tbody.querySelectorAll("tr").forEach((r) => r.remove());

        if (visible.length === 0) {
            tbody.appendChild(noResultsRow);
            noResultsRow.style.display = "";
        } else {
            visible.forEach((row) => tbody.appendChild(row));
        }

        const visibleCount = document.getElementById("visibleCount");
        if (visibleCount) visibleCount.textContent = visible.length;
    }

    searchInput.addEventListener("input", applyFilters);
    statusFilter.addEventListener("change", applyFilters);
    sortSelect.addEventListener("change", applyFilters);

    // Run once on load so sort order is applied immediately
    applyFilters();
})();