/**
 * UI Controller for BellaGlobal
 * Handles Search Overlay, Mobile Navigation, and Interactive Product Scrolling.
 */

document.addEventListener("DOMContentLoaded", function () {
  // Elements for Search Functionality
  const openSearch = document.getElementById("openSearch");
  const closeSearch = document.getElementById("closeSearch");
  const searchOverlay = document.getElementById("searchOverlay");

  /**
   * Toggles the Search Overlay visibility.
   * Adds/Removes the 'active' class to trigger CSS transitions.
   */
  if (openSearch && searchOverlay) {
    openSearch.addEventListener("click", () =>
      searchOverlay.classList.add("active"),
    );
  }

  if (closeSearch && searchOverlay) {
    closeSearch.addEventListener("click", () =>
      searchOverlay.classList.remove("active"),
    );
  }

  /**
   * Accessibility: Closes the search overlay when the 'Escape' key is pressed.
   */
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && searchOverlay) {
      searchOverlay.classList.remove("active");
    }
  });

  /**
   * Mobile Navigation Logic:
   * Handles dropdown toggling specifically for touch/small-screen devices (under 992px).
   */
  const dropdown = document.querySelector(".dropdown-parent");
  if (dropdown) {
    dropdown.addEventListener("click", function (e) {
      if (window.innerWidth < 992) {
        e.preventDefault(); // Prevents top-level link navigation on mobile
        this.classList.toggle("active");
      }
    });
  }
});

/* ============================================================
skincare-section
===============================================================*/
const section = document.getElementById("skincare-section");
const circle = document.getElementById("spinner-path");
const radius = circle.r.baseVal.value;
const circumference = radius * 2 * Math.PI;

// Initialize Circle
circle.style.strokeDasharray = `${circumference} ${circumference}`;
circle.style.strokeDashoffset = circumference;

function runCycle() {
  // 1. Reset Circle Progress instantly
  circle.style.transition = "none";
  circle.style.strokeDashoffset = circumference;

  // 2. Trigger the Visual Switch (Text & Images)
  section.classList.toggle("state-switched");

  // 3. Restart Circle Progress after a tiny frame gap
  setTimeout(() => {
    circle.style.transition = "stroke-dashoffset 4.9s linear";
    circle.style.strokeDashoffset = 0;
  }, 50);
}

// First initialization
setTimeout(() => {
  circle.style.transition = "stroke-dashoffset 4.9s linear";
  circle.style.strokeDashoffset = 0;
}, 100);

// Set the loop (5 seconds total cycle)
setInterval(runCycle, 5000);
