$(document).ready(function () {
  const getAddressDetailsUrl = "/get-address-details/";
  const deleteAddressUrl = "/delete-address/";
  const updateAddressUrl = "/update-address/";


  var spinner = $(".sk-circle");
  var backdrop = $(".backdrop");

  $("#copyButton").click(function () {
    /* Get the text field */
    var copyText = $("#copyInput");

    /* Select the text field */
    copyText.select();

    /* Copy the text inside the text field */
    document.execCommand("copy");

    /* Alert the copied text */
    $(this).text("Copied!!");
  });

  $(".addAddressBtn").click(function () {
    $(".addressList").hide();
    $(".addAddressDiv").removeAttr("hidden");
  });

  $(".addressListBtn").click(function () {
    $(".addressList").show();
    $(".addAddressDiv").attr("hidden", true);
  });

  $("#orderDetailsModal").on("show.bs.modal", function (event) {
    var modal = $(this);
    var button = event.relatedTarget;
    var orderData = $(button).data("order"); // Extract the order data
    var order = JSON.parse(orderData); // Parse the JSON string back to an object

    modal.find(".modal-body .alert").remove();
    modal.find(".modal-content").addClass("loading");

    // Load Spinner
    spinner.addClass("visible");
    backdrop.addClass("visible");

    // Show "Calculating orders" message
    Swal.fire({
        title: "Calculating Orders...",
        html: "Please wait while we calculate your order details.",
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        },
    });

    // Simulate delay for calculation
    setTimeout(() => {
        // Update modal content with the order details
        modal.find(".modal-title").text("Order Details - " + order.order_id);
        modal.find(".invoice").text(order.order_id);
        modal.find("#orderDate").text(order.created_at);
        modal.find("#orderMobile").text(order.contact_number);
        modal.find(".orderQuantity").text(order.total_quantity);
        modal.find(".orderTotal").text("₱" + order.total_amount);

        var orderItemsList = modal.find("#orderItemsList");
        orderItemsList.empty();
        if (order.order_items.length > 0) {
            $.each(order.order_items, function (index, item) {
                var listItem = $("<tr>").append(
                    $("<td>").text(item.product_name),
                    $("<td>").text(item.quantity),
                    $("<td>").text("₱" + item.price)
                );
                orderItemsList.append(listItem);
            });
        } else {
            orderItemsList.append('<tr><td colspan="3">No items found</td></tr>');
        }

        updateProgressBar(order.status);

        // Hide the spinner when data is ready
        spinner.removeClass("visible");
        backdrop.removeClass("visible");

        modal.find(".modal-content").removeClass("loading");

        // Show the modal after data is loaded
        modal.modal("show");

        // Close the "Calculating orders" message
        Swal.close();
    }, 2000); // Simulate delay for 2 seconds
});


  //ORDER PROGRESS BAR
  function updateProgressBar(status) {
    console.log("Updating progress bar for status:", status);
    // Reset all steps to their default state;

    // Remove existing classes and add appropriate classes based on order status
    switch (status) {
      case "processed":
        $("#step1").removeClass("text-muted").addClass("active");
        $("#step2, #step3, #step4")
          .removeClass("active")
          .addClass("text-muted");
        break;
      case "prepared":
        $("#step1, #step2").removeClass("text-muted").addClass("active");
        $("#step3, #step4").removeClass("active").addClass("text-muted");
        break;
      case "shipped":
        $("#step1, #step2, #step3")
          .removeClass("text-muted")
          .addClass("active");
        $("#step4").removeClass("active").addClass("text-muted");
        break;
      case "received":
        $(".step0").removeClass("text-muted").addClass("active");
        break;
      default:
        break;
    }
  }

  //DELETE ADDRESS

  $(".delete-address").click(function (e) {
    e.preventDefault();
    var addressId = $(this).data("address-id");
    
    // Display SweetAlert confirmation dialog
    Swal.fire({
        icon: 'warning',
        title: 'Are you sure?',
        text: 'You are about to delete this address.',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'Cancel'
    }).then((result) => {
        if (result.isConfirmed) {
            // If user confirms deletion, call deleteAddress function
            deleteAddress(addressId);
        }
    });
});

function deleteAddress(addressId) {
    $.ajax({
        type: "POST",
        url: deleteAddressUrl,
        data: {
            address_id: addressId,
            csrfmiddlewaretoken: csrf,
        },
        success: function (response) {
            $("#address-" + addressId).remove();
            spinner.removeClass("visible");
            backdrop.removeClass("visible");
        },
        error: function (xhr, textStatus, errorThrown) {
            console.log("Error:", errorThrown);
        },
    });
}

  //EDIT ADDRESS

  $(".edit-address").click(function (e) {
    e.preventDefault();
    var addressId = $(this).data("address-id");
    var updateAddressUrl = $(this).data("update-url");
    fetchAddressDetails(addressId);
    spinner.addClass("visible");
    backdrop.addClass("visible");

    $("#saveAddressChanges").data("update-url", updateAddressUrl);
    $("#saveAddressChanges").data("address-id", addressId);
  });

  function updateSelectValueAndTriggerChange(selectId, selectedValue) {
    $(selectId).val(selectedValue).trigger("change");
  }

  function fetchAddressDetails(addressId) {
    $.ajax({
      type: "GET",
      url: getAddressDetailsUrl,
      data: {
        address_id: addressId,
      },
      success: function (response) {
        // Populate the form fields in the modal with the retrieved address details
        $(".inputFirstName").val(response.address.first_name);
        $(".inputLastName").val(response.address.last_name);
        $(".inputEmail").val(response.address.email);
        $(".inputPhone").val(response.address.phone);
        $(".inputLine1").val(response.address.line1);
        $(".inputLine2").val(response.address.line2);
        $(".inputPostcode").val(response.address.postcode);
        $(".inputMessage").val(response.address.message);

        updateSelectValueAndTriggerChange(
          ".regionDropdown",
          response.address.region
        );
        updateSelectValueAndTriggerChange(
          ".provinceDropdown",
          response.address.province
        );
        updateSelectValueAndTriggerChange(
          ".cityDropdown",
          response.address.city
        );
        updateSelectValueAndTriggerChange(
          ".barangayDropdown",
          response.address.barangay
        );

        spinner.removeClass("visible");
        backdrop.removeClass("visible");

        $("#changeAddressModal").modal("hide");
        $("#editAddressModal").modal("show");
      },
      error: function (xhr, textStatus, errorThrown) {
        console.log("Error:", errorThrown);
      },
    });
  }

  // Handle form submission for updating the address
  $(".editAddressForm").submit(function (e) {
    e.preventDefault();
    var formData = new FormData($(this)[0]);
    saveAddressChanges(formData);
  });

  // Function to save address changes
  function saveAddressChanges(formData) {
    var updateAddressUrl = $("#saveAddressChanges").data("update-url");
    var addressId = $("#editAddressModal").data("address-id");

    console.log("Update Address URL:", updateAddressUrl);
    console.log("Address ID:", addressId);

    // Retrieve form field values
    formData.append("first_name", $(".inputFirstName").val());
    formData.append("last_name", $(".inputLastName").val());
    formData.append("email", $(".inputEmail").val());
    formData.append("phone", $(".inputPhone").val());
    formData.append("region", $(".regionDropdown").val());
    formData.append("province", $(".provinceDropdown").val());
    formData.append("city", $(".cityDropdown").val());
    formData.append("barangay", $(".barangayDropdown").val());
    formData.append("line1", $(".inputLine1").val());
    formData.append("line2", $(".inputLine2").val());
    formData.append("postcode", $(".inputPostcode").val());
    formData.append("message", $(".inputMessage").val());

    formData.append("address_id", addressId);
    formData.append("csrfmiddlewaretoken", csrf);

    $.ajax({
        type: "POST",
        url: updateAddressUrl,
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            console.log("Success Response:", response);

            $("#editAddressModal").modal("hide");

            updateShippingDetails(response.new_data);

            updateTableRow(response.address_id, response.new_data);
        },
        error: function (xhr, textStatus, errorThrown) {
            console.error("Error:", errorThrown);
            // Handle error
        },
    });
  }

  function updateTableRow(addressId, newData) {
    var row = $("#address-" + addressId);
    row
      .find(".table-list-code")
      .text(newData.first_name + " " + newData.last_name);
    row
      .find("td:nth-child(2)")
      .text(newData.line1 + ", " + newData.city + ", " + newData.postcode);
    row.find("td:nth-child(3)").text(newData.phone);
  }

  function updateShippingDetails(newData) {
    $("#customer-name").text(newData.first_name + " " + newData.last_name);
    $("#customer-mobile").text("+" + newData.phone);
    $("#customer-address").text(newData.postcode + ", " + newData.barangay + ", " + newData.city + ", " + newData.province + ", " + newData.region + ", Philippines");
  } 


  // Event listener for the "Save changes" button click
  $("#saveAddressChanges").click(function () {
    var addressId = $("#editAddressModal").data("address-id"); // Retrieve the address ID from modal data attribute
    var formData = new FormData($("#editAddressForm")[0]); // Create FormData object from form
    formData.append("address_id", addressId); // Append the address ID to the form data
    formData.append("csrfmiddlewaretoken", csrf); // Append the CSRF token to the form data
    saveAddressChanges(formData);
  });

});
