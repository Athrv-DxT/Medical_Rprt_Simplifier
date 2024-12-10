document.getElementById("pdfForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const fileInput = document.getElementById("pdfInput");
    if (!fileInput.files.length) {
        alert("Please select a PDF file.");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const response = await fetch("http://localhost:5000/upload", {
            method: "POST",
            body: formData
        });

        const result = await response.json();
        if (response.ok) {
            document.getElementById("responseMessage").textContent = `
File processed successfully.
Tables saved to: ${result.table_file_path}
Text saved to: ${result.text_file_path}`;
        } else {
            document.getElementById("responseMessage").textContent = result.message;
        }
    } catch (error) {
        document.getElementById("responseMessage").textContent = "Error uploading file.";
        console.error("Upload error:", error);
    }
});
