function updateDiscount(button) {
    var updateUrl = button.getAttribute('data-update-url');
    var maxProfit = parseFloat(button.getAttribute('data-max-profit'));

    console.log("Update URL:", updateUrl);
    console.log("Max Profit:", maxProfit);

    Swal.fire({
        icon: 'question',
        title: 'Do you want to add discount to your cart?',
        html: '<div class="input-group mt-3">' +
            '<span class="input-group-text" id="basic-addon1" style="width: 3rem!important;">₱</span>' +
            '<input id="id_discount_amount" type="number" class="form-control" placeholder="Discount Amount" aria-label="Discount Amount" aria-describedby="basic-addon1" min="0" max="' + maxProfit + '">' +
            '</div>' +
            '<span style="font-size: 10pt">Max Discount you can give is ' + maxProfit.toLocaleString('en-US', { style: 'currency', currency: 'PHP' }) + '.</span>',
        showCancelButton: true,
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        showLoaderOnConfirm: true,
        preConfirm: () => {
            var discount = $('#id_discount_amount').val();
            var order_id = button.getAttribute('data-order-id');

            if (parseFloat(discount) > parseFloat(maxProfit)) {
                Swal.showValidationMessage('Discount cannot exceed maximum profit');
                return false;
            }

            return $.ajax({
                type: 'POST',
                url: updateUrl,
                dataType: 'json',
                headers: { "X-CSRFToken": csrf },
                data: {
                    discount: discount,
                    order_id: order_id,
                },
            });
        }
    }).then((result) => {
        if (result.value.success) {
            var formattedDiscount = '₱' + parseFloat(result.value.discount_amount).toFixed(2);
            $('#discount-amount').text(formattedDiscount);
            
            var orderTotal = parseFloat(button.getAttribute('data-order-total'));
            var sellerTotal = parseFloat(button.getAttribute('data-seller-total'));
            var shippingFee = parseFloat(button.getAttribute('data-shipping-fee'));
            var discountAmount = parseFloat(result.value.discount_amount);

            var newCODAmount = orderTotal - discountAmount;
            var newSellerProfit = newCODAmount - sellerTotal - shippingFee
            console.log('New COD Amount:', newCODAmount);
                
            var formattedCODAmount = '₱' + newCODAmount.toFixed(2);
            var formattedNewSellerProfit = '₱' + newSellerProfit.toFixed(2);
            $('#review-cod-amount').text(formattedCODAmount);
            $('#review-seller-cod-amount').text(formattedCODAmount);
            $('#review-seller-profit').text(formattedNewSellerProfit);
            
            Swal.fire('Success', 'Discount updated successfully!', 'success');
        } else {
            Swal.fire('Error', 'Failed to update discount!', 'error');
        }
    });

    $('.discount-currency').css('width', '2rem');
}

// Function to handle confirmation of order
function confirmOrderBtn(button) {
    var orderId = button.getAttribute('data-order-id');
    Swal.fire({
        icon: 'question',
        title: 'Place Order Now!',
        html: 'Do you confirm that all the details are correct?',
        showCancelButton: true,
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel'
    }).then((result) => {
        if (result.isConfirmed) {
            // Show modal to select payment method
            Swal.fire({
                icon: 'warning',
                title: 'Select Your Payment Method',
                html: '<select id="id_payment_method" class="form-select form-control mt-3" required>' +
                        '<option value="select" selected>- Select Payment -</option>' +
                        '<option value="cod">Cash On Delivery</option>' +
                        '<option value="prepaid" disabled>Prepaid</option>' +
                        '</select>',
                showCancelButton: true,
                confirmButtonText: 'Confirm',
                cancelButtonText: 'Cancel',
                preConfirm: () => {
                    var paymentMethod = $('#id_payment_method').val();
                    if (paymentMethod === 'select') {
                        Swal.showValidationMessage('You must select a payment option');
                        return false;
                    }
                }
            }).then((paymentResult) => {
                if (paymentResult.isConfirmed) {
                    var paymentMethod = $('#id_payment_method').val();
                    // Send AJAX request to confirm order with payment method
                    $.ajax({
                        type: 'POST',
                        url: confirmOrder, 
                        headers: { "X-CSRFToken": csrf },
                        data: { 'order_id': orderId, 'payment_method': paymentMethod },
                        success: function(response) {
                            console.log("Order reviewed and confirmed!");
                            Swal.fire({
                                icon: 'success',
                                title: 'Order Confirmed',
                                text: 'Redirecting to dashboard...',
                                timer: 2000,
                                timerProgressBar: true,
                                didOpen: () => {
                                    Swal.showLoading();
                                },
                                willClose: () => {
                                    window.location.href = sellerPendingOrderUrl;
                                }
                            });
                        }, 
                        error: function(xhr, textStatus, errorThrown) {
                            console.error('Error:', errorThrown);
                            // Handle error
                        }
                    });
                }
            });
        }
    });
}
