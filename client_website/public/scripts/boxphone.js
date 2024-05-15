

document.getElementById('submitMessage').onclick = function() {
    const imageResponse = document.getElementById('imageResponse');
    const textResponse = document.getElementById('textResponse');
    // TODO: send either image or text based on which turn it is
    const text = textResponse.innerText;
    socket.emit("boxphone-text-response", text);
    const file = imageResponse.files[0];
    if (file) {
        socket.emit("boxphone-image-reponse", file, (status) => {
            console.log(status);
        });
    } else {
        console.log('No file selected');
    }
}