document.addEventListener('DOMContentLoaded', function() {
    // Test endpoint functionality
    document.querySelectorAll('.test-endpoint').forEach(button => {
        button.addEventListener('click', async function() {
            const url = this.dataset.url;
            const queryParams = this.closest('.endpoint').querySelector('.query-params').value;
            const responseContainer = this.closest('.endpoint-card').querySelector('.response-container');
            const responseData = responseContainer.querySelector('.response-data');
            
            try {
                const fullUrl = queryParams ? `${url}${queryParams}` : url;
                const response = await fetch(fullUrl);
                const data = await response.json();
                responseContainer.style.display = 'block';
                responseData.textContent = JSON.stringify(data, null, 2);
                Prism.highlightElement(responseData);
            } catch (error) {
                responseContainer.style.display = 'block';
                responseData.textContent = `Error: ${error.message}`;
            }
        });
    });

    // Test single record endpoint
    document.querySelectorAll('.test-single-record').forEach(button => {
        button.addEventListener('click', async function() {
            const baseUrl = this.dataset.url;
            const recordId = this.previousElementSibling.value;
            const responseContainer = this.closest('.endpoint-card').querySelector('.response-container');
            const responseData = responseContainer.querySelector('.response-data');
            
            if (!recordId) {
                alert('Please enter a record ID');
                return;
            }

            try {
                const response = await fetch(`${baseUrl}${recordId}`);
                const data = await response.json();
                responseContainer.style.display = 'block';
                responseData.textContent = JSON.stringify(data, null, 2);
                Prism.highlightElement(responseData);
            } catch (error) {
                responseContainer.style.display = 'block';
                responseData.textContent = `Error: ${error.message}`;
            }
        });
    });
});
