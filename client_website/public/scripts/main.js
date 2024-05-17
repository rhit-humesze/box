var socket;

// sound effects
var click = new Audio('./assets/click.mp3');
var unveil = new Audio('./assets/unveil.mp3');
var timesUp = new Audio('./assets/times_up.mp3');

// helper function to convert text to html elements
htmlToElement = (html) => {
	var template = document.createElement("template");
	html = html.trim();
	template.innerHTML = html;
	return template.content.firstChild;
}

// page for joining box lobby from code
window.onload = () => {
    var clickable = true
    document.getElementById("joinSession").onclick = () => {
        var boxCode = document.getElementById("boxCode").value;
        if(boxCode == "" || !clickable) {
            return;
        }
        clickable = false;
        console.log(boxCode);
        click.play();
        //var serverLobby = "https://" + "137.112.226.137" + ":5100/"
        // DEBUGGING/TESTING purposes only
        var serverLobby = "https://" + "localhost" + ":5100/";

        socket = io.connect(`${serverLobby}`, {rejectUnauthorized: false});
        socket.on("connect_error", () => {
            socket.close()
            clickable = true;
            timesUp.play();
            document.getElementById("boxCode").value = "";
            var errorMsg = htmlToElement(`<div class="popupError">Box Code invalid! Try again.</div>`);
            document.getElementById("headerGroup").appendChild(errorMsg);
            setTimeout(() => errorMsg.style.opacity = '0', 1000);
            setTimeout(() => errorMsg.remove(), 2000);
        });
        socket.on("connect", () => {
            socket.emit("gameCode", boxCode);
        });
        socket.on("codeDenied", () => {
            socket.close();
            clickable = true;
            timesUp.play();
            document.getElementById("boxCode").value = "";
            var errorMsg = htmlToElement(`<div class="popupError">Box Code invalid! Try again.</div>`);
            document.getElementById("headerGroup").appendChild(errorMsg);
            setTimeout(() => errorMsg.style.opacity = '0', 1000);
            setTimeout(() => errorMsg.remove(), 2000);
        });
        socket.on("codeAccepted", () => {
            playerSetup();
        });
    }
}

// page for player setup on connected box lobby
playerSetup = () => {
    socket.on("connect_error", (error) => {
        if (socket.active) {
            // temporary failure, the socket will automatically try to reconnect
        } else {
            clearPage()
            console.log(error.message);
        }
    });
    socket.on("connect", () => {});
    socket.on("drawSomeDraw", () => {
        drawSomeDraw();
    });
    socket.on("drawSomeVote", () => {
        drawSomeVote();
    });
    socket.on("boxphoneWait", () => {
        boxphoneWait();
    });
    socket.on("boxphoneFirstWrite", () => {
        boxphoneFirstWrite();
    });
    socket.on("boxphoneWrite", (prevImageData) => {
        boxphoneWrite(prevImageData);
    });
    socket.on("boxphoneDraw", (prevText) => {
        boxphoneDraw(prevText);
    });
    socket.on("boxphoneResults", (textPrompts, imagePrompts) => {
        boxphoneResults(textPrompts, imagePrompts);
    });
    socket.on("timesUp", () => {
        timesUp.play();
        clearPage();
    });
    document.querySelector('#pageContent').remove();
    var setupPage = htmlToElement(
        `<div id="pageContent">
            <div class="RHpopup">
                <div id="headerGroup">
                    <div class="popupHeader">Game found!</div>
                    <div class="popupSubheader">Please enter your name:</div>
                </div>
                <div class="entryGroup">
                    <input id="userName" class="textInput" maxlength="12" spellcheck="false" placeholder="(ex: Jack)" style='width: clamp(8rem, 50vw, 30rem) !important'>
                    <button id="addPlayer">Join Box</button>
                </div>
            </div>
        </div>`);
    document.querySelector('body').appendChild(setupPage);
    document.getElementById("addPlayer").onclick = (event) => {
        var userName = document.getElementById("userName").value;
        if(userName == "") {
            return;
        }
        console.log(userName);
        click.play();
        socket.emit("userName", userName);
        boxLobby();
    }
    unveil.play();
}

// page for awaiting game start within box lobby
boxLobby = () => {
    document.querySelector('#pageContent').remove();
    var setupPage = htmlToElement(
        `<div id="pageContent">
            <div class="RHpopup">
                <div id="headerGroup">
                    <div class="popupHeader">You're in!</div>
                    <div class="popupSubheader">Please wait for the host to start.</div>
                </div>
            </div>
        </div>`);
    document.querySelector('body').appendChild(setupPage);
    unveil.play();
}

// page for drawing images in draw some game
drawSomeDraw = () => {
    document.querySelector('#pageContent').remove();
    var setupPage = htmlToElement(
        `<div id="pageContent">
            <div class="LHpopup">
                <div class="sideBySide">
                    <div class="entryGroup">
                        <div class="popupHeader">Draw Some!</div>
                        <div class="popupSubheader">Draw your idea and click submit before time runs out!</div>
                        <div class="sideBySide">
                            <input id="nameEntry" class="textInput" maxlength="20" spellcheck="false" placeholder="(ex: Super funny drawing)" style="margin-right:1vw; font-size: 3vh;">
                            <button id="drawSomeSubmitButton">Submit</button>
                        </div>
                    </div>
                    <div class="paintArea">
                        <canvas id="paintCanvas"></canvas>
                        <div style="display: flex; flex-direction: row; flex-wrap: nowrap;">
                            <div class="clr" data-clr="#000000"></div>
                            <div class="clr" data-clr="#FF0000"></div>
                            <div class="clr" data-clr="#FF8800"></div>
                            <div class="clr" data-clr="#FFFF00"></div>
                            <div class="clr" data-clr="#00FF00"></div>
                            <div class="clr" data-clr="#0000FF"></div>
                            <div class="clr" data-clr="#8800FF"></div>
                            <div class="clr" data-clr="#FFFFFF"></div>
                            <div class="clr" data-clr="#E6C25D"></div>
                        </div>
                        <input id="slider" class="rangeSlider" type="range" min="3" max="7" value="3">
                    </div>
                    <script src="scripts/draw.js"></script>
                    <!-- courtesy of https://dev.to/0shuvo0/lets-create-a-drawing-app-with-js-4ej3 -->
                </div>
            </div>
        </div>`);
    document.querySelector('body').appendChild(setupPage);
    var newScript = document.createElement('script');
    newScript.type = 'text/javascript';
    newScript.src = 'scripts/draw.js';
    newScript.id = 'canvasScript';
    document.getElementsByTagName('head')[0].appendChild(newScript);

    const canvas = document.getElementById("paintCanvas");
    let saveBtn = document.getElementById("drawSomeSubmitButton");
    saveBtn.addEventListener("click", () => {
        let data = canvas.resizeAndExport(256, 256);
        let name = document.getElementById("nameEntry").value;
        if(name == "") {
            return;
        }
        console.log(data);
        console.log(name);
        // let a = document.createElement("a");
        // a.href = data;
        // a.download = "sketch.png";
        // a.click();
        socket.emit("drawingSubmission", data, name);
        click.play();
        document.getElementById("canvasScript").remove();
        clearPage()
    })
    canvas.resizeAndExport = function(width, height){
        var c = document.createElement('canvas');
        c.width = width;
        c.height = height;
        c.getContext('2d').drawImage(this, 0, 0, this.width, this.height, 0, 0, width, height);
        return c.toDataURL();
    }
    unveil.play();
}

// page for voting on drawings in draw some game
drawSomeVote = () => {
    document.querySelector('#pageContent').remove();
    var setupPage = htmlToElement(
        `<div id="pageContent">
            <div class="RHpopup">
                <div class="entryGroup">
                    <div class="popupHeader" style="text-align:center;">Vote!</div>
                    <div class="sideBySide">
                        <button id="button1">Left!</button>
                        <button id="button2">Right!</button>
                    </div>
                </div>
            </div>
        </div>`);
    document.querySelector('body').appendChild(setupPage);
    document.getElementById("button1").onclick = () => {
        click.play();
        socket.emit("drawingVote", "left");
        clearPage();
    }
    document.getElementById("button2").onclick = () => {
        click.play();
        socket.emit("drawingVote", "right");
        clearPage();
    }
    unveil.play();
}

boxphoneWait = () => {
    document.querySelector('#pageContent').remove();
    var setupPage = htmlToElement(
        `<div id="pageContent">
            <div class="LHpopup">
                <div class="sideBySide">
                    <div class="entryGroup">
                        <div class="popupHeader">Box Phone!</div>
                        <div class="popupSubheader">Wait for your turn!</div>
                    </div>
                </div>
            </div>
        </div>`);
    document.querySelector('body').appendChild(setupPage);
}

boxphoneFirstWrite = () => {
    document.querySelector('#pageContent').remove();
    var setupPage = htmlToElement(
        `<div id="pageContent">
            <div class="LHpopup">
                <div class="sideBySide">
                    <div class="entryGroup">
                        <div class="popupHeader">Box Phone!</div>
                        <div class="popupSubheader">Write a funny prompt and click submit before time runs out!</div>
                        <div class="sideBySide">
                            <input id="textResponse" class="textInput" maxlength="100" spellcheck="false" placeholder="(Ex: A bird feeding it's chicks)" style='font-size:100%;width:clamp(8rem,50vw,30rem) !important' />
                            <button id="boxphoneSubmitButton">Submit</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>`);
    document.querySelector('body').appendChild(setupPage);

    const textResponse = document.getElementById("textResponse");
    let saveBtn = document.getElementById("boxphoneSubmitButton");
    saveBtn.addEventListener("click", () => {
        let data = textResponse.innerHTML;
        console.log(data);
        socket.emit("boxphoneTextSubmission", data);
        click.play();
        clearPage()
    })
    unveil.play();
}

boxphoneWrite = (prevImageData) => {
    document.querySelector('#pageContent').remove();
    var setupPage = htmlToElement(
        `<div id="pageContent">
            <div class="LHpopup">
                <div class="sideBySide">
                    <div class="entryGroup">
                        <div class="popupHeader">Box Phone!</div>
                        <div class="popupSubheader">Previous player's drawing:</div>
                        <img id="prevImageArea" src="./public/assets/box_tile.png" alt="Previous Player's Drawing" width="256" height="256"> 
                        <div class="popupSubheader">Write your response and click submit before time runs out!</div>
                        <input id="textResponse" class="textInput" maxlength="100" spellcheck="false" placeholder="(Ex: A bird feeding it's chicks)" style='font-size:100%;width:clamp(8rem,50vw,30rem) !important' />
                        <button id="boxphoneSubmitButton">Submit</button>
                    </div>
                </div>
            </div>
        </div>`);
    document.querySelector('body').appendChild(setupPage);

    // Change the image to be the one from previous player
    const prevImagePath = `data:image/png;base64,${prevImageData}`;
    document.getElementById("prevImageArea").src = prevImagePath;


    const textResponse = document.getElementById("textResponse");
    let saveBtn = document.getElementById("boxphoneSubmitButton");
    saveBtn.addEventListener("click", () => {
        let data = textResponse.innerHTML;
        console.log(data);
        socket.emit("boxphoneTextSubmission", data);
        click.play();
        clearPage()
    })
    unveil.play();
}

// page for drawing images in boxphone game
boxphoneDraw = (prevText) => {
    document.querySelector('#pageContent').remove();
    var setupPage = htmlToElement(
        `<div id="pageContent">
            <div class="LHpopup">
                <div class="sideBySide">
                    <div class="entryGroup">
                        <div class="popupHeader">Box Phone!</div>
                        <div class="popupSubheader">Previous player's description:</div>
                        <p id="prevTextArea">This player didn't submit anything... Good luck!</p>
                        <div class="popupSubheader">Draw your response and click submit before time runs out!</div>
                        <button id="boxphoneSubmitButton">Submit</button>
                    </div>
                    <div class="paintArea">
                        <canvas id="paintCanvas"></canvas>
                        <div style="display: flex; flex-direction: row; flex-wrap: nowrap;">
                            <div class="clr" data-clr="#000000"></div>
                            <div class="clr" data-clr="#FF0000"></div>
                            <div class="clr" data-clr="#FF8800"></div>
                            <div class="clr" data-clr="#FFFF00"></div>
                            <div class="clr" data-clr="#00FF00"></div>
                            <div class="clr" data-clr="#0000FF"></div>
                            <div class="clr" data-clr="#8800FF"></div>
                            <div class="clr" data-clr="#FFFFFF"></div>
                            <div class="clr" data-clr="#E6C25D"></div>
                        </div>
                        <input id="slider" class="rangeSlider" type="range" min="3" max="7" value="3">
                    </div>
                    <script src="scripts/draw.js"></script>
                    <!-- courtesy of https://dev.to/0shuvo0/lets-create-a-drawing-app-with-js-4ej3 -->
                </div>
            </div>
        </div>`);
    document.querySelector('body').appendChild(setupPage);
    var newScript = document.createElement('script');
    newScript.type = 'text/javascript';
    newScript.src = 'scripts/draw.js';
    newScript.id = 'canvasScript';
    document.getElementsByTagName('head')[0].appendChild(newScript);

    // Change the text to be the one from previous player
    document.getElementById("prevTextArea").innerHTML = prevText;

    const canvas = document.getElementById("paintCanvas");
    let saveBtn = document.getElementById("boxphoneSubmitButton");
    saveBtn.addEventListener("click", () => {
        let data = canvas.resizeAndExport(256, 256);
        console.log(data);
        socket.emit("boxphoneDrawingSubmission", data);
        click.play();
        document.getElementById("canvasScript").remove();
        clearPage()
    })
    canvas.resizeAndExport = function(width, height){
        var c = document.createElement('canvas');
        c.width = width;
        c.height = height;
        c.getContext('2d').drawImage(this, 0, 0, this.width, this.height, 0, 0, width, height);
        return c.toDataURL();
    }
    unveil.play();
}

boxphoneResults = (textPrompts, imagePrompts) => {
    document.querySelector('#pageContent').remove();
    var setupPage = htmlToElement(
        `<div id="pageContent">
            <div class="LHpopup">
                <div class="sideBySide">
                    <div class="entryGroup">
                        <div class="popupHeader">Box Phone!</div>
                        <div class="popupSubheader">The game is over, here are the results!</div>
                        <div id="boxphoneResultsArea"></div>
                    </div>
                </div>
            </div>
        </div>`);
    document.querySelector('body').appendChild(setupPage);

    /*
    // Display text, image, text, image
    const resultsArea = document.getElementById("boxphoneResultsArea");

    const totalSubmissions = textPrompts.length + imagePrompts.length;
    for (let i = 0; i < totalSubmissions; i++) {
        if (i % 2 === 0) { // even
            let textResponse = textPrompt
            let elem = document.createTextNode(textResponse)

        } else { // odd
            const imagePath = `data:image/png;base64,${prevImageData}`;
            let elem = new Image();
            elem.src = imagePath;
        }
        resultsArea.appendChild(img);
    }
    */
}

clearPage = () => {
    document.querySelector('#pageContent').remove();
    var setupPage = htmlToElement(
        `<div id="pageContent"></div>`);
    document.querySelector('body').appendChild(setupPage);
    unveil.play();
}