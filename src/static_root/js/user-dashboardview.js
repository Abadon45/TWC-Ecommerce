$(document).ready(function () {

  const dashboardTab = document.querySelector(".dashboard-tab");
  const profileTab = document.querySelector(".profile-tab");
  const addressTab = document.querySelector(".address-tab");
  const trackOrderTab = document.querySelector(".track-order-tab");


  dashboardTab.addEventListener("click", function (event) {
    event.preventDefault();
    const currentPath = window.location.pathname;
    let newPath = currentPath.replace(/\/[^\/]*$/, "/");
    history.pushState({}, "", newPath);
  });

  profileTab.addEventListener("click", function (event) {
    event.preventDefault();
    history.pushState({}, "", "/profile");
  });

  addressTab.addEventListener("click", function (event) {
    event.preventDefault();
    history.pushState({}, "", "/address");
  });

  trackOrderTab.addEventListener("click", function (event) {
    event.preventDefault();
    history.pushState({}, "", "/track-order");
  });

  
});
