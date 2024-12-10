document.addEventListener('DOMContentLoaded', () => {
    const elements = document.querySelectorAll('.br');
    elements.forEach(element => {
        // Add the 'animate' class to start the transition
        element.classList.add('animate');
    });
});

const images = [
    "images/mrs1.jpeg",
    "images/mrs2.jpeg",
    "images/mrs3.jpeg",
    "images/mrs4.jpeg"
];

const imageElement = document.getElementById('backgroundImage');
let currentIndex = 0;

function changeImage() {
    // Fade out effect
    imageElement.style.opacity = 0;

    setTimeout(() => {
        // Update image and fade in
        currentIndex = (currentIndex + 1) % images.length;
        imageElement.style.backgroundImage = `url(${images[currentIndex]})`;
        imageElement.style.opacity = 1;
    }, 500); // Delay for fade out to complete
}

// Change image every 2 seconds
setInterval(changeImage, 2000);

// Backend logic for file upload
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
            // Format and display success message
            const { diagnosis, table_file_path, text_file_path } = result;
            const diagnosisText = diagnosis.join('\n'); // Join array into a string with line breaks

            document.getElementById("responseMessage").textContent = `
File processed successfully.
Diagnosis: 
${diagnosisText}
Tables saved to: ${table_file_path}
Text saved to: ${text_file_path}`;
        } else {
            // Display error message if something went wrong
            document.getElementById("responseMessage").textContent = result.message;
        }
    } catch (error) {
        // Display an error if the fetch call fails
        document.getElementById("responseMessage").textContent = "Error uploading file.";
        console.error("Upload error:", error);
    }
});

