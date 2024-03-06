// $(document).ready(function () {
//     console.log("document ready");
//     $("#sendResetLinkBtn").click(function (e) {
//         e.preventDefault(); // Prevent form submission
//         console.log("button clicked")
//         var email = $("#emailInput").val();
//         var csrfToken = $("input[name='csrfmiddlewaretoken']").val();

//         $.ajax({
//             url: forgotPasswordURL, // Endpoint to send the reset link
//             type: "POST", // HTTP method
//             headers: {
//                 "X-CSRFToken": csrfToken 
//             },
//             data: { email: email }, // Data to send in the request body
//             success: function (response) {
//                 // Disable input box and button
//                 $("#emailInput").prop("disabled", true);
//                 $("#sendResetLinkBtn").text("Reset Link Sent!").prop("disabled", true);
//                 console.log("Reset link sent successfully!");

//                 Swal.fire({
//                     icon: 'success',
//                     title: 'Success!',
//                     text: 'Check your email to reset your password',
//                 });
//             },
//             error: function (error) {
//                 console.error("Error sending reset link:", error);
//             },
//         });
        
//     });
// });