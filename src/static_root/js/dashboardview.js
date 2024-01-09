document.addEventListener('DOMContentLoaded', function () {
    const navLinkEls = document.querySelectorAll('.nav__link');
    const contentDivs = document.querySelectorAll('.content-div');
    // const addProductBtn = document.getElementById('addProductBtn');
    // const addProductLink = document.getElementById('addProductLink');
    // const productBtn = document.getElementById('ProductBtn');
    // const productsLink = document.getElementById('productsLink'); 

    function handleNavLinkClick(index, linkElement) {
        if (!linkElement.classList.contains('active')) {
            const activeNavLink = document.querySelector('.nav__link.active');
            if (activeNavLink) {
                activeNavLink.classList.remove('active');
            }
            linkElement.classList.add('active');

            // Hide all content divs
            contentDivs.forEach((div) => {
                div.setAttribute('hidden', true);
            });

            // Show the corresponding content div
            contentDivs[index].removeAttribute('hidden');
        }
    }

    navLinkEls.forEach((navLinkEl, index) => {
        navLinkEl.addEventListener('click', () => {
            handleNavLinkClick(index, navLinkEl);
        });
    });

    // // Add event listener for the "Add Product" button
    // addProductBtn.addEventListener('click', () => {
    //     handleNavLinkClick(3, addProductLink);
    //     // Trigger a click event on the "Add New Product" link
    //     addProductLink.click();
    // });

    // // Event listener for the "ProductBtn"
    // productBtn.addEventListener('click', () => {
    //     handleNavLinkClick(2, productsLink);
    //     // Trigger a click event on the "Products" link
    //     productsLink.click();
    // });
});
