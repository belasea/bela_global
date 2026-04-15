// Function to bypass cache and reload the page
function clearCacheAndReload() {
  const timestamp = new Date().getTime(); // Create a unique timestamp

  // Append the timestamp to the current page URL to bypass the cache
  const newUrl =
    window.location.origin + window.location.pathname + "?v=" + timestamp;

  // Reload the page with the cache-busted URL
  window.location.href = newUrl;
}

// Event listener for the button
document
  .getElementById("clearCacheButton")
  .addEventListener("click", clearCacheAndReload);

// Function to simulate loading and hide the loader
window.onload = function () {
  // Simulate loading by using setTimeout
  setTimeout(function () {
    document.getElementById("loader").style.display = "none"; // Hide loader
    document.getElementById("main").style.display = "block"; // Show content
  }, 2);
};
