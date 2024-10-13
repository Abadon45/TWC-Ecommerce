$(document).ready(function () {

    $(document).on("click", ".update-cart", function (event) {
        event.preventDefault();
        var button = $(this);
        var shop = button.data("shop")
        var productId = button.data("product");
        var orderId = button.data("order-id");
        var action = button.data("action");
        var quantityInput = $("#quantity");
        var quantity = parseInt(quantityInput.val()) || 1;

        console.log("Product Slug: " + productId)
        console.log("Quantity: ", quantity)

        if (action === 'remove') {
            Swal.fire({
                title: 'Are you sure?',
                text: "Do you want to remove this item from your cart?",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, remove it!'
            }).then((result) => {
                if (result.isConfirmed) {
                    Swal.fire({
                        title: 'Removing...',
                        allowOutsideClick: false,
                        didOpen: () => {
                            Swal.showLoading();
                        }
                    });
                    setTimeout(() => {
                        updateUserOrder(productId, action, quantity, updateItemUrl, button);
                        Swal.close();
                    }, 1000);
                }
            });
        } else {
            updateUserOrder(productId, action, quantity, updateItemUrl, button);
        }
    });

    function updateUserOrder(productId, action, quantity, url, button) {
        $.ajax({
            url: url,
            method: "GET",
            dataType: "json",
            data: {
                productId: productId,
                action: action,
                quantity: quantity,
            },
            success: function (data) {
                // Check if the order quantity exceeds the limit
                console.log("Data from add to cart: ", data)

                // Access basic data
                var totalItems = data.cart_items;
                var totalCartPrice = data.total_cart_price;
                var subtotal = data.subtotal !== undefined && data.subtotal !== null ? data.subtotal : 0;

                // Access individual products in the cart
                var cart = data.cart;
                var shop_cart = data.shop_cart
                var productData = cart[productId];
                var cartHtml = '';
                var shop = button.data("shop")

                console.log("shop_cart[shop]:", shop_cart[shop]);

                // logic to update the cart
                var formattedCartItems = String(totalItems).padStart(2, "0");
                var orderTotal = parseFloat(totalCartPrice).toLocaleString(
                    "en-US",
                    {
                        minimumFractionDigits: 2,
                    }
                );

                console.log("Max Order: " + data.max_order_exceeded)
                if (data.max_order_exceeded) {
                    Swal.fire({
                        title: 'Order Quantity Limit Exceeded!',
                        text: data.message,
                        icon: 'error',
                        confirmButtonText: 'OK'
                    });
                    return; // Stop further processing if the limit is exceeded
                }

                var cartDropdownHtml = `
                    <div class="dropdown-cart-menu">
                        <div class="dropdown-cart-header">
                            <span class="cart-items-count">${formattedCartItems} ITEMS</span>
                            <a href="/cart">View Cart</a>
                        </div>
                        <ul id="dropdown-cart-list">
                            <!--insert dropdown cart items here-->
                        </ul>
                        <div class="dropdown-cart-bottom">
                            <div class="dropdown-cart-total">
                                <span>Total</span>
                                <span class="total-amount">${orderTotal}</span>
                            </div>
                            <a href="/cart" class="theme-btn">Checkout</a>
                        </div>
                    </div>`;

                // Iterate over the products in the cart
                for (var slug in cart) {
                    if (cart.hasOwnProperty(slug)) {
                        var item = cart[slug]; // Each product in the cart

                        cartHtml += `
                          <li id="cart-row-${item.id}">
                              <div class="dropdown-cart-item">
                                  <div class="cart-img">
                                      <a href="/shop/single/${item.slug}">
                                          ${item.image ? `<img src="${item.image}" alt="${item.name}">` : '<img src="/static/img/product/default-product-image.png" alt="Default Product Image">'}
                                      </a>
                                  </div>
                                  <div class="cart-info">
                                      <h4><a href="/shop/single/${item.slug}">${item.name}</a></h4>
                                      <p class="cart-qty">${item.quantity}x - <span class="cart-amount">₱${item.get_total.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}</span></p>
                                  </div>
                                  <a href="#" data-product="${item.slug}" data-action="remove" class="update-cart shop-cart-remove">
                                      <i class="far fa-times-circle"></i>
                                  </a>
                              </div>
                          </li>`;
                    }
                }

                //Update Cart Count
                $("#upper-cart-count").text(totalItems);
                $("#lower-cart-count").text(totalItems);

                if ($('#cart-dropdown').text().trim() === "") {
                    $('#cart-dropdown').html(cartDropdownHtml);
                }
                $("#dropdown-cart-list").empty().append(cartHtml);
                $('.cart-items-count').text(formattedCartItems + " ITEMS");

                if (totalItems === 0) {
                    $('#cart-dropdown').empty();
                }

                //Disable add to cart button after product is added
                if (action === 'remove') {
                    $(".item-id-" + productId)
                        .text("ADD TO CART")
                        .removeClass("btn-secondary")
                        .addClass("theme-btn update-cart")
                        .prop("disabled", false)

                    location.reload();
                } else {
                    $(".item-id-" + productId)
                        .text("ADDED TO CART")
                        .removeClass("theme-btn")
                        .addClass("btn-secondary")
                        .prop("disabled", true)

                    if (isCartPage()) {

                        // CART PAGE
                        if (productData.quantity === 1) {
                            $('.minus-btn[data-product="' + productId + '"]').prop("disabled", true);
                        } else {
                            $('.minus-btn[data-product="' + productId + '"]').prop("disabled", false);
                        }

                        $('.input-' + productId).val(productData.quantity)
                        $('.product-subtotal-' + productId).text("₱" + productData.get_total.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ','))
                        $('#order-subtotal-' + shop).text("₱" + shop_cart[shop].subtotal.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ','))
                        $('#order-total-' + shop).text("₱" + shop_cart[shop].cod_amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ','))
                        $('.total-amount').text("₱" + orderTotal)
                    }

                }

                if (!isCartPage()) {
                    Swal.fire({
                        icon: "success",
                        title: "Success",
                        text: "Cart updated successfully!",
                        timer: 1500,
                        timerProgressBar: true,
                        showConfirmButton: false,
                        didOpen: () => {
                            Swal.showLoading();
                        },
                    });
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.error("AJAX Error:", textStatus, errorThrown);

            },
        });
    }

    function isCartPage() {
        return window.location.pathname.includes("/cart/");
    }
});
