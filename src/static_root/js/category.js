function showSubcategories(category) {
  const $subcategoryWidget = $("#subcategory-sante");
  console.log('category')
  if (category === 'sante') {
  $subcategoryWidget.show();
} else {
  $subcategoryWidget.hide();
}
}

$(document).ready(function () {
  const $productListContainerBody = $("#product-list-container tbody");
  const $categoryDropdownBtn = $("#category-dropdown button");
  const $categoryDropdownLinks = $("#category-dropdown a");


  $categoryDropdownLinks.click(function (event) {
    event.preventDefault();
    const $this = $(this);
    const selectedCategory = $this.text().trim();
    const isAll = selectedCategory.toLowerCase() === 'all';
    const selectedCategoryId = isAll ? undefined : $this.attr('href').split('=')[1];
    const url = isAll ? '/products/' : `/products/?category=${selectedCategoryId}`;

    console.log('Selected Category:', selectedCategory);
    console.log('Request URL:', url);

    $.ajax({
      url: url,
      type: "GET",
      dataType: "json",
      success: function (products) {
        console.log('Received Products:', products);
        $productListContainerBody.empty();
        $categoryDropdownBtn.text(selectedCategory);

        if (!products.length) {
          $productListContainerBody.append("<tr><th colspan='6'>There are no products in this category yet.</th></tr>");
        } else {
          products.forEach(product => {
            const productImage = product.images && product.images[0] ? product.images[0].image_url : null;
            const imageTag = productImage ? `<img src="${productImage}" alt="${product.name}">` : `<p>No image available</p>`;
            const tableRow = `
              <tr>
                <td>
                    <div class="table-list-info">
                        <a href="#">
                            <div class="table-list-img">${imageTag}</div>
                            <div class="table-list-content">
                                <h6>${product.name}</h6>
                                <span>SKU: #${product.sku}</span>
                            </div>
                        </a>
                    </div>
                </td>
                <td>${product.stock} ${product.stock_unit}</td>
                <td>₱ ${product.price}</td>
                <td>${product.sales_count || 0}</td>
                <td><span class="badge badge-success">Active</span></td>
                <td>
                    <a href="#" class="btn btn-outline-secondary btn-sm rounded-2" data-tooltip="tooltip" title="Details"><i class="far fa-eye"></i></a>
                    <a href="#" class="btn btn-outline-secondary btn-sm rounded-2" data-tooltip="tooltip" title="Edit"><i class="far fa-pen"></i></a>
                    <a href="#" class="btn btn-outline-danger btn-sm rounded-2" data-tooltip="tooltip" title="Delete"><i class="far fa-trash-can"></i></a>
                </td>
              </tr>
            `;
            $productListContainerBody.append(tableRow);
          });
        }
      },
      error: function (error) {
        console.error("Error fetching products:", error);
      }
    });
  });
});
