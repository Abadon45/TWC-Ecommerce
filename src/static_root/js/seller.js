function copyToClipboard(textElementId, buttonElementId) {
    var textToCopy = $("#" + textElementId).val().trim();
    var tempInput = $("<input>");

    $("body").append(tempInput);
    tempInput.val(textToCopy).select();
    document.execCommand("copy");
    tempInput.remove();
    $("#" + buttonElementId).text("Copied!");
    setTimeout(function() {
        $("#" + buttonElementId).text("Copy");
    }, 3000);
}
