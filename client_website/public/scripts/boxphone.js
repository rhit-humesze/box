// helper function to convert text to html elements
htmlToElement = (html) => {
    var template = document.createElement("template");
    html = html.trim();
    template.innerHTML = html;
    return template.content.firstChild;
}

boxPhone = () => {
    document.querySelector('#pageContent').remove();
    var setupPage = htmlToElement(
        `<div id="pageContent">
        </div>`);
    document.querySelector('body').appendChild(setupPage);
    unveil.play()
    // TODO: fill page content from box lobby game stuff
}