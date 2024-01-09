$(document).ready(function () {
    $('.sweet-modal').click(function () {
        Swal.fire({
            title: 'Authentication Required',
            text: 'Please log in or register to add items to your cart.',
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
