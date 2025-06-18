/******************** HOME PAGE ********************/
document.addEventListener("DOMContentLoaded", () => {
    const dropArea = document.getElementById("drop-area");
    const fileInput = document.getElementById("fileInput");

    // Drag & Drop Events
    dropArea.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropArea.style.backgroundColor = "rgba(255, 255, 255, 0.2)";
    });

    dropArea.addEventListener("dragleave", () => {
        dropArea.style.backgroundColor = "rgba(255, 255, 255, 0.1)";
    });

    dropArea.addEventListener("drop", (e) => {
        e.preventDefault();
        dropArea.style.backgroundColor = "rgba(255, 255, 255, 0.1)";
        const file = e.dataTransfer.files[0];
        if (file) handleFile(file);
    });

    // File Input Event
    fileInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (file) handleFile(file);
    });

    // Uploading CSV file funtionality
    function handleFile(file) {
        if (file.type !== "text/csv") {
            alert("Please upload a valid CSV file.");
            return;
        }

        let formData = new FormData();
        formData.append("file", file);

        fetch("/upload", {
            method: "POST",
            body: formData
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error("File upload failed.");
            }
        })
        .then(data => {
            if (data.message) {  // Check if there's a message, not a success flag
                alert(data.message);  // Show message without "Error: "
            } else {
                alert("An unexpected error occurred.");
            }
        })        
        .catch(error => {
            console.error("Error:", error);
            alert("An error occurred while uploading the file.");
        });
    }
});

/******************** TRANSACTIONS PAGE ********************/
// filter transactions by date button
function filterByDate() {
    const startDate = document.getElementById("start-date").value;
    const endDate = document.getElementById("end-date").value;

    if (startDate && endDate) {
        const newUrl = `${window.location.pathname}?start_date=${startDate}&end_date=${endDate}`;
        window.location.href = newUrl;
    } else {
        alert("Please select both start and end dates.");
    }
}

// changing colour of rows with changed categories
function markRowAsChanged(selectElement) {
    const row = selectElement.closest("tr");
    const originalCategory = row.getAttribute("data-original-category");
    const selectedCategory = selectElement.value;

    if (originalCategory !== selectedCategory) {
        row.classList.add("changed-row");
        row.setAttribute("data-changed", "true");
    } else {
        row.classList.remove("changed-row");
        row.removeAttribute("data-changed");
    }
}

// save category changes to database
function saveCategoryChanges() {
    const changedRows = document.querySelectorAll("tr[data-changed='true']");
    if (changedRows.length === 0) {
        alert("No changes to save.");
        return;
    }

    const updates = Array.from(changedRows).map(row => {
        const nr = parseInt(row.getAttribute("data-transaction-id"));
        const category = row.querySelector("select.category-select").value;
        return { nr, category };
    });

    console.log("Sending updates:", updates);
    fetch("/update-transactions", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(updates)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to save changes");
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert("Changes saved successfully!");
            // Reset changed markers
            changedRows.forEach(row => {
                const select = row.querySelector("select.category-select");
                row.setAttribute("data-original-category", select.value);
                row.classList.remove("changed-row");
                row.removeAttribute("data-changed");
            });
        } else {
            alert("Failed to save some or all changes.");
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("An error occurred while saving changes.");
    });
}


/******************* BUDGETS PAGE  ********************/
// Function to calculate the total for each section
function calculateTotal(sectionClass) {
    let total = 0;

    // Select all input fields within the given section (income, expenses, etc.)
    const inputs = document.querySelectorAll(`${sectionClass} .budget-input`);

    // Sum up the values of the input fields
    inputs.forEach(input => {
        const value = parseFloat(input.value) || 0; // Handle non-numeric inputs (NaN)
        total += value;
    });

    // Update the total amount in the corresponding total display
    const totalAmountElement = document.querySelector(`${sectionClass} .total-amount`);
    if (totalAmountElement) {
        totalAmountElement.textContent = total.toFixed(2); // Format to 2 decimal places
    }
}

// Function to trigger total calculation whenever an input value changes
function setupEventListeners() {
    // Add event listeners to all budget input fields
    const allInputs = document.querySelectorAll('.budget-input');
    allInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Get the parent section element that the input belongs to
            const section = input.closest('.budget-box'); // Get the closest budget-box (parent container)

            // Get the section's specific class (e.g., .income, .expense, etc.)
            const sectionClass = `.${section.classList[1]}`;

            // Calculate the total for this section
            calculateTotal(sectionClass);
        });
    });
}

// Run the setup function once the page loads
document.addEventListener('DOMContentLoaded', setupEventListeners);

