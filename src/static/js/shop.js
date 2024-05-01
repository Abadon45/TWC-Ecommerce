$(document).ready(function () {
  // Initial setup
  let categories_1, categories_2;
  toggleView("grid");

  // Combine click events and use a single toggleView call
  $("#gridBtn, #listBtn").click(function () {
    toggleView($(this).hasClass("shop-sort-grid") ? "grid" : "list");
  });

  function toggleView(view) {
    const $grid = $(".shop-grid"),
      $list = $(".shop-list"),
      $gridBtn = $("#gridBtn"),
      $listBtn = $("#listBtn");

    $grid.toggle(view === "grid");
    $list.toggle(view !== "grid");
    $gridBtn.toggleClass("active", view === "grid");
    $listBtn.toggleClass("active", view !== "grid");
  }

  var urlParams = new URLSearchParams(window.location.search);
  if (
    !(
      urlParams.has("category_id") &&
      (urlParams.get("category_id") === "chingu" ||
        urlParams.get("category_id") === "mood")
    )
  ) {
    $("#subcategory-sante").show();
  }
});

