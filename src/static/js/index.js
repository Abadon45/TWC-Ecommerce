$(document).ready(function() {
    // Check if the alert has already been shown in this session
    if (!sessionStorage.getItem('alertShown')) {
        $.get('/', function(data) {
            if (data.has_existing_order) {
                Swal.fire({
                    title: 'Hello!',
                    text: `Hi! is your Email ${data.email}?`,
                    icon: 'info',
                    showCancelButton: true,
                    cancelAnimationFrame: true,
                    cancelButtonText: 'No',
                    confirmButtonText: 'Login',
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.location.href = '/login/';
                    }
                });

                // Set the alertShown session variable to true
                sessionStorage.setItem('alertShown', 'true');
            }
        });
    }
});