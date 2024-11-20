document.getElementById('uploadForm').addEventListener('submit', async (event) => {
    event.preventDefault();

    // Retrieve file input
    const fileInput = document.getElementById('fileInput');
    // Retrieve transformation type
    const transformation = document.getElementById('transformation').value;

    // Collect parameter values, defaulting to null if not provided
    const params = {
        scale_factor: parseFloat(document.getElementById('scaleInput').value) || 1,
        angle: parseFloat(document.getElementById('angleInput').value) || 0,
        offset_x: parseInt(document.getElementById('offsetXInput').value) || 0,
        offset_y: parseInt(document.getElementById('offsetYInput').value) || 0,
        shear_x: parseFloat(document.getElementById('shearXInput')?.value) || 0,
        shear_y: parseFloat(document.getElementById('shearYInput')?.value) || 0
    };
    
    

    // Prepare form data to send to the server
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('transformation', transformation);
    formData.append('params', JSON.stringify(params)); // Serialize params to JSON format

    try {
        // Send the form data to the server via a POST request
        const response = await fetch('http://127.0.0.1:5000/upload', {
            method: 'POST',
            body: formData
        });

        // Check if the response is ok, if not throw an error
        if (!response.ok) {
            throw new Error(await response.text());
        }

        // Convert the response to a blob (image)
        const imageBlob = await response.blob();
        const imageURL = URL.createObjectURL(imageBlob);

        // Display the processed image in the result section
        document.getElementById('resultImage').src = imageURL;
    } catch (error) {
        // Handle any errors that occur during the fetch request
        console.error('Error:', error);
        alert('An error occurred: ' + error.message);
    }
});
