$(document).ready(function () {
  var spinner = $(".sk-circle");
  var backdrop = $(".backdrop");

  $(document).on("click", ".update-cart", function (event) {
    event.preventDefault();
    var button = $(this);
    var productId = button.data("product");
    var orderId = button.data("order-id");
    var action = button.data("action");
    var quantityInput = $("#quantity-input-" + productId);
    var quantity = parseInt(quantityInput.val()) || 1;

    console.log(
      "Product ID:",
      productId,
      "Action:",
      action,
      "Quantity:",
      quantity
    );

    spinner.addClass("visible"); // Show the spinner
    backdrop.addClass("visible");

    if (!isCartPage()) {
      Swal.fire({
        icon: "success",
        title: "Success",
        text: "Cart updated successfully!",
        timer: 2000,
        showConfirmButton: false,
      });
    }

    updateUserOrder(
      productId,
      orderId,
      action,
      quantity,
      updateItemUrl,
      button
    );
  });

  function updateUserOrder(productId, orderId, action, quantity, url, button) {
    $.ajax({
      url: url,
      method: "GET",
      dataType: "json",
      data: {
        productId: productId,
        orderId: orderId,
        action: action,
        quantity: quantity,
      },
      success: function (data) {
        console.log("Server Response Data:", data);
        console.log("Quantity:", quantity);
        console.log("Cart Items Count:", data.cart_items);
        console.log("Order ID:", orderId);

        spinner.removeClass("visible");
        backdrop.removeClass("visible");

        $("#cart-count").text(data.cart_items);

        var formattedCartItems = String(data.cart_items).padStart(2, "0");
        if (data.action === "add") {
          if (data.cart_items === 1) {
            var dropdownHtml = `
                    <div class="dropdown-cart-menu">
                        <div class="dropdown-cart-header">
                          <span class="cart-items-count">${formattedCartItems} Items</span>
                            <a href="{% url_with_domain 'cart:cart' %}">View Cart</a>
                        </div>
                        <ul class="dropdown-cart-list">
                            <li id="cart-row-${data.products[0].id}">
                                <div class="dropdown-cart-item">
                                    <div class="cart-img">
                                        <a href="${data.products[0].url}"><img src="${data.products[0].image}" alt="${data.products[0].name}"></a>
                                    </div>
                                    <div class="cart-info">
                                        <h4><a href="${data.products[0].url}">${data.products[0].name}</a></h4>
                                        <p class="cart-qty">${data.products[0].quantity}x - <span class="cart-amount">${data.products[0].total}</span></p>
                                    </div>
                                    <a href="#" data-product="${data.products[0].id}" data-action="remove" class="update-cart shop-cart-remove">
                                        <i class="far fa-times-circle"></i>
                                    </a>
                                </div>
                            </li>
                        </ul>
                        <div class="dropdown-cart-bottom">
                            <div class="dropdown-cart-total">
                                <span>Total</span>
                                <span class="total-amount">${data.total_cart_subtotal}</span>
                            </div>
                            <a href="{% url_with_domain 'cart:cart' %}" class="theme-btn">Checkout</a>
                        </div>
                    </div>`;

            $("#cart-dropdown").append(dropdownHtml);
          } else if (data.cart_items > 1) {
              var existingProduct = $("#cart-row-" + data.products[0].id);
                // Append each additional product to the dropdown menu list
                var dropdownMenu = $("#cart-dropdown .dropdown-cart-menu");
                data.products.forEach(function (product) {
                  var productHtml = `
                      <li id="cart-row-${product.id}">
                          <div class="dropdown-cart-item">
                              <div class="cart-img">
                                  <a href="${product.url}"><img src="${product.image}" alt="${product.name}"></a>
                              </div>
                              <div class="cart-info">
                                  <h4><a href="${product.url}">${product.name}</a></h4>
                                  <p class="cart-qty">${product.quantity}x - <span class="cart-amount">₱${product.total}</span></p>
                              </div>
                              <a href="#" data-product="${product.id}" data-action="remove" class="update-cart shop-cart-remove">
                                  <i class="far fa-times-circle"></i>
                              </a>
                          </div>
                      </li>`;
                    if (existingProduct.length > 0) {
                      $("#cart-row-" + productId).remove();
                    }
                  dropdownMenu.find(".dropdown-cart-list").append(productHtml);
                  $(".cart-items-count").text(formattedCartItems + " Items");
                });
              }
        }

        if (button && button.length > 0 && !button.hasClass("excludeDisable")) {
          console.log("Before disabling minus button");
          button.prop("disabled", true);
          button
            .removeClass("theme-btn add-to-cart-btn")
            .addClass("btn btn-dark");
          if (button.text() === "Add To Cart") {
            button.text("Added To Cart");
          }
        }

        if (data.products.length > 0) {
          if (data.action !== "remove") {
            $("#product-subtotal-" + productId).text(data.products[0].total);
          }

          if (data.action === "remove") {
            console.log("Removing product with ID:", productId);
            $("#product-row-" + productId).remove();
            $("#cart-row-" + productId).remove();
          }

          if (data.cart_items === 0) {
            // Check if the order table becomes empty
            $(".dropdown-cart-menu").remove();
            $("#order-card-" + orderId).remove();
          }

          if (quantity > 0) {
            $(".minus-btn").prop("disabled", false);
          }

          console.log("Orders:", data.orders);

          // Update cart summary
          data.orders.forEach(function (order) {
            var $orderSubtotal = $(`#order-subtotal-${order.order_id}`);
            var $orderTotal = $(`#order-total-${order.order_id}`);
            $orderSubtotal.text(`₱${order.subtotal}`);
            $orderTotal.text(`₱${order.subtotal}`);
          });
          // Update cart total
          $("#cart-total").text("₱" + data.total_cart_subtotal);
        } else {
          console.error("Empty products array in the response.");

          Swal.fire({
            icon: "error",
            title: "Error",
            text: "Failed to update cart. Please try again.",
          });
        }
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.error("AJAX Error:", textStatus, errorThrown);

        spinner.removeClass("visible"); // Hide the spinner
        backdrop.removeClass("visible");
      },
    });
  }
  function isCartPage() {
    return window.location.pathname.includes("/cart/");
  }
});
