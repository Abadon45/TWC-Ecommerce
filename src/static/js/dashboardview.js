$(document).ready(function () {
  const navLinkEls = $(".nav__link");
  const contentDivs = $(".content-div");

  function handleNavLinkClick(index, linkElement) {
    if (!linkElement.hasClass("active")) {
      const activeNavLink = $(".nav__link.active");
      if (activeNavLink) {
        activeNavLink.removeClass("active");
      }
      linkElement.addClass("active");

      // Hide all content divs
      contentDivs.attr("hidden", true);

      // Show the corresponding content div
      contentDivs.eq(index).removeAttr("hidden");

      // Store the active index in localStorage
      localStorage.setItem("activeIndex", index);
    }
  }

  navLinkEls.each(function (index) {
    $(this).on("click", function () {
      handleNavLinkClick(index, $(this));
    });
  });

  // Get the active index from localStorage
  const activeIndex = localStorage.getItem("activeIndex");

  // If there is an active index stored in localStorage, click the corresponding link
  if (activeIndex !== null) {
    navLinkEls.eq(activeIndex).click();
  }

  $("#copyButton").click(function () {
    /* Get the text field */
    var copyText = $("#copyInput");

    /* Select the text field */
    copyText.select();

    /* Copy the text inside the text field */
    document.execCommand("copy");

    /* Alert the copied text */
    $(this).text("Copied!!");
  });

    $("#orderDetailsModal").on("show.bs.modal", function (event) {
        var modal = $(this);
        var spinner = $('.sk-circle');
        var backdrop = $('.backdrop'); 
        var button = event.relatedTarget;
        var orderId = $(button).data("order-id");


        modal.find(".modal-body .alert").remove(); 
        modal.find(".modal-content").addClass("loading");

        //Load Spinner
        spinner.addClass('visible');
        backdrop.addClass('visible');
        
    // Fetch order details from the server
        $.get(`/get_order_details/?order_id=${orderId}`)
            .done(function (data) {
                // Update modal content with the fetched order details
                console.log("Order details:", data);
                modal.find(".modal-title").text("Order Details - " + data.order_id);
                modal.find(".invoice").text(data.order_id);
                modal.find("#orderDate, #orderMobile").text(data.created_at);
                modal.find(".orderQuantity").text(data.total_quantity); 
                modal.find(".orderTotal").text("₱" + data.total_amount); 

                var orderItemsList = modal.find("#orderItemsList");
                orderItemsList.empty();
                if (data.order_items.length > 0) {
                    $.each(data.order_items, function (index, item) {
                        var listItem = $("<tr>").append(
                            $("<td>").text(item.product_name),
                            $("<td>").text(item.quantity),
                            $("<td>").text("₱" + item.price)
                        );
                        orderItemsList.append(listItem);
                    });
                } else {
                    orderItemsList.append('<tr><td colspan="3">No items found</td></tr>');
                }

                updateProgressBar(data.status);

                // Hide the spinner when data is ready
                spinner.removeClass('visible');
                backdrop.removeClass('visible');

                modal.find(".modal-content").removeClass("loading");

                // Show the modal after data is loaded
                modal.modal("show");
            })
            .fail(function (jqXHR, textStatus, errorThrown) {
                console.error("Error fetching order details:", textStatus, errorThrown);
                // Example: Display error within the modal   
                modal.find(".modal-body").prepend(
                    '<div class="alert alert-danger">Error fetching order details. Please try again later.</div>'
                );

                // Hide the spinner if there's an error
                spinner.removeClass('visible');
                backdrop.removeClass('visible');

                modal.find(".modal-content").removeClass("loading");
        });
    });


  //ORDER PROGRESS BAR
    function updateProgressBar(status) {
    console.log('Updating progress bar for status:', status);
    // Reset all steps to their default state;

    // Remove existing classes and add appropriate classes based on order status
    switch (status) {
        case 'processed':
            $('#step1').removeClass('text-muted').addClass('active');
            $('#step2, #step3, #step4').removeClass('active').addClass('text-muted');
            break;
        case 'prepared':
            $('#step1, #step2').removeClass('text-muted').addClass('active');
            $('#step3, #step4').removeClass('active').addClass('text-muted');
            break;
        case 'shipped':
            $('#step1, #step2, #step3').removeClass('text-muted').addClass('active');
            $('#step4').removeClass('active').addClass('text-muted');
            break;
        case 'received':
            $('.step0').removeClass('text-muted').addClass('active');
            break;
        default:
            break;
        }
    }
});
