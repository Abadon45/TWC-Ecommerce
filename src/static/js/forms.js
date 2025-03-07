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
                $("#step1-tab .step-count").text('\u2713');
                $("#step2").addClass("active show");
                $("#step2-tab").addClass("active done");
                $(".checkout-btn").removeAttr("hidden");
                $(".dummy-submit").addClass("hide");
                $(".shipping-details h1, .shipping-details p, .shipping-details span").css("color", "#56a27b");
                $(".payment-method h1, .payment-method p, .payment-method span").css("color", "#ffffff");

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
                    }, 500);
                });
            },
            error: function (errorData) {
                console.log(errorData);
                var errorMessage = "Something went wrong! Please try again later. " + errorData;

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
        var fullName = $(".inputFullName").val().trim();

        if (!fullName) {
            return {username: generateRandomString(6)}; // Fallback if no name is entered
        }

        var userDetails = splitFullName(fullName);
        var firstInitial = userDetails.first_name ? userDetails.first_name.charAt(0).toLowerCase() : "";
        var lastName = userDetails.last_name ? userDetails.last_name.replace(/\s/g, "").toLowerCase() : "";

        var userName = firstInitial + lastName + generateRandomString(3);
        var email = $('input[name="email"]').val().trim();

        console.log("Generated Username:", userName);

        return {
            username: userName,
            email: email
        };
    }

// Function to split full name into first and last name
    function splitFullName(fullName) {
        var lastNamePrefixes = ["de", "de la", "van", "von", "da", "del", "la", "san", "dela"];
        var parts = fullName.split(/\s+/);

        if (parts.length <= 1) {
            return {first_name: fullName, last_name: ""};
        }

        var firstName = [];
        var lastName = [];

        for (var i = parts.length - 1; i >= 0; i--) {
            var potentialLastName = parts.slice(i).join(" ").toLowerCase();
            if (lastName.length === 0 || lastNamePrefixes.includes(potentialLastName)) {
                lastName.unshift(parts[i]);
            } else {
                firstName = parts.slice(0, i + 1);
                break;
            }
        }

        return {
            first_name: firstName.join(" "),
            last_name: lastName.join(" ")
        };
    }

// Function to generate a random string
    function generateRandomString(length) {
        var result = "";
        var characters = "abcdefghijklmnopqrstuvwxyz0123456789";
        for (var i = 0; i < length; i++) {
            result += characters.charAt(Math.floor(Math.random() * characters.length));
        }
        return result;
    }

});




