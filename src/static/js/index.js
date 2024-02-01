$(document).ready(function() {
    console.log("Document is ready");

    // Check if the alert has already been shown in this session
    if (!sessionStorage.getItem('alertShown')) {
        console.log("Alert has not been shown in this session");
        
        $.get(window.location.origin, function(data) {
            console.log("Received data from server:", data);
            if (data.has_existing_order) {
                console.log("User has existing order");
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
                console.log("Setting alertShown to true in sessionStorage");
                // Set the alertShown session variable to true
                sessionStorage.setItem('alertShown', 'true');
            }
        });
    }
});