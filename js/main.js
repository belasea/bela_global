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
    // Only the top-level nav-link should toggle the dropdown
    const dropdownToggle = dropdown.querySelector(":scope > .nav-link");
    if (dropdownToggle) {
      dropdownToggle.addEventListener("click", function (e) {
        if (window.innerWidth < 992) {
          e.preventDefault(); // Prevents top-level link navigation on mobile
          e.stopPropagation(); // Don't bubble to parent
          dropdown.classList.toggle("active");
        }
      });
    }
  }

  /**
   * Sticky Navbar Shadow + Jump to Top Button
   */
  const navbarSection = document.querySelector(".navbar-section");
  const jumpToTopBtn = document.getElementById("jumpToTop");

  window.addEventListener("scroll", () => {
    const scrollY = window.scrollY;

    // Add shadow to navbar when scrolled
    if (navbarSection) {
      if (scrollY > 10) {
        navbarSection.classList.add("scrolled");
      } else {
        navbarSection.classList.remove("scrolled");
      }
    }

    // Show/hide jump to top button after scrolling 300px
    if (jumpToTopBtn) {
      if (scrollY > 300) {
        jumpToTopBtn.classList.add("visible");
      } else {
        jumpToTopBtn.classList.remove("visible");
      }
    }
  });

  // Scroll to top on click
  if (jumpToTopBtn) {
    jumpToTopBtn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
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

/* ============================================================
   Product Scroll Area Dragging & Progress Bar
===============================================================*/
const scrollContainer = document.getElementById("scrollContainer");
const scrollProgress = document.getElementById("scrollProgress");

if (scrollContainer) {
  let isDown = false;
  let startX;
  let scrollLeftPos;

  // Mouse drag to scroll
  scrollContainer.addEventListener("mousedown", (e) => {
    isDown = true;
    scrollContainer.style.cursor = "grabbing";
    startX = e.pageX - scrollContainer.offsetLeft;
    scrollLeftPos = scrollContainer.scrollLeft;
  });

  scrollContainer.addEventListener("mouseleave", () => {
    isDown = false;
    scrollContainer.style.cursor = "grab";
  });

  scrollContainer.addEventListener("mouseup", () => {
    isDown = false;
    scrollContainer.style.cursor = "grab";
  });

  scrollContainer.addEventListener("mousemove", (e) => {
    if (!isDown) return;
    e.preventDefault();
    const x = e.pageX - scrollContainer.offsetLeft;
    const walk = (x - startX) * 1.5; // Scroll speed multiplier
    scrollContainer.scrollLeft = scrollLeftPos - walk;
  });

  // Update progress bar
  if (scrollProgress) {
    scrollContainer.addEventListener("scroll", () => {
      const maxScrollLeft = scrollContainer.scrollWidth - scrollContainer.clientWidth;
      if (maxScrollLeft > 0) {
        const scrollPercentage = (scrollContainer.scrollLeft / maxScrollLeft) * 100;
        scrollProgress.style.width = `${scrollPercentage}%`;
      }
    });

    // Initial update
    const initMaxScrollLeft = scrollContainer.scrollWidth - scrollContainer.clientWidth;
    if (initMaxScrollLeft > 0) {
      const initScrollPercentage = (scrollContainer.scrollLeft / initMaxScrollLeft) * 100;
      scrollProgress.style.width = `${initScrollPercentage}%`;
    }
  }

  // Handle active states of Sidebar and Label during scroll
  const groupsData = [
    { id: 'group-new', label: 'NEW', targetNode: '[data-target="group-new"]' },
    { id: 'group-essentials', label: 'ESSENTIALS', targetNode: '[data-target="group-essentials"]' },
    { id: 'group-star', label: 'STAR PRODUCTS', targetNode: '[data-target="group-star"]' }
  ];

  const currentLabelElement = document.getElementById("currentLabel");
  const sidebarLinks = document.querySelectorAll(".sidebar-link");

  const observerOptions = {
    root: scrollContainer,
    rootMargin: "0px",
    threshold: 0.5 // trigger when 50% of the group is visible
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        const matchingGroup = groupsData.find(g => g.id === id);
        
        if (matchingGroup) {
          // Update Label
          if (currentLabelElement) {
            currentLabelElement.textContent = matchingGroup.label;
          }
          
          // Update Sidebar
          sidebarLinks.forEach(link => link.classList.remove("active"));
          const activeLink = document.querySelector(matchingGroup.targetNode);
          if (activeLink) {
            activeLink.classList.add("active");
          }
        }
      }
    });
  }, observerOptions);

  groupsData.forEach(group => {
    const el = document.getElementById(group.id);
    if (el) observer.observe(el);
  });

  // Handle sidebar clicking to slide to appropriate group
  sidebarLinks.forEach(link => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const targetId = link.getAttribute("data-target");
      if (targetId) {
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
          // The container will scroll to the element smoothly
          targetElement.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'start' });
        }
      }
    });
  });
}
