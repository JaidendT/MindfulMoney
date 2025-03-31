document.addEventListener("DOMContentLoaded", () => {
    const dropArea = document.getElementById("drop-area");
    const fileInput = document.getElementById("fileInput");

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
        handleFile(file);
    });

    fileInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        handleFile(file);
    });

    function handleFile(file) {
        if (file && file.type === "text/csv") {
            alert(`File uploaded: ${file.name}`);
            // You can add logic here to send the file to the server
        } else {
            alert("Please upload a valid CSV file.");
        }
    }
});
