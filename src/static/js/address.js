$(document).ready(function () {
    var selectedRegionCode;
    var spinner = $(".sk-circle");
    var backdrop = $(".backdrop");


    const input = $(".id_mobile")[0]; // Using jQuery to select the input element

    if (input) {
        // Clean up any existing intlTelInput instances
        if ($(input).data("iti")) {
            $(input).data("iti").destroy();
            $(input).removeData("iti");
        }
        if ($(input).parent().hasClass("iti")) {
            $(input).unwrap(); // Remove the .iti wrapper
        }

        const iti = window.intlTelInput(input, {
            initialCountry: "PH",
            onlyCountries: ["PH"],
            separateDialCode: true,
            nationalMode: false, // Allow full international format
            showFlags: true,
            utilsScript: "https://cdn.jsdelivr.net/npm/intl-tel-input@23.8.1/build/js/utils.js",
        });

        // Store the instance for reference
        $(input).data("iti", iti);

        // This function moves the dial code inside the selected country primary div
        const moveDialCode = function () {
            // Target the correct selected country container for this specific input
            const selectedCountry = $(input).closest(".iti").find(".iti__selected-country");

            // Find the dial code and country primary div inside the selected container
            const dialCode = selectedCountry.find(".iti__selected-dial-code");
            const countryPrimary = selectedCountry.find(".iti__selected-country-primary");

            // Only move if dial code exists and isn't already in the correct place
            if (dialCode.length > 0 && !dialCode.closest('.iti__selected-country-primary').length) {
                dialCode.detach().insertBefore(countryPrimary.find('.iti__arrow')); // Insert before the arrow
            }
        };


        // Move dial code when the country is changed
        $(input).on('countrychange', function () {
            moveDialCode();
        });

        // Move dial code when the page first loads (initial setup)
        moveDialCode();

        // Prevent letters and allow only numbers in the input field
        $(input).on("keydown", function (e) {
            const key = e.key;
            // Allow: backspace, delete, tab, escape, enter, and arrow keys
            if (
                $.inArray(e.keyCode, [46, 8, 9, 27, 13, 37, 38, 39, 40]) !== -1 ||
                // Allow: Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X, and Command keys
                (e.ctrlKey === true || e.metaKey === true) &&
                (key === "a" || key === "c" || key === "v" || key === "x")
            ) {
                return; // Allow these keys
            }
            // Prevent any key that is not a digit
            if (input.value.replace(/\s/g, '').length >= 10 && (key >= "0" && key <= "9")) {
                e.preventDefault(); // Prevent input if it's already 10 characters, excluding spaces
            }

        });


        const handleChange = function () {
            const formattedNumber = iti.getNumber();
            $("#id_mobile_full").val(formattedNumber);
        };

        // Format number when user types, and prevent leading zeros when user starts typing
        $(input).on("input change keyup blur", function () {
            let localNumber = input.value.trim();

            // Remove non-digit characters and leading zero if present
            localNumber = localNumber.replace(/\D/g, ''); // Remove any non-digit characters
            if (localNumber.startsWith("0") && localNumber.length > 1) {
                // Remove leading 0 only if user typed more than 1 character
                localNumber = localNumber.substring(1);
            }

            // Limit input to 10 digits
            localNumber = localNumber.slice(0, 10);

            // Apply phone number formatting (e.g., 917 770 0256)
            input.value = localNumber.replace(/(\d{3})(\d{3})(\d{4})/, '$1 $2 $3');

            handleChange();
        });

        // Ensure the complete phone number is in the hidden input on form submission
        $("form").on("submit", function () {
            handleChange();
        });
    }


    // =======================================================//
    // -------- Populate regions on page load --------//
    // =======================================================//
    // populateDropdown(".provinceDropdown", Philippines.provinces, "Select Province");
    // $(".postalInputBox").hide();
    //
    // // Handle province selection
    // $(".provinceDropdown").change(function () {
    //     var selectedProvinceCode = $(this).find("option:selected").data("code");
    //     console.log("Selected Province Code: " + selectedProvinceCode);
    //     var municipalitiesInProvince = Philippines.city_mun.filter(function (
    //         municipality
    //     ) {
    //         return municipality.prov_code === selectedProvinceCode;
    //     });
    //
    //     // Add the "Other (Specify City)" option
    //     municipalitiesInProvince.push({
    //         name: "Other (Specify City)",
    //         prov_code: "",
    //     });
    //
    //     populateDropdown(".cityDropdown", municipalitiesInProvince, "Select City");
    // });
    //
    // // Handle municipality selection
    // $(".cityDropdown").change(function () {
    //     var selectedMunicipalityCode = $(this).find(":selected").data("code");
    //     console.log("Selected Municipality Code: " + selectedMunicipalityCode);
    //
    //     // Show/hide the city input box based on the selected option
    //     var selectedCity = $(this).val();
    //     var postalCodeInput = $(".inputPostcode");
    //     var matchingCodes = [];
    //     $(".cityInputBox").toggle(selectedCity === "Other (Specify City)");
    //     if (selectedCity === "Other (Specify City)") {
    //         $(".cityDropdownBox").hide();
    //         $(".cityDropdown").attr("name", "city_input");
    //         $(".cityInputBox input")
    //             .attr("name", "city")
    //             .prop("required", true)
    //             .focus();
    //     } else {
    //         $(".cityDropdownBox").show();
    //         $(".cityDropdown").attr("name", "city");
    //         $(".cityInputBox input")
    //             .attr("name", "city_input")
    //             .removeAttr("required");
    //     }
    //
    //     $(".city-dropdown").click(function () {
    //         $(".cityInputBox").hide();
    //         $(".cityDropdownBox").show();
    //         $(".cityDropdown").attr("name", "city");
    //         $(".cityInputBox input")
    //             .attr("name", "city_input")
    //             .removeAttr("required");
    //         $(".cityDropdown").val("");
    //     });
    //
    //     postalCodeInput.val("");
    //
    //     console.log("Selected City:", selectedCity);
    //
    //     for (var code in zipCodeDB) {
    //         var city = zipCodeDB[code];
    //         if (
    //             typeof city === "string" &&
    //             city.toUpperCase() === selectedCity.toUpperCase()
    //         ) {
    //             matchingCodes.push(code);
    //             // postalCodeInput.val(code);
    //             // console.log('Postal code found:', code);
    //             // break;
    //         }
    //     }
    //
    //     if (matchingCodes.length === 1) {
    //         postalCodeInput.val(matchingCodes[0]);
    //         $(".postalInputBox").hide();
    //     } else {
    //         // Unhide the input group for manual entry
    //         $(".postalInputBox").show();
    //         console.log(
    //             "City has duplicates or no match found. Unhiding input group."
    //         );
    //     }
    //
    //     // Filter barangays based on the selected municipality
    //     var barangaysInMunicipality = Philippines.barangays.filter(function (
    //         barangay
    //     ) {
    //         return barangay.mun_code === selectedMunicipalityCode;
    //     });
    //
    //     barangaysInMunicipality.push({
    //         name: "Other (Specify Barangay)",
    //         mun_code: "",
    //     });
    //
    //     populateDropdown(
    //         ".barangayDropdown",
    //         barangaysInMunicipality,
    //         "Select Barangay"
    //     );
    //
    //     $(".barangayDropdown").change(function () {
    //         var selectedOption = $(this).val();
    //         $(".barangayInputBox").toggle(
    //             selectedOption === "Other (Specify Barangay)"
    //         );
    //         if (selectedOption === "Other (Specify Barangay)") {
    //             $(".barangayDropdownBox").hide();
    //             $(".barangayDropdown").attr("name", "barangay_input");
    //             $(".barangayInputBox input")
    //                 .attr("name", "barangay")
    //                 .prop("required", true)
    //                 .focus();
    //         } else {
    //             $(".barangayDropdownBox").show();
    //             $(".barangayDropdown").attr("name", "barangay");
    //             $(".barangayInputBox input")
    //                 .attr("name", "barangay_input")
    //                 .removeAttr("required");
    //         }
    //     });
    //
    //     $(".barangay-dropdown").click(function () {
    //         $(".barangayInputBox").hide();
    //         $(".barangayDropdownBox").show();
    //         $(".barangayDropdown").attr("name", "city");
    //         $(".barangayInputBox input")
    //             .attr("name", "city_input")
    //             .removeAttr("required");
    //         $(".barangayDropdown").val("");
    //     });
    // });
    //
    // // Function to populate a dropdown based on data
    // function populateDropdown(dropdownId, data, placeholder) {
    //     console.log("Dropdown ID: " + dropdownId);
    //     console.log("Data for Dropdown: ", data);
    //
    //     var dropdown = $(dropdownId);
    //     dropdown.empty();
    //     dropdown.append("<option selected>- " + placeholder + " -</option>");
    //
    //     $.each(data, function (index, item) {
    //         // Create an option with data-code attribute
    //         var option = $("<option></option>").val(item.name).text(item.name);
    //
    //         // Set data-code attribute based on the item's code property
    //         if (item.reg_code) option.data("code", item.reg_code);
    //         if (item.prov_code) option.data("code", item.prov_code);
    //         if (item.mun_code) option.data("code", item.mun_code);
    //
    //         dropdown.append(option);
    //     });
    // }
});