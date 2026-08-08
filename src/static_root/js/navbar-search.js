(function () {
    function initializeSearch() {
        var form = document.querySelector(".navbar-search-form");
        var input = document.getElementById("navbar-search-input");
        var clearButton = document.querySelector(".navbar-search-clear");

        if (!form || !input) return;

        function updateClearButton() {
            if (!clearButton) return;
            clearButton.hidden = input.value.trim().length === 0;
        }

        input.addEventListener("input", updateClearButton);
        form.addEventListener("submit", function (event) {
            var query = input.value.trim();
            if (!query) {
                event.preventDefault();
                input.focus();
                return;
            }
            input.value = query;
        });

        if (clearButton) {
            clearButton.addEventListener("click", function () {
                input.value = "";
                updateClearButton();
                input.focus();
            });
        }

        updateClearButton();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initializeSearch);
    } else {
        initializeSearch();
    }
}());
