function bookOrder(button) {
  var courierId = $(button).data('courier-id');
  var fulfiller = $(button).data('courier-fulfiller');
  var fulfiller_full = $(button).data('courier-fulfiller_full');
  var spinner = $(".sk-circle");
  var backdrop = $(".backdrop");

  Swal.fire({
    title: "Courier Booking Details",
    html: `
        <div class="row justify-content-center">
          <div class="col-md-12">
            <form id="courierBookingForm">
              <div class="row">
                <div class="col-md-12">
                  <div class="mb-3 label-left">
                    <label for="supplier" class="form-label">Supplier*</label>
                    <select id="supplier" name="fulfiller" class="form-select">
                      <option value="${fulfiller}">Default (${fulfiller_full})</option>
                      <option value="mandaluyong hub">Mandaluyong Hub</option>
                      <option value="sante valenzuela">Valenzuela Branch</option>
                      <option value="sante cdo">CDO Branch</option>
                    </select>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3 label-left">
                    <label for="courier" class="form-label">Courier *</label>
                    <select id="courier" name="courier" class="form-select">
                      <option value="choose">Select Courier</option>
                      <option value="j&t">J&amp;T</option>
                      <option value="lbc">LBC</option>
                      <option value="gogoxpress">GogoXpress</option>
                    </select>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3 label-left">
                    <label for="tracking_number" class="form-label">Tracking Number *</label>
                    <input type="text" id="tracking_number" name="tracking_number" class="form-control" placeholder="ex: 4152-9532-NVEL">
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3 label-left">
                    <label for="pouch_size" class="form-label">Pouch Size *</label>
                    <select id="pouch_size" name="pouch_size" class="form-select">
                      <option value="choose">Select Pouch Size</option>
                      <option value="sakto pack">Sakto Pack</option>
                      <option value="small">Small</option>
                      <option value="medium">Medium</option>
                      <option value="large">Large</option>
                      <option value="box">Box</option>
                      <option value="others">Others</option>
                    </select>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3 label-left">
                    <label for="pickup_date" class="form-label">Pickup Date *</label>
                    <input type="text" id="datepicker" width="276" name="pickup_date" class="form-control" placeholder="Select a date">
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3 label-left">
                    <label for="actual_sf" class="form-label">Actual Shipping Fee *</label>
                    <input type="text" id="actual_sf" name="actual_shipping_fee" class="form-control" placeholder="ex: 120">
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3" style="text-align: justify; font-size: 11pt;">
                    <label for="is_sf_fulfiller" class="form-label">Paid by Fulfiller *</label>
                    <div class="form-check form-switch" style="font-size: xx-large;">
                      <input class="form-check-input" type="checkbox" id="is_sf_fulfiller" name="paid_by_fulfiller" checked>
                      <label class="form-check-label fullfiller-choice" for="is_sf_fulfiller" style="font-size: 14px!important;">Yes</label>
                    </div>
                  </div>
                </div>
                <div class="col-md-12">
                  <div class="mb-3 label-left">
                    <label for="booking_notes" class="form-label text-left">Notes</label>
                    <textarea id="booking_notes" name="booking_notes" class="form-control" rows="3" placeholder="Booking notes"></textarea>
                  </div>
                </div>
              </div>
            </form>
          </div>
        </div>
      `,
    showCancelButton: true,
    confirmButtonText: "Save",
    cancelButtonText: "Cancel",
    didOpen: () => {
        // Bind the event handler when the popup is opened
        flatpickr("#datepicker", {
          dateFormat: "Y-m-d", // Date format (e.g., "YYYY-MM-DD")
          altInput: true, // Show the date in an alternative input field
          altFormat: "F j, Y", // Format for the alternative input field (e.g., "January 1, 2022")
          enableTime: false, // Enable time selection (set to true if you need time selection)
          // Additional options as needed
      });
        $('#is_sf_fulfiller').click(function() {
          var toggleLabel = $('.fullfiller-choice');
          if ($(this).prop('checked')) {
            toggleLabel.text('Yes');
          } else {
            toggleLabel.text('No');
          }
        });
      }
    // Other options as needed
}).then((result) => {
      if (result.isConfirmed) {
        var formData = $('#courierBookingForm').serialize();
        spinner.addClass("visible");
        backdrop.addClass("visible");
        formData += '&courier_id=' + courierId;
        console.log(formData)
        $.ajax({
          url: courierBooking,
          type: 'POST',
          data: formData,
          headers: {
            "X-CSRFToken": csrf
          },
          success: function(response) {
            spinner.removeClass("visible");
            backdrop.removeClass("visible");

            var row = $(button).closest('tr');
            var dataTable = $('#orders-table').DataTable();
            var rowIndex = dataTable.row(row).index();
            dataTable.row(row).remove().draw();

            console.log("Success:", response);
            Swal.fire({
              title: "Success",
              text: "Booking submitted successfully!",
              icon: "success",
              confirmButtonText: "OK"
            });
          },
          error: function(xhr, status, error) {
            console.error(xhr.responseText);
          }
        });
      } else {
        spinner.removeClass("visible");
        backdrop.removeClass("visible");
        console.log("Booking cancelled");
      }
    });
}

function rejectOrder(button) {
  var courierId = $(button).data('courier-id');
  var spinner = $(".sk-circle");
  var backdrop = $(".backdrop");

  Swal.fire({
      title: 'Are you sure?',
      text: 'You are about to reject this order. This action cannot be undone.',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#11B76B',
      cancelButtonColor: '#E56975',
      confirmButtonText: 'Yes, reject it!',
      cancelButtonText: 'Cancel'
  }).then((result) => {
    if (result.isConfirmed) {
        spinner.addClass("visible");
        backdrop.addClass("visible");
        $.ajax({
            url: rejectOrderUrl,
            type: 'POST',
            data: {
                courier_id: courierId,
                new_status: 'pending'
            },
            headers: {
              "X-CSRFToken": csrf
            },
            success: function(response) {
                Swal.fire(
                    'Rejected!',
                    'The order has been rejected.',
                    'success'
                );
                $('#booking-action-status').html('<span class="badge badge-pending">REJECTED</span>');
                spinner.removeClass("visible");
                backdrop.removeClass("visible");
                console.log("Success:", response);
                
            },
            error: function(xhr, status, error) {
                console.error(xhr.responseText);
                Swal.fire(
                    'Error!',
                    'Failed to reject the order. Please try again later.',
                    'error'
                );
                spinner.removeClass("visible");
                backdrop.removeClass("visible");
            }
        });
    }
});
}

