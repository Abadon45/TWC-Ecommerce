$(document).ready(function () {
    // Delay the execution to ensure the DOM is fully loaded
    $('.cart-link').click(function (event) {
        var cartCount = parseInt($("#upper-cart-count").text());
        if (cartCount === 0) {
            event.preventDefault();
            // Trigger SweetAlert for an empty cart
            Swal.fire({
                title: 'Cart is Empty!',
                icon: 'warning',
                showConfirmButton: true,
                confirmButtonText: 'Okay',
                timer: 2000, // Display alert for 2 seconds
            });
        }
    });
});
