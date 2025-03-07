function isPhMobileNumber(number) {
    // Normalize input by removing spaces
    let sanitizedNumber = number.replace(/\s+/g, "");

    // Add leading '0' if the number is 10 digits starting with '9'
    if (sanitizedNumber.length === 10 && /^[98]/.test(sanitizedNumber)) {
        sanitizedNumber = "0" + sanitizedNumber;
    }

    // Validate 11-digit numbers starting with '09'
    if (sanitizedNumber.length === 11 && /^0[89]/.test(sanitizedNumber)) {
        const prefix = sanitizedNumber.substring(0, 4);
        return phNumbers.includes(prefix);
    }

    // If neither condition is met, it's not a valid Philippine mobile number
    return false;
}

function submitForm() {
    const fullName = $('input[name="full_name"]').val().trim();
    const phone = $('input[name="phone_display"]').val().trim();
    const email = $('input[name="email"]').val().trim();
    const address = $('input[name="address"]').val().trim();
    const province = $('select[name="province"]').val();
    const city = $('select[name="city"]').val();
    const barangay = $('select[name="barangay"]').val();
    const landmark = $('textarea[name="landmark"]').val().trim();


    // Validate if any required field is missing
    let missingFields = [];

    if (!fullName) missingFields.push('Full Name');
    if (!email) missingFields.push('Email');
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

