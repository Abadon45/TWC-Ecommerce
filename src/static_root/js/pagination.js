// $(document).on("click", ".pagination a", function (event) {
//     event.preventDefault();
//     var page = $(this).attr("href").split("page=")[1];
//     var view = $("#gridBtn").hasClass("active") ? "grid" : "list";
//     fetchProducts(page, view);
// });

// function fetchProducts(page, view) {
//     $.ajax({
//     url: "/shop/?page=" + page,
//     type: "get",
//     dataType: "json",
//     success: function (data) {
//         $("#products-grid").html(data.products_grid_html);
//         $("#products-list").html(data.products_list_html);
//         $(".pagination").html(data.pagination_html);
//         toggleView(view);
//         },
//     });
// }
