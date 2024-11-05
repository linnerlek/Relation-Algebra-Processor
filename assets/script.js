// Toggle for schema information
document.addEventListener("DOMContentLoaded", function () {
  const schemaContainer = document.getElementById("schema-container");

  if (schemaContainer) {
    const schemaSummary = schemaContainer.querySelector("summary");

    schemaSummary.addEventListener("click", function () {
      schemaContainer.open = !schemaContainer.open;
    });
  }
});


// Shows buttons if row is more than 8
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        togglePaginationButtons: function(rowCount) {
            const prevButton = document.getElementById("prev-page-btn");
            const nextButton = document.getElementById("next-page-btn");

            if (rowCount > 8) {
                prevButton.style.display = "inline-block";
                nextButton.style.display = "inline-block";
            } else {
                prevButton.style.display = "none";
                nextButton.style.display = "none";
            }
            return null; 
        }
    }
});

// Wait for the page to load to avoid errors with elements not being found
function observeCytoscapeTree() {
  const cyElement = document.getElementById("cytoscape-tree");

  if (cyElement) {
    // Set up ResizeObserver if cyElement exists
    const resizeObserver = new ResizeObserver((entries) => {
      entries.forEach((entry) => {
        if (window.cy) {
          cy.resize();
          cy.center();
          cy.fit();
        }
      });
    });
    resizeObserver.observe(cyElement);
  } else {
    console.log("Waiting for 'cytoscape-tree' to load...");
    setTimeout(observeCytoscapeTree, 100); // Retry every 100ms
  }
}

// Start checking after DOMContentLoaded
document.addEventListener("DOMContentLoaded", observeCytoscapeTree);

function initializeResizableDivider() {
  const divider = document.getElementById("divider");
  const leftSection = document.getElementById("left-section");
  const rightSection = document.getElementById("right-section");
  const container = document.getElementById("app-container");

  // Check if elements exist
  if (!divider || !leftSection || !rightSection || !container) {
    console.log("Waiting for elements to load...");
    setTimeout(initializeResizableDivider, 100); // Retry every 100ms
    return;
  }

  let isDragging = false;

  // Start dragging when the mouse is down on the divider
  divider.addEventListener("mousedown", (e) => {
    isDragging = true;
    document.body.style.cursor = "ew-resize";
    e.preventDefault();
  });

  // Adjust width on mouse move
  document.addEventListener("mousemove", (e) => {
    if (!isDragging) return;

    const containerWidth = container.offsetWidth;
    const leftWidth = e.clientX; // Mouse position from the left edge

    // Ensure sections don't get too small or too large
    if (leftWidth >= 100 && leftWidth <= containerWidth - 100) {
      leftSection.style.flexBasis = `${leftWidth}px`;
      rightSection.style.flexBasis = `${containerWidth - leftWidth}px`;
    }
  });

  // Stop dragging on mouse up
  document.addEventListener("mouseup", () => {
    isDragging = false;
    document.body.style.cursor = "default";
  });
}

// Start checking for elements after DOMContentLoaded
document.addEventListener("DOMContentLoaded", initializeResizableDivider);
