$(document).ready(function() {
    $(".checkoutBtn").hide();

    $(".paymentBtn").on("click", function (e) {
        e.preventDefault();
        $("#step2-tab").click();
        $("#step1").removeClass("active show");
        $("#step1-tab").removeClass("nav-link active done");
        $("#step1-tab").addClass("nav-link done");
        $("#step2").addClass("active show");
        $("#step2-tab").addClass("active done");
    });

    $(".confirmPaymentBtn").on("change", function () { 
        // Add blur class to SweetAlert backdrop
        showLoading();

        if ($(this).prop("checked")) {
            $(".checkoutBtn").show();
        } else {
            $(".checkoutBtn").hide();
        }
    });

    function showLoading() {
        Swal.fire({
            title: 'Loading...',
            allowOutsideClick: false,
            showConfirmButton: false,
            onBeforeOpen: () => {
                Swal.showLoading()
            },
        });

        // Set a 2-second timeout to hide SweetAlert
        setTimeout(function() {
            hideLoading();
        }, 1000);
    }

    function hideLoading() {
        Swal.close();
    }
});
