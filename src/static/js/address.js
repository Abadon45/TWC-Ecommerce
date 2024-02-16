
$(document).ready(function () {
    var selectedRegionCode; 

    $('.cancelAddress').click(function() {
        $('#addAddressModal').modal('hide'); 
        $('#changeAddressModal').modal('show'); 
    });
    
    $('.change-address-btn').click(function() {
        // Adapt based on the Bootstrap version in use:
        if ($('#changeAddressModal').hasClass('modal')) { 
            // Assuming you use Bootstrap 5...
            var changeAddressModal = new bootstrap.Modal(document.getElementById('changeAddressModal')) 
            changeAddressModal.show();
        } else {
             // Assuming you use Bootstrap 4 or prior
            $('#changeAddressModal').modal('show');
        } 
    });

    $('#changeAddressModal button[style*="fa-plus"]').click(function() { 
        alert('Button clicked!'); 
        $('#addressFormContainer').show(); 
    });

    $('#changeAddressModal').on('hidden.bs.modal', function() { // Modal close event
        $('#addressFormContainer').hide(); 
    });

    $('#addNewAddressBtn').click(function() {
        $('#changeAddressModal').modal('hide'); // Hide the initial modal
        $('#addAddressModal').modal('show'); // Show the add address modal  
    });

    function changeAddressElement(selectedAddressData) {
        console.log("changeAddressElement called with data:", selectedAddressData);
        const addressHTML = `
            <div class="col-lg-1">
                <input type="radio" name="addressChoice" id="defaultAddress" data-address-text="${selectedAddressData.nameLine} - ${selectedAddressData.addressLine}">  
            </div>
            <div class="col-lg-9">
                <p class="address-name" data-name="${selectedAddressData.nameLine}"><b>${selectedAddressData.nameLine}</b></p> 
                <div class="change-address row mb-20" data-address-details>
                    <div class="col-lg-10">
                        <p data-address-line>${selectedAddressData.addressLine}</p> 
                    </div>
                </div>
            </div>
            <div class="col-lg-2">
                <a href="#">Edit</a>
            </div>
            <hr class="mt-2 mb-3">
        `;
        console.log("Generated addressHTML:", addressHTML);
        return addressHTML;
    }

    function handleAddressSelection() {
        console.log("handleAddressSelection triggered");
        const selectedAddressRadio = document.querySelector('input[name="addressChoice"]:checked');
        console.log("Selected address radio:", selectedAddressRadio);
        if (selectedAddressRadio) { 
            const addressContainer = selectedAddressRadio.closest('[data-address-details]');
            console.log("Found address container:", addressContainer);

            const nameElement = addressContainer.querySelector('[data-name]'); // Find elements first
            const addressElement = addressContainer.querySelector('[data-address-line]');

            if (nameElement && addressElement) { // Check if elements were found
                const nameLine = nameElement.textContent;
                const addressLine = addressElement.textContent;
                // ... (Rest of your update logic)
            } else {
                console.error(
                    "Error: nameLine or addressLine element NOT FOUND within address container" 
                );  
            }

            console.log("Extracted nameLine:", nameLine);
            console.log("Extracted addressLine:", addressLine);
    
            // Update existing display element
            const selectedAddressDisplay = document.getElementById('selected-address'); 
            console.log("Found selectedAddressDisplay:", selectedAddressDisplay);
            if (selectedAddressDisplay) {
                selectedAddressDisplay.innerHTML = changeAddressElement({ nameLine, addressLine });
            }
        }
    }
    
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('changeAddressBtn')) {
            e.preventDefault();
            handleAddressSelection();
        }
    });

    function createAddressElement(addressData) {
        const addressHTML = `
          <div class="col-lg-1"><input type="radio" name="addressChoice" id="defaultAddress"></div>
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
        const addNewAddressBtn = $('#addNewAddressBtn'); 
    
        // Add the new address before the 'Add New Address' button
        addNewAddressBtn.before(addressElement); 
    }

    $(document).on('submit', '#addAddressForm', function (e) { // Attach to 'document'
        e.preventDefault();

        var thisForm = $(this);
        var submitButton = thisForm.find('button[type="submit"]')
    
        var actionEndpoint = thisForm.attr("action");
        var httpMethod = thisForm.attr("method");
        var formData = thisForm.serializeArray();
    
        console.log(formData);
        submitButton.prop('disabled', true); // Disable the button
        submitButton.append('<div class="spinner"></div>');

        $.ajax({
            url: actionEndpoint,
            method: httpMethod,
            data: formData,
            complete: function() { 
                submitButton.prop('disabled', false); // Re-enable
                submitButton.find('.spinner').remove(); // Remove spinner
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
                $('#addAddressModal').modal('hide');
                $('#changeAddressModal').modal('show');
            },
            error: function (errorData) {
            console.log(errorData);
          },
        });
    });

    // Populate regions on page load
    populateDropdown("#regionDropdown", Philippines.regions);

    // Handle region selection
    $("#regionDropdown").change(function () {
        selectedRegionCode = $(this).find(":selected").data("code");
        console.log("Selected Region Code: " + selectedRegionCode);
        var provincesInRegion = Philippines.provinces.filter(function (province) {
            return province.reg_code === selectedRegionCode;
        });
        populateDropdown("#provinceDropdown", provincesInRegion);
        $("#cityDropdown, #barangayDropdown").empty(); // Clear other dropdowns
    });

    // Handle province selection
    $("#provinceDropdown").change(function () {
        var selectedProvinceCode = $(this).find("option:selected").data("code");
        console.log("Selected Province Code: " + selectedProvinceCode);
        var municipalitiesInProvince = Philippines.city_mun.filter(function (municipality) {
            return municipality.prov_code === selectedProvinceCode;
        });
        populateDropdown("#cityDropdown", municipalitiesInProvince);
        $("#barangayDropdown").empty(); // Clear barangay dropdown
    });

    // Handle municipality selection
    $("#cityDropdown").change(function () {
        var selectedMunicipalityCode = $(this).find(":selected").data("code");
        console.log("Selected Municipality Code: " + selectedMunicipalityCode);
    
        // Filter barangays based on the selected municipality
        var barangaysInMunicipality = Philippines.barangays.filter(function (barangay) {
            return barangay.mun_code === selectedMunicipalityCode;
        });
    
        populateDropdown("#barangayDropdown", barangaysInMunicipality);
    });

    // Function to populate a dropdown based on data
    function populateDropdown(dropdownId, data) {
        console.log("Dropdown ID: " + dropdownId);
        console.log("Data for Dropdown: ", data);
    
        var dropdown = $(dropdownId);
        dropdown.empty();
        dropdown.append('<option selected>- Select -</option>');
    
        $.each(data, function (index, item) {
            // Create an option with data-code attribute
            var option = $('<option></option>').val(item.name).text(item.name);
    
            // Set data-code attribute based on the item's code property
            if (item.reg_code) option.data("code", item.reg_code);
            if (item.prov_code) option.data("code", item.prov_code);
            if (item.mun_code) option.data("code", item.mun_code);
        
    
            dropdown.append(option);
        });
    }
    
});