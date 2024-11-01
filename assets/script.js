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
