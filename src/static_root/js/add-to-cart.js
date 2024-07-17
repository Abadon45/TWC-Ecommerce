$(document).ready(function () {

  $(document).on("click", ".update-cart", function (event) {
    event.preventDefault();
    var button = $(this);
    var productId = button.data("product");
    var orderId = button.data("order-id");
    var action = button.data("action");
    var quantityInput = $("#quantity-input-" + productId);
    var quantity = parseInt(quantityInput.val()) || 1;
    

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
            updateUserOrder(productId, orderId, action, quantity, updateItemUrl, button);
            Swal.close();
          }, 1000);
        }
      });
    } else {
      updateUserOrder(productId, orderId, action, quantity, updateItemUrl, button);
    }
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
        var formattedCartItems = String(data.cart_items).padStart(2, "0");
        var subtotal = data.products[0].total;
        var subtotalNumber = parseFloat(subtotal);
        var orderTotal = parseFloat(data.total_cart_subtotal).toLocaleString(
          "en-US",
          {
            minimumFractionDigits: 2,
          }
        );
        var formattedSubtotal = subtotalNumber.toLocaleString("en-US", {
          minimumFractionDigits: 2,
        });
        var totalOrders = data.orders.length;

        //Update Cart Count
        $("#upper-cart-count").text(data.cart_items);
        $("#lower-cart-count").text(data.cart_items);
        

        //Add to cart create dropdown
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
          } else if (data.cart_items > 1 || data.action === "minus") {
            var existingProduct = $("#cart-row-" + data.products[0].id);
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
              $(".total-amount").text("₱" + orderTotal);
              $("#cart-total").text("₱" + orderTotal);
              
            });
          }
        }

        //Disable add to cart button after product is added
        $(".item-id-" + productId)
          .text("ADDED TO CART")
          .removeClass("theme-btn")
          .addClass("btn-secondary")
          .prop("disabled", true)
          // .css("padding", "9px 20px");

        //Remove order table if order items is 0
        if (data.orders.length === 0){
          $('#order-card-' + orderId).remove();
        }

        //Product quantity function
        if (data.products.length > 0) {
          if (data.action !== "remove") {
            $("#product-subtotal-" + productId).text("₱" + formattedSubtotal);
            $(".total-amount").text("₱" + orderTotal);
          }

          if (data.action === "remove") {
            console.log("Removing product with ID:", productId);
            $("#product-row-" + productId).remove();
            $("#cart-row-" + productId).remove();
            $(".total-amount").text("₱" + orderTotal);
            $(".item-id-" + productId)
              .text("Added To Cart")
              .addClass("theme-btn update-cart")
              .removeClass("btn-secondary")
              .prop("disabled", false)
              .attr("data-product", productId)
              .attr("data-action", "add");
          }
          

          //If the cart becomes empty
          if (data.cart_items === 0) {
            $(".dropdown-cart-menu").remove();
          }

          //disable the minus button if quantity is 0
          if (quantity === 0) {
            $(".minus-btn").prop("disabled", false);
          }

          // Update cart summary
          data.orders.forEach(function (order) {
            var $orderSubtotal = $(`#order-subtotal-${order.order_id}`);
            var $orderTotal = $(`#order-total-${order.order_id}`);
            var subtotalNumber = parseFloat(order.subtotal);
            var formattedSubtotal = subtotalNumber.toLocaleString("en-US", {
              minimumFractionDigits: 2,
            });
            var formattedTotal = subtotalNumber.toLocaleString("en-US", {
              minimumFractionDigits: 2,
            });
            $orderSubtotal.text(`₱${formattedSubtotal}`);
            $orderTotal.text(`₱${formattedTotal}`);
          });
        } else {
          console.error("Empty products array in the response.");
          Swal.fire({
            icon: "error",
            title: "Error",
            text: "Failed to update cart. Please try again.",
          });
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

        spinner.removeClass("visible"); // Hide the spinner
        backdrop.removeClass("visible");
      },
    });
  }
  function isCartPage() {
    return window.location.pathname.includes("/cart/");
  }
});
