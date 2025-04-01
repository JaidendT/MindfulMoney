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
