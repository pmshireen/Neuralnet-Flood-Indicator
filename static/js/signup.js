// signup.js

document.addEventListener('DOMContentLoaded', function() {
  // Add event listener to the form submission
  document.getElementById('signupForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    // Retrieve form data
    const formData = new FormData(this);

    // Example of sending form data to the server
    fetch('/signup', {
      method: 'POST',
      body: formData
    })
    .then(response => {
      // Handle response from the server
      if (response.ok) {
        // Display success message or redirect to another page
        alert('Signup successful!');
        // You can redirect the user to another page if needed
        // window.location.href = 'success.html';
      } else {
        // Handle error response from the server
        alert('Signup failed. Please try again.');
      }
    })
    .catch(error => {
      // Handle network errors
      console.error('Error:', error);
      alert('Network error. Please try again later.');
    });
  });
});
