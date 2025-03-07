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
});