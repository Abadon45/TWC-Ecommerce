$(document).ready(function() {
    $('#chat-seller').on('click', function(event) {
        event.preventDefault();
        const chatLink = $(this).attr('href');

        if (!chatLink || chatLink === 'none') {
            Swal.fire({
                title: 'Seller currently unavailable',
                icon: 'error',
                confirmButtonText: 'OK'
            });
        } else {
            Swal.fire({
                title: 'Redirecting you to messenger',
                html: 'Please wait...',
                timer: 2000,
                timerProgressBar: true,
                didOpen: () => {
                    Swal.showLoading();
                },
                willClose: () => {
                    window.open(chatLink, '_blank');
                }
            });
        }
    });
});