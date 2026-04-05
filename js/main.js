document.addEventListener("DOMContentLoaded", function () {
  const openSearch = document.getElementById("openSearch");
  const closeSearch = document.getElementById("closeSearch");
  const searchOverlay = document.getElementById("searchOverlay");

  // SEARCH
  openSearch.addEventListener("click", function () {
    searchOverlay.classList.add("active");
  });

  closeSearch.addEventListener("click", function () {
    searchOverlay.classList.remove("active");
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      searchOverlay.classList.remove("active");
    }
  });

  // MOBILE DROPDOWN
  const dropdown = document.querySelector(".dropdown-parent");

  dropdown.addEventListener("click", function (e) {
    if (window.innerWidth < 992) {
      e.preventDefault();
      this.classList.toggle("active");
    }
  });
});
