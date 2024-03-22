$(document).ready(function () {
  const getAddressDetailsUrl = "/get-address-details/";
  const deleteAddressUrl = "/delete-address/";
  const updateAddressUrl = "/update-address/";

  const navLinkEls = $(".nav__link");
  const contentDivs = $(".content-div");

  const baseURL = window.location.origin;

  const tabPaths = {
    dashboard: "/",
    profile: "/profile",
    address: "/address",
    "track-order": "/track-order",
  };

  const dashboardTab = document.querySelector(".dashboard-tab");
  const profileTab = document.querySelector(".profile-tab");
  const addressTab = document.querySelector(".address-tab");
  const trackOrderTab = document.querySelector(".track-order-tab");

  var spinner = $(".sk-circle");
  var backdrop = $(".backdrop");

  // Function to update the URL dynamically based on the selected tab
  function updateURL(tab) {
    const tabPath = tabPaths[tab];
    const newURL = baseURL + tabPath;
    history.pushState({}, "", newURL);
  }

  dashboardTab.addEventListener("click", function (event) {
    event.preventDefault();
    const currentPath = window.location.pathname;
    let newPath = currentPath.replace(/\/[^\/]*$/, "/");
    history.pushState({}, "", newPath);
  });

  profileTab.addEventListener("click", function (event) {
    event.preventDefault();
    history.pushState({}, "", "/profile");
  });

  addressTab.addEventListener("click", function (event) {
    event.preventDefault();
    history.pushState({}, "", "/address");
  });

  trackOrderTab.addEventListener("click", function (event) {
    event.preventDefault();
    history.pushState({}, "", "/track-order");
  });

  // Event listeners for tab clicks
  $(".dashboard-tab").on("click", function (event) {
    event.preventDefault();
    const tab = "dashboard";
    updateURL(tab);
    showContent(tab);
  });

  $(".profile-tab").on("click", function (event) {
    event.preventDefault();
    const tab = "profile";
    updateURL(tab);
    showContent(tab);
  });

  $(".address-tab").on("click", function (event) {
    event.preventDefault();
    const tab = "address";
    updateURL(tab);
    showContent(tab);
  });

  $(".track-order-tab").on("click", function (event) {
    event.preventDefault();
    const tab = "track-order";
    updateURL(tab);
    showContent(tab);
  });

  // Function to show content based on tab selection
  function showContent(tab) {
    // Your existing showContent function logic here
  }

  // Load initial content based on the URL
  function loadInitialContent() {
    const currentPath = window.location.pathname;
    const tab = Object.keys(tabPaths).find(
      (key) => tabPaths[key] === currentPath
    );
    showContent(tab);
  }
  loadInitialContent();

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

  // If there's an active index and the tab matches the active index, append the tab URL to the base URL
  if (activeIndex !== null && tabPaths[activeIndex]) {
    const tab = activeIndex;
    updateURL(tab);
}

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

  $(".addAddressBtn").click(function () {
    $(".addressList").hide();
    $(".addAddressDiv").removeAttr("hidden");
  });

  $(".addressListBtn").click(function () {
    $(".addressList").show();
    $(".addAddressDiv").attr("hidden", true);
  });

  $("#orderDetailsModal").on("show.bs.modal", function (event) {
    var modal = $(this);
    var button = event.relatedTarget;
    var orderId = $(button).data("order-id");

    modal.find(".modal-body .alert").remove();
    modal.find(".modal-content").addClass("loading");

    //Load Spinner
    spinner.addClass("visible");
    backdrop.addClass("visible");

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
        spinner.removeClass("visible");
        backdrop.removeClass("visible");

        modal.find(".modal-content").removeClass("loading");

        // Show the modal after data is loaded
        modal.modal("show");
      })
      .fail(function (jqXHR, textStatus, errorThrown) {
        console.error("Error fetching order details:", textStatus, errorThrown);
        // Example: Display error within the modal
        modal
          .find(".modal-body")
          .prepend(
            '<div class="alert alert-danger">Error fetching order details. Please try again later.</div>'
          );

        // Hide the spinner if there's an error
        spinner.removeClass("visible");
        backdrop.removeClass("visible");

        modal.find(".modal-content").removeClass("loading");
      });
  });

  //ORDER PROGRESS BAR
  function updateProgressBar(status) {
    console.log("Updating progress bar for status:", status);
    // Reset all steps to their default state;

    // Remove existing classes and add appropriate classes based on order status
    switch (status) {
      case "processed":
        $("#step1").removeClass("text-muted").addClass("active");
        $("#step2, #step3, #step4")
          .removeClass("active")
          .addClass("text-muted");
        break;
      case "prepared":
        $("#step1, #step2").removeClass("text-muted").addClass("active");
        $("#step3, #step4").removeClass("active").addClass("text-muted");
        break;
      case "shipped":
        $("#step1, #step2, #step3")
          .removeClass("text-muted")
          .addClass("active");
        $("#step4").removeClass("active").addClass("text-muted");
        break;
      case "received":
        $(".step0").removeClass("text-muted").addClass("active");
        break;
      default:
        break;
    }
  }

  //DELETE ADDRESS

  $(".delete-address").click(function (e) {
    e.preventDefault();
    var addressId = $(this).data("address-id");
    deleteAddress(addressId);
  });

  function deleteAddress(addressId) {
    $.ajax({
      type: "POST",
      url: deleteAddressUrl,
      data: {
        address_id: addressId,
        csrfmiddlewaretoken: csrf,
      },
      success: function (response) {
        $("#address-" + addressId).remove();
      },
      error: function (xhr, textStatus, errorThrown) {
        console.log("Error:", errorThrown);
      },
    });
  }

  //EDIT ADDRESS

  $(".edit-address").click(function (e) {
    e.preventDefault();
    var addressId = $(this).data("address-id");
    fetchAddressDetails(addressId);
    spinner.addClass("visible");
    backdrop.addClass("visible");
  });

  function updateSelectValueAndTriggerChange(selectId, selectedValue) {
    $(selectId).val(selectedValue).trigger("change");
  }

  function fetchAddressDetails(addressId) {
    $.ajax({
      type: "GET",
      url: getAddressDetailsUrl,
      data: {
        address_id: addressId,
      },
      success: function (response) {
        // Populate the form fields in the modal with the retrieved address details
        $(".inputFirstName").val(response.address.first_name);
        $(".inputLastName").val(response.address.last_name);
        $(".inputEmail").val(response.address.email);
        $(".inputPhone").val(response.address.phone);
        $(".inputLine1").val(response.address.line1);
        $(".inputLine2").val(response.address.line2);
        $(".inputPostcode").val(response.address.postcode);
        $(".inputMessage").val(response.address.message);

        updateSelectValueAndTriggerChange(
          ".regionDropdown",
          response.address.region
        );
        updateSelectValueAndTriggerChange(
          ".provinceDropdown",
          response.address.province
        );
        updateSelectValueAndTriggerChange(
          ".cityDropdown",
          response.address.city
        );
        updateSelectValueAndTriggerChange(
          ".barangayDropdown",
          response.address.barangay
        );

        spinner.removeClass("visible");
        backdrop.removeClass("visible");

        $("#changeAddressModal").modal("hide");
        $("#editAddressModal").modal("show");
      },
      error: function (xhr, textStatus, errorThrown) {
        console.log("Error:", errorThrown);
      },
    });
  }

  // Handle form submission for updating the address
  $("#editAddressForm").submit(function (e) {
    e.preventDefault();
    saveAddressChanges();
  });

  function updateTableRow(addressId, newData) {
    var row = $("#address-" + addressId);
    row
      .find(".table-list-code")
      .text(newData.first_name + " " + newData.last_name);
    row
      .find("td:nth-child(2)")
      .text(newData.line1 + ", " + newData.city + ", " + newData.postcode);
    row.find("td:nth-child(3)").text(newData.phone);
  }

  // Function to save address changes
  function saveAddressChanges(formData) {
    formData.append("address_id", $("#editAddressModal").data("address-id")); // Append the address ID to the form data
    formData.append("csrfmiddlewaretoken", csrf); // Add CSRF token
    $.ajax({
      type: "POST",
      url: updateAddressUrl,
      data: formData,
      processData: false, // Ensure formData is not processed as a query string
      contentType: false, // Ensure correct content type for formData
      success: function (response) {
        console.log(response);
        // Close the modal
        $("#editAddressModal").modal("hide");

        updateTableRow(response.address_id, response.new_data);
      },
      error: function (xhr, textStatus, errorThrown) {
        console.error("Error:", errorThrown);
        // Handle error
      },
    });
  }

  // Event listener for the "Save changes" button click
  $("#saveAddressChanges").click(function () {
    var addressId = $("#editAddressModal").data("address-id"); // Retrieve the address ID from modal data attribute
    var formData = new FormData($("#editAddressForm")[0]); // Create FormData object from form
    formData.append("address_id", addressId); // Append the address ID to the form data
    formData.append("csrfmiddlewaretoken", csrf); // Append the CSRF token to the form data
    saveAddressChanges(formData);
  });

  // Update pagination click event handler
  $(document).on("click", ".pagination a", function (event) {
    event.preventDefault();
    var page = $(this).data("page");
    spinner.addClass("visible");
    backdrop.addClass("visible");
    fetchOrders(page);
  });

  // AJAX function to fetch orders
  function fetchOrders(page) {
    console.log("Fetching orders for page:", page);
    console.log("Current URL:", window.location.href);
    console.log("Dashboard URL:", dashboardURL);

    $.ajax({
      url: dashboardURL,
      type: "GET",
      data: { page: page },
      dataType: "json",
      success: function (data) {
        console.log("AJAX Response:", data);
        console.log("Pagination HTML:", data.pagination_html);
        $(".pagination").html(data.pagination_html);
        // Update Order List
        const orderListContainer = $(".order-list");
        orderListContainer.empty(); // Clear existing items

        $.each(data.orders, function (index, order) {
          const newListItem = createOrderItem(order); // Create new list items
          orderListContainer.append(newListItem);
        });
        spinner.removeClass("visible");
        backdrop.removeClass("visible");
      },
      error: function (xhr, status, error) {
        console.error("AJAX error:", error);
        console.error("Request Status:", status);
        console.error("XMLHttpRequest:", xhr);
      },
    });
  }
  function createOrderItem(order) {
    const date = new Date(order.created_at);
    const options = {
      month: "long",
      day: "numeric",
      year: "numeric",
      hour: "numeric",
      minute: "numeric",
      hour12: true,
    }; // Customize options

    const formattedDate = date.toLocaleString("en-US", options);
    return $(`
      <tr>
        <td><span class="table-list-code">${order.order_id}</span></td>
        <td>${formattedDate}</td>
        <td>₱${order.get_cart_items}</td>
        <td><span id="orderStatus" class="badge badge-${order.status.toLowerCase()}">${order.status.toUpperCase()}</span></td>
        <td>  
          <button type="button" 
                  class="btn btn-outline-secondary btn-sm rounded-2" 
                  data-bs-toggle="modal" 
                  data-bs-target="#orderDetailsModal" 
                  data-order-id="${order.order_id}"
                  data-order-date="${order.created_at}"
                  data-order-total="${order.total_amount}"
                  data-order-status="${order.status}"
                  data-tooltip="Order Details" 
                  title="Details">
            <i class="far fa-eye"></i>
          </button>      
        </td>
      </tr>
    `);
  }
});
