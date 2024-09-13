$(document).ready(function () {
  var productForm = $("#addProduct");
  var shippingForm = $("#addShipping");

  productForm.submit(function (e) {
    e.preventDefault();
    var thisForm = $(this);
    var actionEndpoint = thisForm.attr("action");
    var httpMethod = thisForm.attr("method");
    var formData = new FormData(thisForm[0]);

    console.log("Submitting form via AJAX");
    console.log("Action Endpoint:", actionEndpoint);
    console.log("HTTP Method:", httpMethod);
    console.log("Form Data:", formData);

    $.ajax({
      url: actionEndpoint,
      method: httpMethod,
      data: formData,
      cache: false,
      contentType: false,
      processData: false,
      success: function (response) {
        window.location.href = window.location.href + "../";
      },
      error: function (errorData) {
        console.log(errorData);
      },
    });
  });

  shippingForm.submit(function (e) {
    e.preventDefault();
    var thisForm = $(this);

    var actionEndpoint = thisForm.attr("action");
    var httpMethod = thisForm.attr("method");
    var formData = thisForm.serializeArray();

    // Prepare user data and add it to the form data
    var userData = prepareUserData();
    formData.push({ name: "username", value: userData.username });
    formData.push({ name: "email", value: userData.email });

    // spinner.addClass("visible");
    // backdrop.addClass("visible");

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
      url: actionEndpoint,
      method: httpMethod,
      data: formData,
      success: function (successData) {
        console.log("Success Data: ", successData);
        $("#step2-tab").click();
        $("#step1").removeClass("active show");
        $("#step1-tab").removeClass("nav-link active done");
        $("#step1-tab").addClass("nav-link done");
        $("#step2").addClass("active show");
        $("#step2-tab").addClass("active done");

        $(".checkout-btn").removeAttr("hidden");
        $(".dummy-submit").addClass("hide");

        successData.updated_orders.forEach(function (order) {
          var shippingFeeFormatted =
            "₱" + parseFloat(order.shipping_fee).toFixed(2);
          var shippingFeeElement = $("#shipping_fee_" + order.shop + " span");
          var orderTotalFormatted =
            "₱" +
            parseFloat(order.total_amount)
              .toFixed(2)
              .replace(/\B(?=(\d{3})+(?!\d))/g, ",");
          var orderTotalUpdate = $("#order-total-" + order.shop);

          shippingFeeElement.text("Calculating...");

          // Update shipping fee and total amount after a delay
          setTimeout(() => {
            shippingFeeElement.text(shippingFeeFormatted);
            orderTotalUpdate.text(orderTotalFormatted);

            var totalPayment =
              "₱" + parseFloat(successData.total_payment).toFixed(2);
            var totalPaymentFormatted = totalPayment.replace(
              /\B(?=(\d{3})+(?!\d))/g,
              ","
            );
            $("#total-payment").text(totalPaymentFormatted);

            Swal.close();
          }, 2000);
        });
      },
      error: function (errorData) {
        console.log(errorData);
        Swal.fire({
          icon: "error",
          title: "Oops...",
          text: "Something went wrong! Please try again later.",
        });
      },
    });
  });

  // Initialize an object to store input details
  var userDetails = {
    first_name: "",
    last_name: "",
    email: "",
  };

  // Variables to store generated username and email
  var userName = "";
  var userEmail = "";

  // Function to update userDetails object
  function prepareUserData() {
    userDetails.first_name = $(".inputFirstName").val().charAt(0);
    userDetails.last_name = $(".inputLastName").val();
    userDetails.email = $(".inputEmail").val();

    userName =
      userDetails.first_name + userDetails.last_name + generateRandomString(3);
    userEmail = userDetails.email;

    console.log("User Details:", userDetails);
    console.log("userName:", userName);
    console.log("userEmail:", userEmail);

    return {
      username: userName,
      email: userEmail,
    };
  }

  // $("#addUserData").click(function(e) {
  //     e.preventDefault();

  //   });

  // Function to generate a random string
  function generateRandomString(length) {
    var result = "";
    var characters =
      "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    var charactersLength = characters.length;
    for (var i = 0; i < length; i++) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
  }
});
