let isOrderBeingCreated = false;
let bundleDetails = {};

function checkout(element, promo) {
    var bundlePrice = $(element).data("price");
    var bundleQty = $(element).data("quantity");

    let summary;
    let promo1_summary =
        "" +
        '<div class="text-white card-border bg-warning card" style="margin-top: 20px;">' +
        '<div class="card-header text-dark">Order Summary:</div>' +
        '<div class="card-body text-dark">' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Product: Santé Barley | Promo 1</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Quantity: 30 Sachet</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Price: ₱2,199.00</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Freebies: Water Bottle</span>' +
        "</div>" +
        "</div>";

    let promo2_summary =
        "" +
        '<div class="text-white card-border bg-warning card" style="margin-top: 20px;">' +
        '<div class="card-header text-dark">Order Summary:</div>' +
        '<div class="card-body text-dark">' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Product: Santé Barley | Promo 2</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Quantity: 40 Sachets</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Price: ₱2,299.00</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Freebies: Water Bottle and Electric Stirrer</span>' +
        "</div>" +
        "</div>";

    let promo3_summary =
        "" +
        '<div class="text-white card-border bg-warning card" style="margin-top: 20px;">' +
        '<div class="card-header text-dark">Order Summary:</div>' +
        '<div class="card-body text-dark">' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Product: Santé Barley | Promo 3</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Quantity: 66 Scoops (3g per Scoops)</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Price: ₱2,840.00</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Freebie: Water Bottle and Electric Stirrer</span>' +
        "</div>" +
        "</div>";

    let promo4_summary =
        "" +
        '<div class="text-white card-border bg-warning card" style="margin-top: 20px;">' +
        '<div class="card-header text-dark">Order Summary:</div>' +
        '<div class="card-body text-dark">' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Product: Fusion Coffee | Promo 1</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Quantity: 2 Boxes</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Price: ₱799.00</span>' +
        "</div>" +
        "</div>";

    let promo5_summary =
        "" +
        '<div class="text-white card-border bg-warning card" style="margin-top: 20px;">' +
        '<div class="card-header text-dark">Order Summary:</div>' +
        '<div class="card-body text-dark">' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Product: Fusion Coffee | Promo 2</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Quantity: 3 Boxes</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Price: ₱1,249.00</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Freebies: Watch and Water Bottle</span>' +
        "</div>" +
        "</div>";

    let promo6_summary =
        "" +
        '<div class="text-white card-border bg-warning card" style="margin-top: 20px;">' +
        '<div class="card-header text-dark">Order Summary:</div>' +
        '<div class="card-body text-dark">' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Product: Fusion Coffee | Promo 3</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Quantity: 4 Boxes</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Price: ₱1,649.00</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Freebies: Stirrer, Watch and Water Bottle</span>' +
        "</div>" +
        "</div>";

    let promo7_summary =
        "" +
        '<div class="text-white card-border bg-warning card" style="margin-top: 20px;">' +
        '<div class="card-header text-dark">Order Summary:</div>' +
        '<div class="card-body text-dark">' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Product: Boost Coffee | Promo 1</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Quantity: 2 Boxes</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Price: ₱899.00</span>' +
        "</div>" +
        "</div>";

    let promo8_summary =
        "" +
        '<div class="text-white card-border bg-warning card" style="margin-top: 20px;">' +
        '<div class="card-header text-dark">Order Summary:</div>' +
        '<div class="card-body text-dark">' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Product: Boost Coffee | Promo 2</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Quantity: 3 Boxes</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Price: ₱1,349.00</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Freebies: Watch and Water Bottle</span>' +
        "</div>" +
        "</div>";

    let promo9_summary =
        "" +
        '<div class="text-white card-border bg-warning card" style="margin-top: 20px;">' +
        '<div class="card-header text-dark">Order Summary:</div>' +
        '<div class="card-body text-dark">' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Product: Boost Coffee | Promo 3</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Quantity: 4 Boxes</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Price: ₱1,799.00</span>' +
        '<span class="mb-2 d-block" style="font-size: 12pt">Freebie: Stirrer, Watch and Water Bottle</span>' +
        "</div>" +
        "</div>";

    if (promo === "promo1") {
        summary = promo1_summary;
    } else if (promo === "promo2") {
        summary = promo2_summary;
    } else if (promo === "promo3") {
        summary = promo3_summary;
    } else if (promo === "promo4") {
        summary = promo4_summary;
    } else if (promo === "promo5") {
        summary = promo5_summary;
    } else if (promo === "promo6") {
        summary = promo6_summary;
    } else if (promo === "promo7") {
        summary = promo7_summary;
    } else if (promo === "promo8") {
        summary = promo8_summary;
    } else if (promo === "promo9") {
        summary = promo9_summary;
    } else {
        summary = "PROMO ERROR";
    }


    Swal.fire({
        title: "Encode Your Shipping Details",
        showCancelButton: true,
        confirmButtonColor: "#2a5298",
        cancelButtonColor: "#d92550",
        confirmButtonText: "Place Order",
        customClass: "swal-wide",
        didOpen: function () {
            $.getScript(addressJS)
                .done(function (script, textStatus) {
                    console.log("address.js loaded successfully.");
                })
                .fail(function (jqxhr, settings, exception) {
                    console.log("Error loading address.js: ", exception);
                });
        },
        didClose: function () {
            let checkbox;
            let checkboxes = document.getElementsByClassName("form-check-input");
            for (checkbox of checkboxes) {
                checkbox.checked = false;
            }
        },
        html:
            '<div class="row">' +
            '<div class="col-md-6">' +
            '<input id="id_first_name" name="first_name" class="form-control mb-2" type="text" autocomplete="off" style="height: 50px" placeholder="Receiver First Name" required>' +
            "</div>" +
            '<div class="col-md-6">' +
            '<input id="id_last_name" name="last_name" class="form-control mb-2" type="text" autocomplete="off" style="height: 50px" placeholder="Receiver Last Name" required>' +
            "</div>" +
            '<div class="col-md-6">' +
            '<input id="id_email" name="email" class="form-control mb-2" type="text" autocomplete="off" style="height: 50px" placeholder="Receiver Email" required>' +
            "</div>" +

            // Change with phone function
            '<div class="col-md-6">' +
            '<input id="id_mobile" name="mobile" class="form-control mb-2 mobileInput id_mobile" type="text" autocomplete="off" style="height: 50px" placeholder="Receiver Mobile" required>' +
            "</div>" +

            '<div class="col-md-12">' +
            '<input id="id_address" name="address" class="form-control mb-2" type="text" autocomplete="off" style="height: 50px" placeholder="Address (House number and street name)" required>' +
            "</div>" +

            '<div class="col-md-6">' +
            '<div class="input-group">' +
            '<label class="input-group-text" for="regionDropdown">Region</label>' +
            '<select id="id_region" class="form-select regionDropdown" name="region" required>' +
            '<option selected>- Select Region -</option>' +
            '</select>' +
            '</div>' +
            '</div>' +

            '<div class="col-md-6">' +
            '<div class="input-group">' +
            '<label class="input-group-text" for="provinceDropdown">Province</label>' +
            '<select id="id_province" class="form-select provinceDropdown" name="province" required>' +
            '<option selected>- Select Province -</option>' +
            '</select>' +
            '</div>' +
            '</div>' +

            '<div class="col-md-6 cityDropdownBox">' +
            '<div class="input-group">' +
            '<label class="input-group-text" for="cityDropdown">City</label>' +
            '<select class="form-select cityDropdown id_city" name="city" required>' +
            '<option selected>- Select City -</option>' +
            '</select>' +
            '</div>' +
            '</div>' +

            '<div class="col-md-6 cityInputBox" style="display: none;">' +
            '<div class="input-group">' +
            '<label class="input-group-text">City</label>' +
            '<input type="text" class="form-control id_city" placeholder="Specify City" name="city_input">' +
            '<div class="input-group-append">' +
            '<button class="btn btn-outline-secondary back-to-dropdown city-dropdown" tooltip="tooltip" title="Back to dropdown select" type="button"><i class="fa-regular fa-circle-xmark"></i></button>' +
            '</div>' +
            '</div>' +
            '</div>' +

            '<div class="col-md-6 barangayDropdownBox">' +
            '<div class="input-group mb-3">' +
            '<label class="input-group-text" for="barangayDropdown">Barangay</label>' +
            '<select class="form-select barangayDropdown id_barangay" name="barangay" required>' +
            '<option selected>- Barangay -</option>' +
            '</select>' +
            '</div>' +
            '</div>' +

            '<div class="col-md-6 barangayInputBox" style="display: none;">' +
            '<div class="input-group mb-3">' +
            '<label class="input-group-text">Barangay</label>' +
            '<input type="text" class="form-control id_barangay" placeholder="Specify Barangay" name="barangay_input">' +
            '<div class="input-group-append">' +
            '<button class="btn btn-outline-secondary back-to-dropdown barangay-dropdown" tooltip="tooltip" title="Back to dropdown select" type="button"><i class="fa-regular fa-circle-xmark"></i></button>' +
            '</div>' +
            '</div>' +
            '</div>' +

            '<div class="col-md-6 postalInputBox">' +
            '<input id="id_postcode" name="postcode" class="form-control mb-2 inputPostcode" type="text" autocomplete="off" style="height: 50px" placeholder="Manually input ZIP CODE">' +
            "</div>" +

            '<div class="col-12">' +
            '<textarea class="form-control form-control-solid" rows="4" name="message" id="id_message" placeholder="Shipping Notes (E.g. Deliver only weekdays.)"></textarea>' +
            "</div>" +
            '<div class="col-md-12">' +
            summary +
            "</div>" +
            "</div>" +
            "",
        preConfirm: () => {
            if (
                $("#id_first_name").val() &&
                $("#id_last_name").val() &&
                $("#id_email").val() &&
                $(".id_mobile").val() &&
                $("#id_address").val() &&
                $(".id_barangay").val() &&
                $(".id_city").val() &&
                $("#id_province").val() &&
                $("#id_region").val() &&
                $("#id_postcode").val()
            ) {
                return new Promise((resolve, reject) => {
                    resolve({
                        first_name: $("#id_first_name").val(),
                        last_name: $("#id_last_name").val(),
                        email: $("#id_email").val(),
                        mobile: $(".id_mobile").val(),
                        address: $("#id_address").val(),
                        barangay: $(".id_barangay").val(),
                        city: $(".id_city").val(),
                        province: $("#id_province").val(),
                        region: $("#id_region").val(),
                        postcode: $("#id_postcode").val(),
                        message: $("#id_message").val() || "",
                    });
                });
            } else {
                Swal.showValidationMessage(
                    "Please provide all required information. Thank you!"
                );
                return false;
            }
        },
    }).then((data) => {
        if (data.isConfirmed) {
            addBundle(promo)
            console.log('Bundle: ' + bundleDetails)
            console.log("Data Value: ", data.value);
            if (data.value) {
                $.ajax({
                    url: createOrder,
                    type: "POST",
                    dataType: "json",
                    data: {
                        csrfmiddlewaretoken: csrf,
                        first_name: data.value.first_name,
                        last_name: data.value.last_name,
                        email: data.value.email,
                        phone: data.value.mobile,
                        line1: data.value.address,
                        barangay: data.value.barangay,
                        city: data.value.city,
                        province: data.value.province,
                        region: data.value.region,
                        postcode: data.value.postcode,
                        message: data.value.message,
                        bundle_price: bundlePrice,
                        bundle_qty: bundleQty,
                        bundleDetails: JSON.stringify(bundleDetails),
                    },
                    beforeSend: function () {
                        sweetAlertShowLoading("We are processing your order...");
                    },
                    success: function (data) {
                        if (data.success) {
                            sweetAlertShowSuccess("Order Successfully Placed!");
                            setTimeout(function () {
                                sweetAlertShowLoading("Redirecting to Thank You Page...");
                                window.location.href = data.redirect_url;
                            }, 2000);
                        } else {
                            // Handle error if success is false
                            sweetAlertShowError("Error: " + data.error);
                        }
                    },
                });
            } else {
                Swal.fire({
                    title: "Please provide all required information. Thank you!",
                    icon: "error",
                    didClose: function () {
                        checkout(promo);
                    },
                });
            }
        }
    });
}

function addBundle(bundleId) {
    console.log("Promo is: ", bundleId);
    if (bundleId === "promo1") {
        bundleDetails = {
            products: [
                {slug: "26", quantity: 1},
                {slug: "40", quantity: 1},
            ],
        };
    } else if (bundleId === "promo2") {
        bundleDetails = {
            products: [
                {slug: "42", quantity: 1},
                {slug: "40", quantity: 1},
                {slug: "41", quantity: 1},
            ],
        };
    } else if (bundleId === "promo3") {
        bundleDetails = {
            products: [
                {slug: "23", quantity: 1},
                {slug: "40", quantity: 1},
                {slug: "41", quantity: 1},
            ],
        };
    } else if (bundleId === "promo4") {
        bundleDetails = {
            products: [{id: "30", quantity: 2}],
        };
    } else if (bundleId === "promo5") {
        bundleDetails = {
            products: [
                {slug: "30", quantity: 3},
                {slug: "40", quantity: 1},
                {slug: "43", quantity: 1},
            ],
        };
    } else if (bundleId === "promo6") {
        bundleDetails = {
            products: [
                {slug: "30", quantity: 4},
                {slug: "40", quantity: 1},
                {slug: "43", quantity: 1},
                {slug: "41", quantity: 1},
            ],
        };
    } else if (bundleId === "promo7") {
        bundleDetails = {
            products: [{slug: "boost-coffee", quantity: 1}],
        };
    } else if (bundleId === "promo8") {
        bundleDetails = {
            products: [
                {slug: "boost-coffee", quantity: 2},
                {slug: "water-bottle", quantity: 1},
            ],
        };
    } else if (bundleId === "promo9") {
        bundleDetails = {
            products: [
                {slug: "boost-coffee", quantity: 4},
                {slug: "water-bottle", quantity: 1},
                {slug: "water-stirrer", quantity: 1},
            ],
        };
    }
    console.log('bundleDetails inside addBundle: ', bundleDetails);
}
