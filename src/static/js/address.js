
$(document).ready(function () {

    $.ajax({
        url: checkoutUrl,
        type: "GET",
        dataType: "json",
        success: function (data) {
            const isAuthenticated = data.isAuthenticated;
            // Now you can use isAuthenticated in your JavaScript logic
            console.log("isAuthenticated:", isAuthenticated);
        },
        error: function (error) {
            console.error("Error fetching data:", error);
        }
    });


    // Initialize an object to store input details
    var userDetails = {
        first_name: "",
        last_name: "",
        email: ""
    };

    function generateRandomString(length) {
        var result = '';
        var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        var charactersLength = characters.length;
        for (var i = 0; i < length; i++) {
            result += characters.charAt(Math.floor(Math.random() * charactersLength));
        }
        return result;
    }

    // Function to update userDetails object
    function updateUserData() {
        userDetails.first_name = $('#inputFirstName').val().charAt(0);
        userDetails.last_name = $('#inputLastName').val();
        userDetails.email = $('#inputEmail').val();

        var randomString = generateRandomString(4);

        var userName = userDetails.first_name + userDetails.last_name + randomString;

        console.log(userName)
    }

    // Event listeners to capture input changes using jQuery
    $('#inputFirstName').on('input', updateUserData);
    $('#inputLastName').on('input', updateUserData);
    $('#inputEmail').on('input', updateUserData);

    
    function createAccountAndProceed() {
        
        // Check if the customer is authenticated
        if (isAuthenticated) {
            // Customer is authenticated, proceed to checkout-complete
            window.location.href = checkoutComplateUrl;
        } else {
            // Customer is not authenticated, create an account
            var userName = userDetails.first_name + userDetails.last_name + generateRandomString(4);
            var userEmail = userDetails.email;

            // Perform an AJAX request to create a user account
            $.ajax({
                url: "{% url 'create_user_account' %}",  // Replace with your URL for creating a user account
                method: "POST",
                data: { 
                    // Pass necessary data for user creation, e.g., userName, userDetails.email, etc.
                    username: userName,
                    email: userEmail,
                    // ... other data
                },
                success: function (response) {
                    // Handle the success response, e.g., show a success message

                    // Proceed to checkout-complete after creating the account
                    window.location.href = "{% url 'cart:checkout_complete' %}";
                },
                error: function (error) {
                    // Handle the error, e.g., show an error message
                }
            });
        }
    }
    
    // Event listener for the checkout button
    $('#checkoutButton').on('click', function () {
        // Update user data before proceeding
        updateUserData();

        // Call the function to create an account or proceed to checkout-complete
        createAccountAndProceed();
    });

    
});