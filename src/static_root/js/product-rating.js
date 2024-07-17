// $(document).ready(function () {
//     $('.product-rate .fa-star').on('click', function () {
//         var $this = $(this);
//         var ratingIndex = $this.data('index');
//         var productId = $this.closest('.product-rate').data('product-id');
//         var $productRate = $this.closest('.product-rate');

//         updateStarRating($productRate, ratingIndex);

//         if (productId !== undefined) {
//             $.ajax({
//                 url: "{% url 'products:rate_product' 0 %}".replace('0', productId),
//                 type: 'POST',
//                 data: {
//                     'score': ratingIndex,
//                     'csrfmiddlewaretoken': '{{ csrf_token }}'
//                 },
//                 success: function (response) {
//                     console.log('Rating submitted successfully');
//                 },
//                 error: function (response) {
//                     console.log('Error in submitting rating');
//                 }
//             });
//         }
//     });

//     function updateStarRating($ratingElement, ratingIndex) {
//         $ratingElement.find('.fa-star').each(function () {
//             var $star = $(this);
//             var starIndex = parseInt($star.data('index'));
//             if (starIndex <= ratingIndex) {
//                 $star.removeClass('far').addClass('fas');
//             } else {
//                 $star.removeClass('fas').addClass('far');
//             }
//         });
//     }
// });