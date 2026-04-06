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

const circle = document.getElementById("spinnerCircle");
const textElement = document.getElementById("changingText");
const imageElements = document.querySelectorAll(".dynamic-img");

const radius = circle.r.baseVal.value;
const circumference = radius * 2 * Math.PI;
circle.style.strokeDasharray = `${circumference} ${circumference}`;

let progress = 0;
let isStateOne = true; // Toggle tracker

function updateDesign() {
  progress += 1;
  const offset = circumference - (progress / 100) * circumference;
  circle.style.strokeDashoffset = offset;

  if (progress >= 100) {
    progress = 0;
    isStateOne = !isStateOne; // Switch state

    // Fade out
    textElement.style.opacity = 0;
    imageElements.forEach((img) => (img.style.opacity = 0));

    setTimeout(() => {
      // 1. Swap Text from Data Attributes
      textElement.innerText = isStateOne
        ? textElement.getAttribute("data-text-one")
        : textElement.getAttribute("data-text-two");

      // 2. Swap Images
      imageElements.forEach((img) => {
        const currentSrc = img.src;
        const altSrc = img.getAttribute("data-alt-src");

        // Swap the actual src with the one stored in data-alt-src
        img.src = altSrc;
        img.setAttribute("data-alt-src", currentSrc);
      });

      // Fade back in
      textElement.style.opacity = 1;
      imageElements.forEach((img) => (img.style.opacity = 1));
    }, 400);
  }
}

setInterval(updateDesign, 50);
