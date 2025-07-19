function checkout(element, promo) {
    let promoType = '';

    const currentPath = window.location.pathname;
    console.log("Current path:", currentPath);
    console.log("Promo:", promo);

    if (currentPath.includes("pf-vw")) {
        promoType = "pf-vw";
    } else if (currentPath.includes("pf-ds")) {
        promoType = "pf-ds";
    }

    const checkoutUrl = `https://www.technowealthcreators.com/eshop/checkout?${promoType}=${promo}`;

    Swal.fire({
        title: "Please wait...",
        text: "We are creating your order.",
        showConfirmButton: false,
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();

            // ⏳ Wait 3 seconds before redirect
            setTimeout(() => {
                window.location.href = checkoutUrl;
            }, 2000);
        },
    });
}
