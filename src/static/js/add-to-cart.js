$(document).ready(function () {
    // for product detail page
    
    $(document).on('click', '.update-cart', function (event) {
        event.preventDefault();
        var button = $(this);
        var productId = button.data('product');
        var action = button.data('action');
        var quantityInput = $('#quantity-input-' + productId);
        var quantity = parseInt(quantityInput.val()) || 1;

        console.log('Product ID:', productId, 'Action:', action, 'Quantity:', quantity);
        
        if (!isCartPage()) {

            Swal.fire({
                icon: 'success',
                title: 'Success',
                text: 'Cart updated successfully!',
                timer: 2000,
                showConfirmButton: false
            });
        }

        updateUserOrder(productId, action, quantity, updateItemUrl, button);
    });

    function updateUserOrder(productId, action, quantity, url, button) {
        
        $.ajax({
            url: url,
            method: 'GET',
            dataType: 'json',
            data: {
                productId: productId,
                action: action,
                quantity: quantity
            },
            success: function (data) {
                console.log(data);

                $('#cart-count').text(data.cart_items);

                if (button && button.length > 0) {
                    // Disable the button
                    button.prop('disabled', true);
                    // Change button class
                    button.removeClass('theme-btn add-to-cart-btn').addClass('btn btn-dark');
                    // Change button text
                    if (button.text() === 'Add To Cart') {
                        button.text('Added To Cart');
                    }
                }

                if (data.products.length > 0) {
                    if (data.action !== 'remove') {
                        $('#product-subtotal-' + productId).text(data.products[0].total);
                    }

                    if (data.action === 'remove') {
                        $('#product-row-' + productId).remove();
                    }

                } else {
                    console.error('Empty products array in the response.');

                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Failed to update cart. Please try again.',
                    });
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.error('AJAX Error:', textStatus, errorThrown);
            }
        });
    }
    function isCartPage() {
        return window.location.pathname.includes('/cart/');
    }

});