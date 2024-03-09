$(document).ready(function () {
  var selectedRegionCode;
  var spinner = $(".sk-circle");
  var backdrop = $(".backdrop");

  // =======================================================//
  // -------- Modal popups --------//
  // =======================================================//
  $(".cancelAddress").click(function () {
    $("#addAddressModal").modal("hide");
    $("#changeAddressModal").modal("show");
  });

  $(".change-address-btn").click(function () {
    if ($("#changeAddressModal").hasClass("modal")) {
      var changeAddressModal = new bootstrap.Modal(
        document.getElementById("changeAddressModal")
      );
      changeAddressModal.show();
    } else {
      $("#changeAddressModal").modal("show");
    }
  });

  $('#changeAddressModal button[style*="fa-plus"]').click(function () {
    alert("Button clicked!");
    $("#addressFormContainer").show();
  });

  $("#changeAddressModal").on("hidden.bs.modal", function () {
    $("#addressFormContainer").hide();
  });

  $("#addNewAddressBtn").click(function () {
    $("#changeAddressModal").modal("hide");
    $("#addAddressModal").modal("show");
  });

  $(".close-edit-address").click(function () {
    $("#editAddressDetailModal").modal("hide");
    $("#changeAddressModal").modal("show");
  });

  // =======================================================//
  // -------- Change Address  --------//
  // =======================================================//

  $(".changeAddressBtn").click(function () {
    var selectedAddressId = $("input[name='addressChoice']:checked").data(
      "address-id"
    );
    console.log(selectedAddressId);
    $.ajax({
      type: "GET",
      url: selectedAddressUrl,
      data: {
        selected_address_id: selectedAddressId,
      },
      success: function (response) {
        // Handle success response
        console.log("Address selection successful");
        $("#changeAddressModal").modal("hide");

        $(".selected_address").html(
          "<b>" +
            response.address.first_name +
            " " +
            response.address.last_name +
            " " +
            response.address.phone +
            "</b>"
        );

        $(".address_details").html(
          response.address.line1 +
            " Brgy. " +
            response.address.barangay +
            ", " +
            response.address.city +
            ", " +
            response.address.province +
            ", " +
            response.address.postcode
        );

        if (!response.address.is_default) {
          $(".is_default").css({
            "border-color": "black",
            color: "black",
          });
        } else {
          $(".is_default").css({
            "border-color": "orange",
            color: "orange",
          });
        }

        $(".is_default").text(
          response.address.is_default ? "Default" : "Pickup"
        );
      },
      error: function (xhr, textStatus, errorThrown) {
        // Handle error
        console.error("Error selecting address:", errorThrown);
      },
    });
  });

  // =======================================================//
  // ------------ Edit Address submission -----------//
  // =======================================================//
  $(".edit-checkout-address").click(function (e) {
    e.preventDefault();
    var addressId = $(this).data("address-id");
    console.log(addressId);
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
      url: getCheckoutAddressDetailsUrl,
      data: {
        address_id: addressId,
      },
      success: function (response) {
        console.log(response);
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

        $("#editAddressDetailModal").data("address-id", response.address.address_id);

        spinner.removeClass("visible");
        backdrop.removeClass("visible");

        $("#changeAddressModal").modal("hide");
        $("#editAddressDetailModal").modal("show");
      },
      error: function (xhr, textStatus, errorThrown) {
        console.log("Error:", errorThrown);
      },
    });
  }

  // =======================================================//
  // -------- Address Form submission --------//
  // =======================================================//
  function createAddressElement(addressData) {
    const addressHTML = `
          <div class="col-lg-1"><input type="radio" name="addressChoice" data-address-id="${addressData.id}"></div>
          <div class="col-lg-9">
            <p><b>${addressData.firstName} ${addressData.lastName} ${addressData.phone}</b></p>
            <div class="change-address row mb-20">
              <div class="col-lg-10">
                  <p>${addressData.line1} Brgy. ${addressData.barangay}, ${addressData.city}, ${addressData.province}, ${addressData.postcode}</p>
              </div>
            </div>
          </div>
          <div class="col-lg-2">
              <a href="#">Edit</a>
          </div>
          <hr class="mt-2 mb-3">
        `;
    return addressHTML;
  }

  function addNewAddress(newAddressData) {
    const addressElement = createAddressElement(newAddressData);

    // Find the 'Add New Address' button
    const addNewAddressBtn = $("#addNewAddressBtn");

    // Add the new address before the 'Add New Address' button
    addNewAddressBtn.before(addressElement);
  }

  $(document).on("submit", "#addAddressForm", function (e) {
    // Attach to 'document'
    e.preventDefault();

    var thisForm = $(this);
    var submitButton = thisForm.find('button[type="submit"]');

    var actionEndpoint = thisForm.attr("action");
    var httpMethod = thisForm.attr("method");
    var formData = thisForm.serializeArray();

    console.log(formData);
    submitButton.prop("disabled", true); // Disable the button
    submitButton.append('<div class="spinner"></div>');

    $.ajax({
      url: actionEndpoint,
      method: httpMethod,
      data: formData,
      complete: function () {
        submitButton.prop("disabled", false); // Re-enable
        submitButton.find(".spinner").remove(); // Remove spinner
      },
      success: function (successData) {
        console.log(successData);
        const newAddressData = {
          firstName: successData.firstName,
          lastName: successData.lastName,
          phone: successData.phone,
          line1: successData.line1,
          province: successData.province,
          city: successData.city,
          barangay: successData.barangay,
          postcode: successData.postcode,
        };

        addNewAddress(newAddressData);
        $("#addAddressModal").modal("hide");
        $("#changeAddressModal").modal("show");
      },
      error: function (errorData) {
        console.log(errorData);
      },
    });
  });

  //Submitting Edit Form
  $("#editAddressDetailForm").submit(function (e) {
    e.preventDefault();
    saveAddressChanges();
  });

  //Update Modal Row HTML
  function updateTableRow(addressId, newData) {
    var row = $("#address-" + addressId);
    row.find(".address-name").css("font-weight", "bold").text(newData.first_name + " " + newData.last_name + " " + newData.phone);
    row
      .find(".address-line")
      .text(
        newData.line1 +
          ", Brgy. " +
          newData.barangay +
          " " +
          newData.city +
          ", " +
          newData.province +
          ", " +
          newData.postcode
      );
  }

  // Function to save address changes
  function saveAddressChanges(formData) {
    var addressId = $("#editAddressDetailModal").data("address-id"); // Retrieve the address ID from modal data attribute
    formData.append("address_id", addressId); // Append the address ID to the form data
    formData.append("csrfmiddlewaretoken", csrf);

    $.ajax({
      type: "POST",
      url: editCheckoutAddressUrl,
      data: formData,
      processData: false,
      contentType: false,
      success: function (response) {
        console.log(response);
        // Close the modal
        $("#editAddressDetailModal").modal("hide");
        $("#changeAddressModal").modal("show");

        spinner.removeClass("visible");
        backdrop.removeClass("visible");

        updateTableRow(response.address_id, response.new_data);
      },
      error: function (xhr, textStatus, errorThrown) {
        console.error("Error:", errorThrown);
        // Handle error
      },
    });
  }

  // Event listener for the "Save changes" button click
  $("#saveCheckoutAddressChanges").click(function () {
    var addressId = $("#editAddressDetailModal").data("address-id"); // Retrieve the address ID from modal data attribute
    var formData = new FormData($("#editAddressDetailForm")[0]); // Create FormData object from form
    formData.append("address_id", addressId); // Append the address ID to the form data
    formData.append("csrfmiddlewaretoken", csrf); // Append the CSRF token to the form data

    spinner.addClass("visible");
    backdrop.addClass("visible");

    saveAddressChanges(formData);
  });

  // =======================================================//
  // -------- Populate regions on page load --------//
  // =======================================================//
  populateDropdown(".regionDropdown", Philippines.regions);

  // Handle region selection
  $(".regionDropdown").change(function () {
    selectedRegionCode = $(this).find(":selected").data("code");
    console.log("Selected Region Code: " + selectedRegionCode);
    var provincesInRegion = Philippines.provinces.filter(function (province) {
      return province.reg_code === selectedRegionCode;
    });
    populateDropdown(".provinceDropdown", provincesInRegion);
    $(".cityDropdown, .barangayDropdown").empty(); // Clear other dropdowns
  });

  // Handle province selection
  $(".provinceDropdown").change(function () {
    var selectedProvinceCode = $(this).find("option:selected").data("code");
    console.log("Selected Province Code: " + selectedProvinceCode);
    var municipalitiesInProvince = Philippines.city_mun.filter(function (
      municipality
    ) {
      return municipality.prov_code === selectedProvinceCode;
    });
    populateDropdown(".cityDropdown", municipalitiesInProvince);
    $(".barangayDropdown").empty(); // Clear barangay dropdown
  });

  // Handle municipality selection
  $(".cityDropdown").change(function () {
    var selectedMunicipalityCode = $(this).find(":selected").data("code");
    console.log("Selected Municipality Code: " + selectedMunicipalityCode);

    // Filter barangays based on the selected municipality
    var barangaysInMunicipality = Philippines.barangays.filter(function (
      barangay
    ) {
      return barangay.mun_code === selectedMunicipalityCode;
    });

    barangaysInMunicipality.push({
      name: "Other (Specify Barangay)",
      mun_code: "",
    });

    populateDropdown(".barangayDropdown", barangaysInMunicipality);

    $(".barangayDropdown").change(function () {
      var selectedOption = $(this).val();
      $(".barangayInputBox").toggle(
        selectedOption === "Other (Specify Barangay)"
      );
      if (selectedOption === "Other (Specify Barangay)") {
        $(".barangayDropdown").attr("name", "barangay_input");
        $(".barangayInputBox input").attr("name", "barangay");
        $(".barangayInputBox input").prop("required", true);
      } else {
        $(".barangayDropdown").attr("name", "barangay");
        $(".barangayInputBox input").attr("name", "barangay_input");
        $(".barangayInputBox input").removeAttr("required");
      }
    });
  });

  // Function to populate a dropdown based on data
  function populateDropdown(dropdownId, data) {
    console.log("Dropdown ID: " + dropdownId);
    console.log("Data for Dropdown: ", data);

    var dropdown = $(dropdownId);
    dropdown.empty();
    dropdown.append("<option selected>- Select -</option>");

    $.each(data, function (index, item) {
      // Create an option with data-code attribute
      var option = $("<option></option>").val(item.name).text(item.name);

      // Set data-code attribute based on the item's code property
      if (item.reg_code) option.data("code", item.reg_code);
      if (item.prov_code) option.data("code", item.prov_code);
      if (item.mun_code) option.data("code", item.mun_code);

      dropdown.append(option);
    });
  }
});
