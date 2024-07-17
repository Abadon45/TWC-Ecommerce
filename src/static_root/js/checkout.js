$(document).ready(function() {

    $(".paymentBtn").on("click", function (e) {
        e.preventDefault();
        $("#step2-tab").click();
        $("#step1").removeClass("active show");
        $("#step1-tab").removeClass("nav-link active done");
        $("#step1-tab").addClass("nav-link done");
        $("#step2").addClass("active show");
        $("#step2-tab").addClass("active done");
    });

});
