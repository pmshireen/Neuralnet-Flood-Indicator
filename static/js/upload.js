
        function previewImage(event){
            var imageInput = document.getElementById('imageInput')
            var imagePreview = document.getElementById('imagePreview')
            // Inside previewImage(event) function
            console.log('Selected image data URL:', imagePreview);



            imagePreview.style.display = 'block'
            var reader = new FileReader();
            reader.onload = function(){
                imagePreview.src = reader.result;
                // Inside request.onload function
                console.log('Response:', reader);
            };
            reader.readAsDataURL(imageInput.files[0])
        }



        function submitImage(){
            var imageInput = document.getElementById('imageInput');
            var imagePreview = document.getElementById('imagePreview');
            var imageSpinner = document.getElementById('imageSpinner');
            var captionResult = document.getElementById('captionResult');

            // Display the selected image preview

            var file = imageInput.files[0];
            var reader = new FileReader();
            reader.onloadend = function(){
                imagePreview.src =  reader.result;
                console.log(reader.result);
                imagePreview.style.display = 'block';
            };
            reader.readAsDataURL(file);

            // show the spinner while waiting for the response

            imageSpinner.style.display = 'block';

            // remove previous results
            captionResult.innerHTML = '';
            var formData = new FormData();
            formData.append('image',file);


            // create the request object

            var request =  new XMLHttpRequest();
            request.open('POST', '/upload',true);
            request.onload = function(){
                if(request.status >= 200 && request.status < 400){
                    var response = JSON.parse(request.responseText);
                    console.log('Response:', response); // Log the response to see its structure

                    imageSpinner.style.display = 'none';

                    var predictionDiv = document.createElement('div');
                    predictionDiv.innerText = 'Prediction: ' + response.prediction;
                    console.log("Prediction",response.prediction)
                    captionResult.appendChild(predictionDiv);

//
//                    var probabilityDiv = document.createElement('div');
//                    probabilityDiv.innerText = 'Prediction: ' + response.probability;
//                    captionResult.appendChild(probabilityDiv);

                }else{
                    imageSpinner.style.display = 'none';
                    alert('An error occured while processing the image');
                }
            };
            request.send(formData);
        }
