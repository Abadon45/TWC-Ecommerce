function saveScrollPosition() {
    sessionStorage.setItem('shopScrollPosition', $(window).scrollTop());
}

function restoreScrollPosition() {
    var scrollPosition = sessionStorage.getItem('shopScrollPosition');
    if (scrollPosition !== null) {
        $(window).scrollTop(parseInt(scrollPosition));
    }
}

$(window).on('beforeunload', saveScrollPosition);
$(window).on('load', restoreScrollPosition);