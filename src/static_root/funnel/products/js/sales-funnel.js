function checkout(element, promo) {
    let promoType = '';

    const currentPath = window.location.pathname;
    const hostname = window.location.hostname; // e.g., john.technowealthcreators.com

    console.log("Current path:", currentPath);
    console.log("Promo:", promo);
    console.log("Hostname:", hostname);

    // Extract subdomain (username)
    const hostParts = hostname.split('.');
    const username = hostParts.length > 2 ? hostParts[0] : null; // only if there's a subdomain

    if (currentPath.includes("pf-vw")) {
        promoType = "pf-vw";
    } else if (currentPath.includes("pf-ds")) {
        promoType = "pf-ds";
    }

    // Fallback if subdomain is not available
    const refParam = username ? `?ref=${username}` : '';

    // Handle proper query param concatenation (avoid double '?')
    const checkoutUrl = `https://www.technowealthcreators.com/eshop/checkout?${promoType}=${promo}${refParam && `&${refParam.slice(1)}`}`;

    Swal.fire({
        title: "Please wait...",
        text: "We are creating your order.",
        showConfirmButton: false,
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
            setTimeout(() => {
                window.location.href = checkoutUrl;
            }, 2000);
        },
    });
}
