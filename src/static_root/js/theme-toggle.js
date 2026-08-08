(function () {
    function setTheme(theme) {
        var isDark = theme === "dark";
        document.documentElement.setAttribute("data-theme", isDark ? "dark" : "light");
        localStorage.setItem("twc-theme", isDark ? "dark" : "light");

        var toggle = document.getElementById("theme-toggle");
        if (toggle) {
            toggle.setAttribute("aria-checked", String(isDark));
            toggle.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");
            toggle.title = isDark ? "Switch to light mode" : "Switch to dark mode";
        }
    }

    function initialize() {
        var currentTheme = document.documentElement.getAttribute("data-theme") || "light";
        setTheme(currentTheme);

        var toggle = document.getElementById("theme-toggle");
        if (toggle) {
            toggle.addEventListener("click", function () {
                setTheme(document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark");
            });
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initialize);
    } else {
        initialize();
    }
}());
