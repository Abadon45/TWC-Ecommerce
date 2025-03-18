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
    const fullName = $('input[name="full_name"]').val()?.trim() || "";
    const phone = $('input[name="phone_display"]').val()?.trim() || "";
    const address = $('input[name="address"]').val()?.trim() || "";
    const province = $('select[name="province"]').val() || "";
    const landmark = $('textarea[name="landmark"]').val()?.trim() || "";

    // Determine city selection (manual input or dropdown)
    const city = $('.cityInputBox').is(':visible')
        ? $('input[name="city"]').val()?.trim() || ""
        : $('select[name="city"]').val()?.trim() || "";

    // Determine barangay selection (manual input or dropdown)
    const barangay = $('.barangayInputBox').is(':visible')
        ? $('.barangayInputBox input').val()?.trim() || ""
        : $('select[name="barangay"]').val()?.trim() || "";

    // Validate missing fields
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
    if (!barangay || barangay === "- Barangay -" || barangay === "") missingFields.push('Barangay');
    if (!landmark) missingFields.push('Landmark');

    if (missingFields.length) {
        Swal.fire({
            icon: 'warning',
            title: 'Incomplete Address',
            text: `Please fill in or select: ${missingFields.join(', ')}`,
            confirmButtonText: 'OK'
        });
        return;
    }

    // Submit the form
    $('#addUserData').click();
}