$(document).ready(function () {
  const getAddressDetailsUrl = "/get-address-details/";
  const deleteAddressUrl = "/delete-address/";
  const updateAddressUrl = "/update-address/";

  const navLinkEls = $(".nav__link");
  const contentDivs = $(".content-div");

  var spinner = $(".sk-circle");
  var backdrop = $(".backdrop");

  function handleNavLinkClick(index, linkElement) {
    if (!linkElement.hasClass("active")) {
      const activeNavLink = $(".nav__link.active");
      if (activeNavLink) {
        activeNavLink.removeClass("active");
      }
      linkElement.addClass("active");

      // Hide all content divs
      contentDivs.attr("hidden", true);

      // Show the corresponding content div
      contentDivs.eq(index).removeAttr("hidden");

      // Store the active index in localStorage
      localStorage.setItem("activeIndex", index);
    }
  }

  navLinkEls.each(function (index) {
    $(this).on("click", function () {
      handleNavLinkClick(index, $(this));
    });
  });

  // Get the active index from localStorage
  const activeIndex = localStorage.getItem("activeIndex");

  // If there is an active index stored in localStorage, click the corresponding link
  if (activeIndex !== null) {
    navLinkEls.eq(activeIndex).click();
  }

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
    var orderId = $(button).data("order-id");

    modal.find(".modal-body .alert").remove();
    modal.find(".modal-content").addClass("loading");

    //Load Spinner
    spinner.addClass("visible");
    backdrop.addClass("visible");

    // Fetch order details from the server
    $.get(`/get_order_details/?order_id=${orderId}`)
      .done(function (data) {
        // Update modal content with the fetched order details
        console.log("Order details:", data);
        modal.find(".modal-title").text("Order Details - " + data.order_id);
        modal.find(".invoice").text(data.order_id);
        modal.find("#orderDate, #orderMobile").text(data.created_at);
        modal.find(".orderQuantity").text(data.total_quantity);
        modal.find(".orderTotal").text("₱" + data.total_amount);

        var orderItemsList = modal.find("#orderItemsList");
        orderItemsList.empty();
        if (data.order_items.length > 0) {
          $.each(data.order_items, function (index, item) {
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

        updateProgressBar(data.status);

        // Hide the spinner when data is ready
        spinner.removeClass("visible");
        backdrop.removeClass("visible");

        modal.find(".modal-content").removeClass("loading");

        // Show the modal after data is loaded
        modal.modal("show");
      })
      .fail(function (jqXHR, textStatus, errorThrown) {
        console.error("Error fetching order details:", textStatus, errorThrown);
        // Example: Display error within the modal
        modal
          .find(".modal-body")
          .prepend(
            '<div class="alert alert-danger">Error fetching order details. Please try again later.</div>'
          );

        // Hide the spinner if there's an error
        spinner.removeClass("visible");
        backdrop.removeClass("visible");

        modal.find(".modal-content").removeClass("loading");
      });
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
    deleteAddress(addressId);
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
    fetchAddressDetails(addressId);
    spinner.addClass("visible");
    backdrop.addClass("visible");
  });

  function updateSelectValueAndTriggerChange(selectId, selectedValue) {
    $(selectId).val(selectedValue).trigger("change");
  }

  function fetchAddressDetails(addressId) {
    $.ajax({
      type: "GET",
      url: getAddressDetailsUrl,
      data: {
        'address_id': addressId,
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

        $("#changeAddressModal").modal("hide")
        $("#editAddressModal").modal("show");

      },
      error: function (xhr, textStatus, errorThrown) {
        console.log("Error:", errorThrown);
      },
    });
  }

  // Handle form submission for updating the address
  $("#editAddressForm").submit(function (e) {
    e.preventDefault();
    saveAddressChanges();
  });

  function updateTableRow(addressId, newData) {
    var row = $("#address-" + addressId);
    row.find(".table-list-code").text(newData.first_name + " " + newData.last_name);
    row.find("td:nth-child(2)").text(newData.line1 + ", " + newData.city + ", " + newData.postcode);
    row.find("td:nth-child(3)").text(newData.phone);
  }


  // Function to save address changes
  function saveAddressChanges(formData) {
    formData.append("address_id", $("#editAddressModal").data("address-id")); // Append the address ID to the form data
    formData.append("csrfmiddlewaretoken", csrf); // Add CSRF token
    $.ajax({
      type: "POST",
      url: updateAddressUrl,
      data: formData,
      processData: false, // Ensure formData is not processed as a query string
      contentType: false, // Ensure correct content type for formData
      success: function (response) {
        console.log(response);
        // Close the modal
        $("#editAddressModal").modal("hide");

        updateTableRow(response.address_id, response.new_data);
      },
      error: function (xhr, textStatus, errorThrown) {
        console.error("Error:", errorThrown);
        // Handle error
      },
    });
  }

  // Event listener for the "Save changes" button click
  $("#saveAddressChanges").click(function () {
    var addressId = $("#editAddressModal").data("address-id"); // Retrieve the address ID from modal data attribute
    var formData = new FormData($("#editAddressForm")[0]); // Create FormData object from form
    formData.append('address_id', addressId); // Append the address ID to the form data
    formData.append('csrfmiddlewaretoken', csrf); // Append the CSRF token to the form data
    saveAddressChanges(formData);
  });
});
