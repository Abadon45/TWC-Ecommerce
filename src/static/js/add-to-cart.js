$(document).ready(function () {

    var spinner = $('.sk-circle');
    var backdrop = $('.backdrop');

    $(document).on('click', '.update-cart', function (event) {
        event.preventDefault();
        var button = $(this);
        var productId = button.data('product');
        var action = button.data('action');
        var quantityInput = $('#quantity-input-' + productId);
        var quantity = parseInt(quantityInput.val()) || 1;

        console.log('Product ID:', productId, 'Action:', action, 'Quantity:', quantity);

        spinner.addClass('visible'); // Show the spinner
        backdrop.addClass('visible');

        
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
                console.log(quantity);

                spinner.removeClass('visible'); // Hide the spinner
                backdrop.removeClass('visible');

                $('#cart-count').text(data.cart_items);

                // Check if button exists and doesn't have the exclude class
 
                if (button && button.length > 0 && !button.hasClass('excludeDisable')) {
                    console.log("Before disabling minus button");
                    button.prop('disabled', true);
                    button.removeClass('theme-btn add-to-cart-btn').addClass('btn btn-dark');
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

                    if (data.cart_items === 0){
                        $('#product-row-' + productId).remove();
                    }

                    if (quantity > 0) {
                        $('.minus-btn').prop('disabled', false);
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

                spinner.removeClass('visible'); // Hide the spinner
                backdrop.removeClass('visible');
            }
        });
    }
    function isCartPage() {
        return window.location.pathname.includes('/cart/');
    }

});
