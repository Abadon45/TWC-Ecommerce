$(document).ready(function () {
    const apiURL = addressApiUrl; // Updated API URL

    // Fetch address data from the Django view
    function fetchAddressData() {
        $.get(apiURL, function (response) {
            if (response.error) {
                console.error('Error:', response.error);
            } else {
                populateProvinces(response);
            }
        }).fail(function (xhr, status, error) {
            console.error('Failed to fetch address data:', error);
        });
    }

    // Populate provinces dropdown
    function populateProvinces(data) {
        const provinceDropdown = $('.provinceDropdown');
        provinceDropdown.empty().append('<option selected>- Select Province -</option>');

        data.forEach(province => {
            provinceDropdown.append(`<option value="${province.province}">${province.province}</option>`);
        });

        provinceDropdown.on('change', function () {
            const selectedProvince = $(this).val();
            const selectedProvinceData = data.find(p => p.province === selectedProvince);
            if (selectedProvinceData) {
                populateCities(selectedProvinceData.cities);
            }
        });
    }

    // Populate cities dropdown
    function populateCities(cities) {
        const cityDropdown = $('.cityDropdown');
        cityDropdown.empty().append('<option selected>- Select City -</option>');

        cities.forEach(city => {
            cityDropdown.append(`<option value="${city.city}">${city.city}</option>`);
        });

        // Add "Other (Specify City)" option
        cityDropdown.append('<option value="Other (Specify City)">Other (Specify City)</option>');

        cityDropdown.on('change', function () {
            const selectedCity = $(this).val();
            if (selectedCity === "Other (Specify City)") {
                $(".cityDropdownBox").hide();
                $(".cityInputBox").show();
                $(".cityDropdown").attr("name", "city_input");
                $(".cityInputBox input")
                    .attr("name", "city")
                    .prop("required", true)
                    .focus();
                $('.barangayDropdown').empty()
                    .append('<option selected>- Barangay -</option>')
                    .append('<option value="Other (Specify Barangay)">Other (Specify Barangay)</option>');
            } else {
                $(".cityDropdownBox").show();
                $(".cityDropdown").attr("name", "city");
                $(".cityInputBox input")
                    .attr("name", "city_input")
                    .removeAttr("required");
            }
        });

        $(".city-dropdown").click(function () {
            $(".cityInputBox").hide();
            $(".cityDropdownBox").show();
            $(".cityDropdown").attr("name", "city");
            $(".cityInputBox input")
                .attr("name", "city_input")
                .removeAttr("required");
            $(".cityDropdown").val("");
        });

        cityDropdown.on('change', function () {
            const selectedCity = $(this).val();
            const selectedCityData = cities.find(c => c.city === selectedCity);
            if (selectedCityData) {
                populateBarangays(selectedCityData.barangays);
            }
        });
    }

    // Populate barangays dropdown
    function populateBarangays(barangays) {
        const barangayDropdown = $('.barangayDropdown');
        barangayDropdown.empty().append('<option selected>- Barangay -</option>');

        barangays.forEach(barangay => {
            barangayDropdown.append(`<option value="${barangay}">${barangay}</option>`);
        });

        // Add "Other (Specify Barangay)" option
        barangayDropdown.append('<option value="Other (Specify Barangay)">Other (Specify Barangay)</option>');

        barangayDropdown.on('change', function () {
            const selectedBarangay = $(this).val();
            if (selectedBarangay === "Other (Specify Barangay)") {
                $(".barangayDropdownBox").hide();
                $(".barangayInputBox").show();
                $(".barangayDropdown").attr("name", "barangay_input");
                $(".barangayInputBox input")
                    .attr("name", "barangay")
                    .prop("required", true)
                    .focus();
            } else {
                $(".barangayDropdownBox").show();
                $(".barangayDropdown").attr("name", "barangay");
                $(".barangayInputBox input")
                    .attr("name", "barangay_input")
                    .removeAttr("required");
            }
        });

        $(".barangay-dropdown").click(function () {
            $(".barangayInputBox").hide();
            $(".barangayDropdownBox").show();
            $(".barangayDropdown").attr("name", "barangay");
            $(".barangayInputBox input")
                .attr("name", "barangay_input")
                .removeAttr("required");
            $(".barangayDropdown").val("");
        });
    }

    // Initialize the fetching process
    fetchAddressData();
});
