(function () {
    function getDrawer() {
        return document.getElementById("cart-drawer");
    }

    function openDrawer() {
        var drawer = getDrawer();
        if (!drawer) return;
        drawer.classList.add("is-open");
        drawer.setAttribute("aria-hidden", "false");
        document.body.classList.add("cart-drawer-open");
    }

    function closeDrawer() {
        var drawer = getDrawer();
        if (!drawer) return;
        drawer.classList.remove("is-open");
        drawer.setAttribute("aria-hidden", "true");
        document.body.classList.remove("cart-drawer-open");
    }

    document.addEventListener("click", function (event) {
        var target = event.target.closest
            ? event.target.closest("[data-cart-drawer-open]")
            : null;
        if (target) {
            event.preventDefault();
            openDrawer();
            return;
        }

        var closeTarget = event.target.closest
            ? event.target.closest("[data-cart-drawer-close]")
            : null;
        if (closeTarget) {
            event.preventDefault();
            closeDrawer();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") closeDrawer();
    });
})();
