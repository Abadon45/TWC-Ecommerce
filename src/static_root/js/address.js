
$(document).ready(function () {
    var selectedRegionCode; 

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