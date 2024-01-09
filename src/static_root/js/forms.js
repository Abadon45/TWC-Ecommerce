$(document).ready(function () {
    var productForm = $("#addProduct");
    var shippingForm = $("#addShipping");
    var copyCheckbox = $("#copy-previous-form-data");

    productForm.submit(function (e) {
        e.preventDefault();
        var thisForm = $(this);
        var actionEndpoint = thisForm.attr("action");
        var httpMethod = thisForm.attr("method");
        var formData = new FormData(thisForm[0]);

        $.ajax({
            url: actionEndpoint,
            method: httpMethod,
            data: formData,
            cache: false,
            contentType: false,
            processData: false,
            success: function (response) {
                window.location.href = window.location.href + '../';
            },
            error: function (errorData) {
                console.log(errorData);
            }
        });
    });

    shippingForm.submit(function (e) {
        e.preventDefault();
        var thisForm = $(this);
        var actionEndpoint = thisForm.attr("action");
        var httpMethod = thisForm.attr("method");
        var formData = thisForm.serialize();
        console.log(formData);

        $.ajax({
            url: actionEndpoint,
            method: httpMethod,
            data: formData,
            success: function (successData) {
                console.log(successData);
                $("#step2-tab").click();
                $("#step1").removeClass("active show");
                $("#step2").addClass("active show");

            },
            error: function (errorData) {
                console.log(errorData);
            }
        });
    });
});

