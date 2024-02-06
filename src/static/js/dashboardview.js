$(document).ready(function() {
    const navLinkEls = $('.nav__link');
    const contentDivs = $('.content-div');

    function handleNavLinkClick(index, linkElement) {
        if (!linkElement.hasClass('active')) {
            const activeNavLink = $('.nav__link.active');
            if (activeNavLink) {
                activeNavLink.removeClass('active');
            }
            linkElement.addClass('active');

            // Hide all content divs
            contentDivs.attr('hidden', true);

            // Show the corresponding content div
            contentDivs.eq(index).removeAttr('hidden');
        }
    }

    navLinkEls.each(function(index) {
        $(this).on('click', function() {
            handleNavLinkClick(index, $(this));
        });
    });
    $("#copyButton").click(function(){
        /* Get the text field */
        var copyText = $("#copyInput");
    
        /* Select the text field */
        copyText.select();
    
        /* Copy the text inside the text field */
        document.execCommand("copy");
    
        /* Alert the copied text */
        $(this).text("Copied!!");
      });

});