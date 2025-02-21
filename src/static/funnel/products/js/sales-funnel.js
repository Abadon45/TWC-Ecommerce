let bundleDetails = {};
let bundlePromo = "";

function checkout(element, promo) {
    var bundlePrice = $(element).data("price");
    var bundleQty = $(element).data("quantity");

    console.log("Promo: " + promo);

    // Add the bundle and log bundleDetails
    addBundle(promo);
    console.log('Bundle Details: ', bundleDetails);

    // Validate that we have enough information to proceed
    if (bundleDetails.products && bundleDetails.products.length > 0) {
        $.ajax({
            url: createOrder,
            type: "GET",
            dataType: "json",
            data: {
                bundle_price: bundlePrice,
                bundle_qty: bundleQty,
                bundleDetails: JSON.stringify(bundleDetails),
                promo: bundlePromo,
            },
            success: function (data) {
                if (data.success) {
                    Swal.fire({
                        title: "Please wait...",
                        text: "We are creating your order.",
                        showConfirmButton: false,
                        allowOutsideClick: false,
                        didOpen: () => {
                            Swal.showLoading();
                            window.location.href = data.redirect_url;
                        },
                        timer: 3000,
                    });
                } else {
                    sweetAlertShowError("Error: " + (data.error || "An unknown error occurred"));
                }
            },
            error: function (xhr, status, error) {
                sweetAlertShowError("Error: " + error);
            }
        });
    } else {
        Swal.fire({
            title: "Please provide all required information. Thank you!",
            icon: "error",
            didClose: function () {
                checkout(element, promo); // Fix for passing 'element' as well in retry
            },
        });
    }
}

function addBundle(bundleId) {
    console.log("Promo is: ", bundleId);
    if (bundleId === "promo1" || bundleId === "promo4" || bundleId === "promo7") {
        bundlePromo = "Promo 1"
    } else if (bundleId === "promo2" || bundleId === "promo5" || bundleId === "promo8") {
        bundlePromo = "Promo 2"
    } else if (bundleId === "promo3" || bundleId === "promo6" || bundleId === "promo9") {
        bundlePromo = "Promo 3"
    }
    if (bundleId === "promo1") {
        bundleDetails = {
            products: [
                {slug: "sante-barley-powder-10s", quantity: 1},
            ],
        };
    } else if (bundleId === "promo2") {
        bundleDetails = {
            products: [
                {slug: "sante-barley-powder-10s", quantity: 2},
                {slug: "water-bottle", quantity: 1},
            ],
        };
    } else if (bundleId === "promo3") {
        bundleDetails = {
            products: [
                {slug: "31-sante-barley-powder-10s", quantity: 1},
                {slug: "water-bottle", quantity: 1},
                {slug: "water-stirrer", quantity: 1},
            ],
        };
    } else if (bundleId === "promo4") {
        bundleDetails = {
            products: [{slug: "fusion-coffee", quantity: 1}],
        };
    } else if (bundleId === "promo5") {
        bundleDetails = {
            products: [
                {slug: "fusion-coffee", quantity: 2},
                {slug: "water-bottle", quantity: 1},
            ],
        };
    } else if (bundleId === "promo6") {
        bundleDetails = {
            products: [
                {slug: "31-fusion-coffee", quantity: 1},
                {slug: "water-bottle", quantity: 1},
                {slug: "water-stirrer", quantity: 1},
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
                {slug: "31-boost-coffee", quantity: 1},
                {slug: "water-bottle", quantity: 1},
                {slug: "water-stirrer", quantity: 1},
            ],
        };
    }
    console.log('bundleDetails inside addBundle: ', bundleDetails);
}


