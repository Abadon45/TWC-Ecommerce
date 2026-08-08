$(function () {
    var $document = $(document);

    $document.on("click", ".update-cart", function (event) {
        event.preventDefault();

        var button = this;
        var productId = button.getAttribute("data-product");
        var action = button.getAttribute("data-action");
        var isDrawerQuantityButton = button.classList.contains("cart-drawer-qty-button");

        if (!productId || !action) {
            console.warn("Cart action skipped: missing product or action", { productId: productId, action: action });
            return;
        }

        var quantity = isDrawerQuantityButton ? 1 : getProductQuantity(productId);

        if (action === "remove") {
            confirmRemoval(productId, quantity, button);
        } else if (isDrawerQuantityButton) {
            updateCart(productId, action, quantity, button, true);
        } else {
            validateAndAdd(productId, quantity, button);
        }
    });

    function getProductQuantity(productId) {
        var input = document.querySelector(".input-" + productId) || document.querySelector(".quantity");
        var value = input ? parseInt(input.value, 10) : 1;
        return Number.isFinite(value) && value > 0 ? value : 1;
    }

    function confirmRemoval(productId, quantity, button) {
        Swal.fire({
            title: "Are you sure?",
            text: "Do you want to remove this item from your cart?",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Yes, remove it!"
        }).then(function (result) {
            if (result.isConfirmed) {
                updateCart(productId, "remove", quantity, button, false);
            }
        });
    }

    function validateAndAdd(productId, quantity, button) {
        if (typeof fetchProductQuantity !== "function") {
            updateCart(productId, "add", quantity, button, false);
            return;
        }

        fetchProductQuantity(productId)
            .done(function (response) {
                var available = parseInt(response.quantity, 10);
                var current = getCurrentCartQuantity(productId);

                if (response.supplier_product && Number.isFinite(available) && current + quantity > available) {
                    showCartToast("Only " + response.quantity + " item(s) are available.", "error");
                    return;
                }

                updateCart(productId, "add", quantity, button, false);
            })
            .fail(function () {
                // Stock lookup is auxiliary; do not prevent the cart update when
                // the legacy stock service is unavailable.
                updateCart(productId, "add", quantity, button, false);
            });
    }

    function getCurrentCartQuantity(productId) {
        var drawerItem = document.querySelector('[data-drawer-product="' + productId + '"] .cart-drawer-qty-value');
        var value = drawerItem ? parseInt(drawerItem.textContent, 10) : 0;
        return Number.isFinite(value) ? value : 0;
    }

    function updateCart(productId, action, quantity, button, isDrawerQuantityButton) {
        setButtonBusy(button, true);

        $.ajax({
            url: updateItemUrl,
            method: "GET",
            dataType: "json",
            data: { productId: productId, action: action, quantity: quantity }
        })
            .done(function (data) {
                if (data.max_order_exceeded) {
                    showCartToast(data.message || "The maximum order quantity was reached.", "error");
                    setButtonBusy(button, false);
                    return;
                }

                synchronizeCartUI(data, productId, action, isDrawerQuantityButton);
            })
            .fail(function (xhr) {
                var message = "Unable to update your cart.";
                if (xhr.responseJSON && (xhr.responseJSON.message || xhr.responseJSON.error)) {
                    message = xhr.responseJSON.message || xhr.responseJSON.error;
                }
                showCartToast(message, "error");
                setButtonBusy(button, false);
            });
    }

    function synchronizeCartUI(data, productId, action, isDrawerQuantityButton) {
        var cart = data.cart || {};
        var totalItems = Number(data.cart_items) || 0;
        var total = Number(data.total_cart_price) || 0;

        updateCartCounts(totalItems);
        syncProductButton(productId, action);

        if (!isCheckoutPage()) {
            renderCartDrawer(cart, total, totalItems);
            openCartDrawer();
        }

        if (action === "remove") {
            showCartToast("Item removed from your cart.", "error");
        } else if (!isDrawerQuantityButton) {
            showCartToast("Added to cart.", "success");
        }

        updateCheckoutFields(data, productId);
    }

    function updateCartCounts(totalItems) {
        $("#upper-cart-count, #lower-cart-count, #cart-drawer-count").text(totalItems);
    }

    function syncProductButton(productId, action) {
        $(".item-id-" + productId).each(function () {
            var productButton = $(this);
            if (productButton.hasClass("cart-drawer-qty-button")) return;

            if (action === "remove") {
                productButton
                    .text("ADD TO CART")
                    .removeClass("btn-secondary is-added")
                    .addClass("shop-product-add update-cart")
                    .attr({ "data-product": productId, "data-action": "add" })
                    .prop("disabled", false);
            } else {
                productButton
                    .text("ADDED TO CART")
                    .removeClass("theme-btn update-cart")
                    .addClass("shop-product-add is-added")
                    .prop("disabled", true);
            }
        });
    }

    function updateCheckoutFields(data, productId) {
        if (!isCheckoutPage()) return;

        var product = data.cart && data.cart[productId];
        if (!product) {
            window.location.reload();
            return;
        }

        $(".input-" + productId).val(product.quantity);
        $(".product-subtotal-" + productId).text("₱" + Number(product.get_total).toFixed(2));
    }

    function isCheckoutPage() {
        return window.location.pathname.indexOf("/cart/checkout") !== -1;
    }

    function setButtonBusy(button, busy) {
        if (!button || button.classList.contains("cart-drawer-remove")) return;
        button.disabled = busy;
        button.classList.toggle("is-cart-updating", busy);
    }

    function showCartToast(message, type) {
        var container = $("#cart-toast-container");
        if (!container.length) {
            container = $('<div id="cart-toast-container" class="cart-toast-container" aria-live="polite"></div>');
            $("body").append(container);
        }

        var icon = type === "success" ? "fas fa-check-circle" : "far fa-trash-can";
        var toast = $('<div class="cart-toast"></div>')
            .addClass(type === "success" ? "cart-toast-add" : "cart-toast-remove")
            .append($('<i aria-hidden="true"></i>').addClass(icon))
            .append($('<span></span>').text(message));

        container.append(toast);
        setTimeout(function () {
            toast.addClass("is-leaving");
            setTimeout(function () { toast.remove(); }, 250);
        }, 2600);
    }

    function renderCartDrawer(cart, total, count) {
        var list = $("#cart-drawer-list");
        if (!list.length) return;
        list.empty();

        var shops = {};
        Object.keys(cart).forEach(function (slug) {
            var item = cart[slug];
            var shop = item.shop || "Store";
            if (!shops[shop]) shops[shop] = [];
            shops[shop].push(item);
        });

        Object.keys(shops).forEach(function (shop) {
            var section = $('<section class="cart-drawer-shop"></section>');
            section.append($('<h3></h3>').text("Shop: " + shop));

            shops[shop].forEach(function (item) {
                var row = $('<article class="cart-drawer-item"></article>').attr("data-drawer-product", item.slug);
                var image = $('<div class="cart-drawer-image"></div>').append($('<img>').attr({
                    src: item.image || "/static/img/product/default-product-image.png",
                    alt: item.name
                }));
                var copy = $('<div class="cart-drawer-item-copy"></div>')
                    .append($('<strong></strong>').text(item.name))
                    .append($('<span></span>').text(item.quantity + " × ₱" + Number(item.price).toLocaleString("en-US", { minimumFractionDigits: 2 })));
                var controls = $('<div class="cart-drawer-qty"></div>').attr("aria-label", "Quantity for " + item.name);
                var minus = $('<button type="button" class="cart-drawer-qty-button update-cart">−</button>')
                    .attr({ "data-product": item.slug, "data-action": "minus", "aria-label": "Decrease quantity" })
                    .prop("disabled", Number(item.quantity) <= 1);
                var plus = $('<button type="button" class="cart-drawer-qty-button update-cart">+</button>')
                    .attr({ "data-product": item.slug, "data-action": "add", "aria-label": "Increase quantity" });
                controls.append(minus, $('<span class="cart-drawer-qty-value"></span>').text(item.quantity), plus);
                copy.append(controls);

                var remove = $('<button type="button" class="cart-drawer-remove update-cart"><i class="far fa-trash-can" aria-hidden="true"></i></button>')
                    .attr({ "data-product": item.slug, "data-action": "remove", "aria-label": "Remove " + item.name });
                row.append(image, copy, remove);
                section.append(row);
            });
            list.append(section);
        });

        if (!Object.keys(cart).length) {
            list.append('<div class="cart-drawer-empty"><strong>Your basket is empty</strong><span>Add something good to get started.</span></div>');
        }
        $("#cart-drawer-count").text(count);
        $("#cart-drawer-total").text("₱" + total.toLocaleString("en-US", { minimumFractionDigits: 2 }));
    }

    function openCartDrawer() {
        $("#cart-drawer").addClass("is-open").attr("aria-hidden", "false");
        $("body").addClass("cart-drawer-open");
    }
});
