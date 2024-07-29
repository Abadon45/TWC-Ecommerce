


let isOrderBeingCreated = false;
function checkout(element, promo) {
  var bundlePrice = $(element).data("price");
  var bundleQty = $(element).data("quantity");
  var isAuthenticated = $(element).data("auth");
  var source = $(element).data("source");

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

  if (isAuthenticated === "True") {
    if (!isOrderBeingCreated) {
      console.log("User is authenticated, attempting to create order");
      isOrderBeingCreated = true;

      $.ajax({
        url: createOrder,
        type: "POST",
        dataType: "json",
        data: {
          csrfmiddlewaretoken: csrf,
          bundle_price: bundlePrice,
          bundle_qty: bundleQty,
        },
        beforeSend: function () {
          console.log("Before send: Showing loading message");
          sweetAlertShowLoading("We are processing your order...");
        },
        success: function (data) {
          console.log("Success: Order placed successfully");
          console.log("Response data:", data);

          sweetAlertShowSuccess("Order Successfully Placed!");
          setTimeout(function () {
            console.log("Success: Redirecting to Thank You Page...");
            sweetAlertShowLoading("Redirecting to Thank You Page...");
            addBundle(promo, source);
            isOrderBeingCreated = false;
          }, 2000);
        },
        error: function (xhr, status, error) {
          console.error("Error occurred:", error);
          console.log("Error details:", xhr, status);
          isOrderBeingCreated = false; 
        },
      });
    } else {
      console.log("Order is already being created. Please wait.");
    }
  } else {
    Swal.fire({
      title: "Encode Your Shipping Details",
      showCancelButton: true,
      confirmButtonColor: "#2a5298",
      cancelButtonColor: "#d92550",
      confirmButtonText: "Place Order",
      customClass: "swal-wide",
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
        '<label for="id_first_name" class="form-label">Receiver First Name *</label>' +
        '<input id="id_first_name" name="first_name" class="form-control mb-2" type="text" autocomplete="off" style="height: 50px" placeholder="Juan" required>' +
        "</div>" +
        '<div class="col-md-6">' +
        '<label for="id_last_name" class="form-label">Receiver Last Name *</label>' +
        '<input id="id_last_name" name="last_name" class="form-control mb-2" type="text" autocomplete="off" style="height: 50px" placeholder="Dela Cruz" required>' +
        "</div>" +
        '<div class="col-md-6">' +
        '<label for="id_email" class="form-label">Receiver Email *</label>' +
        '<input id="id_email" name="email" class="form-control mb-2" type="text" autocomplete="off" style="height: 50px" placeholder="twconline@store.com" required>' +
        "</div>" +
        '<div class="col-md-6">' +
        '<label for="id_mobile" class="form-label">Receiver Mobile *</label>' +
        '<input id="id_mobile" name="mobile" class="form-control mb-2" type="text" autocomplete="off" style="height: 50px" placeholder="+63 999 678 1234" required>' +
        "</div>" +
        '<div class="col-md-12">' +
        '<label for="id_address" class="form-label">Address *</label>' +
        '<input id="id_address" name="address" class="form-control mb-2" type="text" autocomplete="off" style="height: 50px" placeholder="House Number, Subdivision (Landmark)" required>' +
        "</div>" +
        '<div class="col-md-6">' +
        '<label for="id_barangay" class="form-label">Barangay / Street *</label>' +
        '<input id="id_barangay" name="barangay" class="form-control mb-2" type="text" autocomplete="off" style="height: 50px" placeholder="Barangay Bankal" required>' +
        "</div>" +
        '<div class="col-md-6">' +
        '<label for="id_city" class="form-label">Town / City *</label>' +
        '<input id="id_city" name="city" class="form-control mb-2" type="text" autocomplete="off" style="height: 50px" placeholder="Davao City" required>' +
        "</div>" +
        '<div class="col-md-6">' +
        '<label for="id_province" class="form-label">State / Province *</label>' +
        '<input id="id_province" name="province" class="form-control mb-2" type="text" autocomplete="off" style="height: 50px" placeholder="Davao del Sur" required>' +
        "</div>" +
        '<div class="col-md-6">' +
        '<label for="id_region" class="form-label">Region *</label>' +
        '<select id="id_region" name="region" class="form-select form-control custom-select mb-2" style="height: 50px" required>' +
        '<option value="">-------</option>' +
        '<option value="NATIONAL CAPITAL REGION (NCR)">NATIONAL CAPITAL REGION (NCR)</option>' +
        '<option value="REGION IV-A (CALABARZON)">REGION IV-A (CALABARZON)</option>' +
        '<option value="REGION I (ILOCOS REGION)">REGION I (ILOCOS REGION)</option>' +
        '<option value="REGION II (CAGAYAN VALLEY)">REGION II (CAGAYAN VALLEY)</option>' +
        '<option value="REGION III (CENTRAL LUZON)">REGION III (CENTRAL LUZON)</option>' +
        '<option value="REGION IV-B (MIMAROPA)">REGION IV-B (MIMAROPA)</option>' +
        '<option value="REGION V (BICOL REGION)">REGION V (BICOL REGION)</option>' +
        '<option value="REGION VI (WESTERN VISAYAS)">REGION VI (WESTERN VISAYAS)</option>' +
        '<option value="REGION VII (CENTRAL VISAYAS)">REGION VII (CENTRAL VISAYAS)</option>' +
        '<option value="REGION VIII (EASTERN VISAYAS)">REGION VIII (EASTERN VISAYAS)</option>' +
        '<option value="REGION IX (ZAMBOANGA PENINSULA)">REGION IX (ZAMBOANGA PENINSULA)</option>' +
        '<option value="REGION X (NORTHERN MINDANAO)">REGION X (NORTHERN MINDANAO)</option>' +
        '<option value="REGION XI (DAVAO REGION)">REGION XI (DAVAO REGION)</option>' +
        '<option value="REGION XII (SOCCSKSARGEN)">REGION XII (SOCCSKSARGEN)</option>' +
        '<option value="CORDILLERA ADMINISTRATIVE REGION (CAR)">CORDILLERA ADMINISTRATIVE REGION (CAR)</option>' +
        '<option value="AUTONOMOUS REGION IN MUSLIM MINDANAO (ARMM)">AUTONOMOUS REGION IN MUSLIM MINDANAO (ARMM)</option>' +
        '<option value="REGION XIII (Caraga)">REGION XIII (Caraga)</option>' +
        "</select>" +
        "</div>" +
        '<div class="col-md-6">' +
        '<label for="id_country" class="form-label">Country *</label>' +
        '<input id="id_country" name="country" class="form-control mb-2" type="text" autocomplete="off" style="height: 50px" value="Philippines" disabled>' +
        "</div>" +
        '<div class="col-md-6">' +
        '<label for="id_postcode" class="form-label">Postal Code / ZIP</label>' +
        '<input id="id_postcode" name="postcode" class="form-control mb-2" type="text" autocomplete="off" style="height: 50px" placeholder="8000">' +
        "</div>" +
        '<div class="col-md-6">' +
        '<label for="id_message" class="form-label text-left" style="margin-top: 20px;">Shipping Notes</label>' +
        '<textarea class="form-control form-control-solid" rows="4" name="message" id="id_message" placeholder="E.g. Deliver only weekdays."></textarea>' +
        "</div>" +
        '<div class="col-md-6">' +
        summary +
        "</div>" +
        "</div>" +
        "",
      preConfirm: () => {
        if (
          $("#id_first_name").val() &&
          $("#id_last_name").val() &&
          $("#id_email").val() &&
          $("#id_mobile").val() &&
          $("#id_address").val() &&
          $("#id_barangay").val() &&
          $("#id_city").val() &&
          $("#id_province").val() &&
          $("#id_region").val() &&
          $("#id_postcode").val()
        ) {
          return new Promise((resolve, reject) => {
            resolve({
              first_name: $("#id_first_name").val(),
              last_name: $("#id_last_name").val(),
              email: $("#id_email").val(),
              mobile: $("#id_mobile").val(),
              address: $("#id_address").val(),
              barangay: $("#id_barangay").val(),
              city: $("#id_city").val(),
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
            },
            beforeSend: function () {
              sweetAlertShowLoading("We are processing your order...");
            },
            success: function (data) {
              sweetAlertShowSuccess("Order Successfully Placed!");
              setTimeout(function () {
                sweetAlertShowLoading("Redirecting to Thank You Page...");
                addBundle(promo);
              }, 2000);
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
}

function addBundle(bundleId, source) {
  console.log("Promo is: ", bundleId);
  console.log("Source is: ", source);
  let bundleDetails = {};
  if (bundleId === "promo1") {
    bundleDetails = {
      products: [
        { id: "26", quantity: 1 },
        { id: "40", quantity: 1 },
      ],
    };
  } else if (bundleId === "promo2") {
    bundleDetails = {
      products: [
        { id: "42", quantity: 1 },
        { id: "40", quantity: 1 },
        { id: "41", quantity: 1 },
      ],
    };
  } else if (bundleId === "promo3") {
    bundleDetails = {
      products: [
        { id: "23", quantity: 1 },
        { id: "40", quantity: 1 },
        { id: "41", quantity: 1 },
      ],
    };
  } else if (bundleId === "promo4") {
    bundleDetails = {
      products: [{ id: "30", quantity: 2 }],
    };
  } else if (bundleId === "promo5") {
    bundleDetails = {
      products: [
        { id: "30", quantity: 3 },
        { id: "40", quantity: 1 },
        { id: "43", quantity: 1 },
      ],
    };
  } else if (bundleId === "promo6") {
    bundleDetails = {
      products: [
        { id: "30", quantity: 4 },
        { id: "40", quantity: 1 },
        { id: "43", quantity: 1 },
        { id: "41", quantity: 1 },
      ],
    };
  } else if (bundleId === "promo7") {
    bundleDetails = {
      products: [{ id: "29", quantity: 2 }],
    };
  } else if (bundleId === "promo8") {
    bundleDetails = {
      products: [
        { id: "29", quantity: 3 },
        { id: "40", quantity: 1 },
        { id: "43", quantity: 1 },
      ],
    };
  } else if (bundleId === "promo9") {
    bundleDetails = {
      products: [
        { id: "29", quantity: 4 },
        { id: "40", quantity: 1 },
        { id: "43", quantity: 1 },
        { id: "41", quantity: 1 },
      ],
    };
  }

  $.ajax({
    url: updateItem,
    type: "GET",
    data: {
      bundleDetails: JSON.stringify(bundleDetails),
    },
    success: function (response) {
      console.log(response);
      if (source === "shop") {
        Swal.fire({
          title: 'Success',
          text: 'Bundle added to cart!',
          icon: 'success',
          confirmButtonText: 'OK'
        });
      } else {
        setTimeout(function () {
          window.location.href = bundleCheckout;
        }, 2000);
      }
    },
    error: function (xhr, status, error) {
      console.error(xhr.responseText);
    },
  });
}
