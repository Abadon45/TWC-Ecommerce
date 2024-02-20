$(document).ready(function() {
    const navLinkEls = $('.nav__link');
    const contentDivs = $('.content-div');

    function handleNavLinkClick(index, linkElement) {
        if (!linkElement.hasClass('active')) {
            const activeNavLink = $('.nav__link.active');
            if (activeNavLink) {
                activeNavLink.removeClass('active');
            }
            linkElement.addClass('active');

            // Hide all content divs
            contentDivs.attr('hidden', true);

            // Show the corresponding content div
            contentDivs.eq(index).removeAttr('hidden');

            // Store the active index in localStorage
            localStorage.setItem('activeIndex', index);
        }
    }

    navLinkEls.each(function(index) {
        $(this).on('click', function() {
            handleNavLinkClick(index, $(this));
        });
    });

    // Get the active index from localStorage
    const activeIndex = localStorage.getItem('activeIndex');

    // If there is an active index stored in localStorage, click the corresponding link
    if (activeIndex !== null) {
        navLinkEls.eq(activeIndex).click();
    }

    $("#copyButton").click(function(){
        /* Get the text field */
        var copyText = $("#copyInput");
    
        /* Select the text field */
        copyText.select();
    
        /* Copy the text inside the text field */
        document.execCommand("copy");
    
        /* Alert the copied text */
        $(this).text("Copied!!");
    });

    $('#orderDetailsModal').on('show.bs.modal', function (event) {
        var modal = $(this);
        var button = event.relatedTarget;
        var orderId = $(button).data('order-id');

        // Fetch order details from the server
        $.get(`/get_order_details/?order_id=${orderId}`)
            .done(function (data) {
                // Update modal content with the fetched order details
                console.log('Order details:', data);
                var modalTitle = modal.find('.modal-title');
                modalTitle.text('Order Details - ' + data.order_id);

                var orderDateField = modal.find('#orderDate');
                orderDateField.text(data.created_at);

                var orderDateField = modal.find('#orderMobile');
                orderDateField.text(data.created_at);

                var orderTotalField = modal.find('#orderTotal');
                orderTotalField.text('₱' + data.total_amount);

                var orderItemsList = modal.find('#orderItemsList');
                orderItemsList.empty();
                if (data.order_items.length > 0) {
                    $.each(data.order_items, function (index, item) {
                        var listItem = $('<tr>').append(
                            $('<td>').text(item.product_name),
                            $('<td>').text(item.quantity),
                            $('<td>').text('₱' + item.price)
                        );
                        orderItemsList.append(listItem);
                    });
                } else {
                    orderItemsList.append('<tr><td colspan="3">No items found</td></tr>');
                }
            })
            .fail(function (jqXHR, textStatus, errorThrown) {
                console.error('Error fetching order details:', textStatus, errorThrown);      
                // Example: Display error within the modal
                modal.find('.modal-body').prepend('<div class="alert alert-danger">Error fetching order details. Please try again later.</div>'); 
            });
    });
});

