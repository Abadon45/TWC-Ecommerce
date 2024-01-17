$(document).ready(function () {
    // Delay the execution to ensure the DOM is fully loaded
    $('#cart-link').click(function (event) {
        var cartCount = parseInt($("#cart-count").text());
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
    $('.sweet-modal').click(function () {
        Swal.fire({
            title: 'Authentication Required',
            text: 'Please log in or register to proceed to checkout.',
            icon: 'info',
            showCancelButton: true,
            confirmButtonText: 'Log In',
            cancelButtonText: 'Cancel'
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = '/login/';
            }
        });
    });
});
