$(document).ready(function () {
    const apiURL = 'https://dashboard.twcdevtest.com/addresses/api/get-address/';

    // Fetch address data from the API
    function fetchAddressData() {
        $.ajax({
            url: apiURL,
            method: 'GET',
            success: function (response) {
                populateProvinces(response);
            },
            error: function (xhr, status, error) {
                console.error('Failed to fetch address data:', error);
            }
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
    }

    // Initialize the fetching process
    fetchAddressData();
});
