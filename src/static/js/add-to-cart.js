$(document).ready(function () {
    $('.update-cart').click(function () {
        var productId = $(this).data('product');
        var action = $(this).data('action');
        var quantityInput = $('#quantity-input-' + productId);
        var quantity = parseInt(quantityInput.val()) || 1;

        console.log('Product ID:', productId, 'Action:', action, 'Quantity:', quantity);

        updateUserOrder(productId, action, quantity, updateItemUrl);
    });

    function updateUserOrder(productId, action, quantity, url) {
        console.log('User is logged in, sending data...');

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

                if (!isCartPage()) {

                    Swal.fire({
                        icon: 'success',
                        title: 'Success',
                        text: 'Cart updated successfully!',
                        timer: 2000,
                        showConfirmButton: false
                    });
                }
                $('#cart-count').text(data.cart_items);

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
        });
    }
    function isCartPage() {
        return window.location.pathname.includes('/cart/');
    }
});