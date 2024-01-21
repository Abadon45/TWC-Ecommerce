$(document).ready(function () {
    // Initial setup
    let categories_1, categories_2;
    toggleView("grid");

    // Combine click events and use a single toggleView call
    $("#gridBtn, #listBtn").click(function () {
        toggleView($(this).hasClass("shop-sort-grid") ? "grid" : "list");
    });

    // Category filtering for Category 1
    $(document).on('click', '.category-1 a', function (event) {
        event.preventDefault();
        const category_id = $(this).data('category-id');
        console.log("Category 1 ID:", category_id);

        $('#loading-spinner').show();
        filterProducts(category_id);
    });

    // Category filtering for Category 2
    $(document).on('click', '.category-2 a', function (event) {
        event.preventDefault();
        const category_id = $(this).data('category-id');
        console.log("Category 2 ID:", category_id);

        $('#loading-spinner').show();
        filterProducts(category_id);
    });



    function filterProducts(category_id) {
        const requestData = { category: category_id };
        const url = (category_id === "all") ? "/shop/" : `/shop/?category_id=${category_id}`;


        console.log("Filtering products with URL:", url);
        console.log("Request Data:", requestData);

        $.ajax({
            url: url,
            type: "GET",
            data: requestData,
            dataType: "json",
            success: function (data) {
                console.log("AJAX Response:", data);
                console.log("Number of products received:", data.products.length);
                console.log("Filtered products:", data.products);
                const productListContainerGrid = $('.shop-grid .row');
                const productListContainerList = $('.shop-list .row');
             
                productListContainerGrid.empty();
                productListContainerList.empty();

                // Iterate through the received products and append them to the container
                if (data.products.length === 0) {
                    // If there are no products, display a message
                    const noProductsMessage = `<div class="col-md-12">There are no products in this category yet.</div>`;
                    productListContainerGrid.append(noProductsMessage);
                    productListContainerList.append(noProductsMessage);
                } else {
                    data.products.forEach(function (product) {
                        console.log("Product Object:", product);
                        const productGridHtml = `
                            <div class="col-md-6 col-lg-4">
                                <div class="product-item">
                                    <div class="product-img">
                                        <span class="type">Trending</span>
                                        <a href="/shop/single/${product.slug}">
                                            <img src="${product.image}" alt="${product.name}" id="product-image">
                                        </a>
                                        <div class="product-action-wrap">
                                            <div class="product-action">
                                                <a href="#" data-bs-toggle="modal" data-bs-target="#quickview" data-tooltip="tooltip" title="Quick View"><i class="far fa-eye"></i></a>
                                                <a href="#" data-tooltip="tooltip" title="Add To Wishlist"><i class="far fa-heart"></i></a>
                                                <a href="#" data-tooltip="tooltip" title="Add To Compare"><i class="far fa-arrows-repeat"></i></a>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="product-content">
                                        <h3 class="product-title"><a href="/shop/single/${product.slug}">${product.name}</a></h3>
                                        <div class="product-rate">
                                            <i class="fas fa-star"></i>
                                            <i class="fas fa-star"></i>
                                            <i class="fas fa-star"></i>
                                            <i class="fas fa-star"></i>
                                            <i class="far fa-star"></i>
                                        </div>
                                        <div class="product-bottom">
                                            <div class="product-price">
                                                <span>${product.price} Php</span>
                                            </div>
                                            <button data-product="${product.id}" data-action="add" type="button" class="product-cart-btn add-to-cart-btn update-cart">
                                                <i class="far fa-shopping-bag"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>`;

                        productListContainerGrid.append(productGridHtml);

                        const productListHtml = `
                            <div class="col-md-12">
                                <div class="product-item">
                                    <div class="product-img">
                                        <span class="type">Trending</span>
                                        <a href="/shop/single/${product.slug}">
                                            <img src="${product.image}" alt="${product.name}" id="product-image">
                                        </a>
                                        <div class="product-action-wrap">
                                            <div class="product-action">
                                                <a href="#" data-bs-toggle="modal" data-bs-target="#quickview" data-tooltip="tooltip" title="Quick View"><i class="far fa-eye"></i></a>
                                                <a href="#" data-tooltip="tooltip" title="Add To Wishlist"><i class="far fa-heart"></i></a>
                                                <a href="#" data-tooltip="tooltip" title="Add To Compare"><i class="far fa-arrows-repeat"></i></a>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="product-content">
                                        <h3 class="product-title"><a href="/shop/single/${product.slug}">${product.name}</a></h3>
                                        <div class="product-rate">
                                            <i class="fas fa-star"></i>
                                            <i class="fas fa-star"></i>
                                            <i class="fas fa-star"></i>
                                            <i class="fas fa-star"></i>
                                            <i class="far fa-star"></i>
                                        </div>
                                        <p>${product.description}</p>
                                        <div class="product-bottom">
                                            <div class="product-price">
                                                <span>${product.price} Php</span>
                                            </div>
                                            <button data-product="${product.id}" data-action="add" type="button" class="product-cart-btn add-to-cart-btn update-cart">
                                                <i class="far fa-shopping-bag"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>`;

                        productListContainerList.append(productListHtml);
                        console.log("Product Object:", product);
                    });
                    console.log("Appended products to container:", data.products);
                }
            },
            error: function (xhr, status, error) {
                console.error("Error fetching filtered products - Status:", status, "Error:", error);
                if (xhr.readyState == 4) {
                    console.log("XHR Status:", xhr.status);
                    console.log("XHR Status Text:", xhr.statusText);
                    console.log("Response Text:", xhr.responseText);
                } else if (xhr.readyState == 0) {
                    console.log("XHR Status: 0 (Request not initialized)");
                } else {
                    console.log("XHR Status:", xhr.status);
                }
            }
        });
    }

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
});
