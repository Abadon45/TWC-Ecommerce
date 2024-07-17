$(document).ready(function() {
    // Fetch the clicked_order_id from Django session using an AJAX request
    $.ajax({
        type: "GET",
        url: dashboardURL,
        dataType: "json",
        success: function(response) {
            var clickedOrderId = response.clicked_order_id;
            console.log("Clicked Order ID from Django session:", clickedOrderId);
            if (clickedOrderId) {
                setTimeout(function() {
                    console.log("Click event triggered for Order ID:", clickedOrderId);
                    $("[data-order-id='" + clickedOrderId + "']").click();
                }, 100); // Adjust the delay time as needed
                // Optionally, clear the stored information after using it
                sessionStorage.removeItem("clickedOrderId");
            }
        },
        error: function(xhr, errmsg, err) {
            console.error("Error fetching clicked_order_id from Django session:", err);
        }
    });
});
