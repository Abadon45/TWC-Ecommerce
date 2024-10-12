$(document).ready(function () {
    var shippingForm = $("#addShipping");

    shippingForm.submit(function (e) {
        e.preventDefault();
        var thisForm = $(this);
        var actionEndpoint = thisForm.attr("action");
        var formData = thisForm.serialize();

        // Prepare user data and add it to the form data
        var userData = prepareUserData();
        formData += "&username=" + encodeURIComponent(userData.username);
        formData += "&email=" + encodeURIComponent(userData.email);

        console.log(formData);

        // Show SweetAlert with loading message
        Swal.fire({
            title: "Processing...",
            html: "Calculating orders and shipping fees. Please wait.",
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            },
        });

        $.ajax({
            url: actionEndpoint + "?" + formData,
            method: "GET",
            dataType: 'json',  // Expecting JSON
            headers: {
                'X-Requested-With': 'XMLHttpRequest'  // Add this header
            },
            success: function (successData) {
                console.log("Success Data: ", successData);

                // UI update logic
                $("#step2-tab").click();
                $("#step1").removeClass("active show");
                $("#step1-tab").removeClass("nav-link active done").addClass("nav-link done");
                $("#step2").addClass("active show");
                $("#step2-tab").addClass("active done");
                $(".checkout-btn").removeAttr("hidden");
                $(".dummy-submit").addClass("hide");

                // Update shipping fees and totals
                successData.updated_orders.forEach(function (order) {
                    var shippingFeeFormatted = "₱" + parseFloat(order.shipping_fee).toFixed(2);
                    var shippingFeeElement = $("#shipping_fee_" + order.shop + " span");
                    var orderTotalFormatted = "₱" + parseFloat(order.total_amount).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                    var orderTotalUpdate = $("#order-total-" + order.shop);

                    shippingFeeElement.text("Calculating...");

                    // Update shipping fee and total amount after a delay
                    setTimeout(() => {
                        shippingFeeElement.text(shippingFeeFormatted);
                        orderTotalUpdate.text(orderTotalFormatted);

                        var totalPaymentFormatted = "₱" + parseFloat(successData.total_payment).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                        $("#total-payment").text(totalPaymentFormatted);

                        Swal.close();
                    }, 2000);
                });
            },
            error: function (errorData) {
                console.log(errorData);
                var errorMessage = "Something went wrong! Please try again later.";

                if (errorData.responseJSON && errorData.responseJSON.errors) {
                    console.log("Error Message:", errorData.responseJSON.errors);
                    errorMessage = errorData.responseJSON.errors.join(", "); // Assuming errors is an array
                }

                Swal.fire({
                    icon: "error",
                    title: "Oops...",
                    text: errorMessage,
                });
            },
        });
    });

    // Function to prepare user data
    function prepareUserData() {
        var userDetails = {
            first_name: $(".inputFirstName").val().charAt(0),
            last_name: $(".inputLastName").val(),
            email: $(".inputEmail").val(),
        };

        var userName = userDetails.first_name + userDetails.last_name + generateRandomString(3);
        console.log("User Details:", userDetails);

        return {
            username: userName,
            email: userDetails.email,
        };
    }

    // Function to generate a random string
    function generateRandomString(length) {
        var result = "";
        var characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
        var charactersLength = characters.length;
        for (var i = 0; i < length; i++) {
            result += characters.charAt(Math.floor(Math.random() * charactersLength));
        }
        return result;
    }
});
