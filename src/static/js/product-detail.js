(function ($) {
    "use strict";
    $(function () {
        var gallery = $("[data-product-gallery]");
        gallery.on("click", "[data-gallery-image]", function () {
            var button = $(this), main = gallery.find("[data-gallery-main]");
            main.attr("src", button.data("gallery-image"));
            gallery.find(".gallery-thumb").removeClass("is-active");
            button.addClass("is-active");
        });
        var quantity = $("[data-product-quantity]");
        if (quantity.length) {
            var input = quantity.find(".quantity"), total = $("[data-product-total]"), unit = Number(quantity.data("unit-price")) || 0;
            function refresh() {
                var value = Math.max(1, Math.min(10, parseInt(input.val(), 10) || 1));
                input.val(value);
                total.text("₱" + (unit * value).toLocaleString("en-PH", {minimumFractionDigits: 2, maximumFractionDigits: 2}));
            }
            quantity.on("click", "[data-quantity-action]", function () {
                var value = parseInt(input.val(), 10) || 1;
                input.val(value + ($(this).data("quantity-action") === "increase" ? 1 : -1));
                refresh();
            });
            input.on("input change", refresh);
            refresh();
        }
        $("[data-product-share]").on("click", function () {
            if (navigator.share) navigator.share({title: document.title, url: window.location.href});
            else if (navigator.clipboard) navigator.clipboard.writeText(window.location.href);
        });
    });
}(jQuery));
