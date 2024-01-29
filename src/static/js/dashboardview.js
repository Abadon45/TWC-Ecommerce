document.addEventListener('DOMContentLoaded', function () {
    const navLinkEls = document.querySelectorAll('.nav__link');
    const contentDivs = document.querySelectorAll('.content-div');

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
});
