function isPhMobileNumber(number) {
    // Regular expression for Philippine mobile numbers
    const pattern = /^9\d{2}\s?\d{3}\s?\d{4}$/;
    return pattern.test(number);
}

function submitForm() {
    const fullName = $('input[name="full_name"]').val().trim();
    const phone = $('input[name="phone_display"]').val().trim();
    const address = $('input[name="address"]').val().trim();
    const province = $('select[name="province"]').val();
    const city = $('select[name="city"]').val();
    const barangay = $('select[name="barangay"]').val();
    const landmark = $('textarea[name="landmark"]').val().trim();

    console.log("Phone: " + phone)


    // Validate if any required field is missing
    let missingFields = [];

    if (!fullName) missingFields.push('Full Name');
    if (!phone) {
        missingFields.push('Phone');
    } else if (!isPhMobileNumber(phone)) {
        missingFields.push('Phone (Invalid Philippine Mobile Number)');
    }
    if (!address) missingFields.push('Address');
    if (!province || province === "- Select Province -") missingFields.push('Province');
    if (!city || city === "- Select City -") missingFields.push('City');
    if (!barangay || barangay === "- Barangay -") missingFields.push('Barangay');
    if (!landmark) missingFields.push('Landmark');


    if (missingFields.length > 0) {
        if (missingFields.length > 1) {
            const lastField = missingFields.pop();
            Swal.fire({
                icon: 'warning',
                title: 'Incomplete Address',
                text: 'Please fill in or select the following fields: ' + missingFields.join(', ') + ', and ' + lastField,
                confirmButtonText: 'OK'
            });
        } else {
            Swal.fire({
                icon: 'warning',
                title: 'Incomplete Address',
                text: 'Please fill in or select the following field: ' + missingFields[0],
                confirmButtonText: 'OK'
            });
        }

    } else {
        $('#addUserData').click();
    }
}