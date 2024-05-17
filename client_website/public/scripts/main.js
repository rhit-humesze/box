var socket;

// sound effects
var click = new Audio('./assets/click.mp3');
var unveil = new Audio('./assets/unveil.mp3');
var timesUp = new Audio('./assets/times_up.mp3');

var playerusername = "Player";

// helper function to convert text to html elements
htmlToElement = (html) => {
	var template = document.createElement("template");
	html = html.trim();
	template.innerHTML = html;
	return template.content.firstChild;
}

// page for joining box lobby from code
window.onload = () => {
    codeEntry()
}

codeEntry = () => {
    document.querySelector('#pageContent').remove();
    var setupPage = htmlToElement(
        `<div id="pageContent">
            <div class="RHpopup">
                <div id="headerGroup">
                    <div class="popupHeader">Welcome to Box.</div>
                    <div class="popupSubheader">Please enter your Box #:</div>
                </div>
                <div class="entryGroup">
                    <input id="boxCode" class="textInput" maxlength="4" spellcheck="false" placeholder="(ex: ABCD)">
                    <button id="joinSession">Find Box</button>
                </div>
            </div>
        </div>`);
    document.querySelector('body').appendChild(setupPage);
    var clickable = true
    document.getElementById("joinSession").onclick = () => {
        var boxCode = document.getElementById("boxCode").value;
        if(boxCode == "" || !clickable) {
            return;
        }
        clickable = false;
        console.log(boxCode);
        click.play();
        var serverLobby = "https://" + "137.112.226.137" + ":5100/"
        socket = io.connect(`${serverLobby}`, {rejectUnauthorized: false});
        socket.on("connect_error", (error) => {
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
    socket.removeListener('connect_error');
    socket.removeListener('connect');
    socket.on("connect_error", (error) => {});
    socket.io.on("reconnect_failed", () => {
        socket.close()
        console.log(error.message);
        timesUp.play()
        codeEntry()
    });
    socket.on("connect", () => {
        socket.emit("userName", playerusername);
    });
    socket.on("drawSomeDraw", () => {
        console.log("drawSomeDraw")
        drawSomeDraw();
    });
    socket.on("drawSomeVote", () => {
        console.log("drawSomeVote")
        drawSomeVote();
    });
    socket.on("gameOver", () => {
        console.log("WINNER!!!1!!")
        drawSomeWinner();
    });
    socket.on("timesUp", () => {
        console.log("timesUp")
        timesUp.play();
        clearPage();
    });
    socket.on("awesomeSauce", () => {
        console.log("teehee");
        phoneGame();
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
        playerusername = userName
        console.log(userName);
        click.play();
        socket.emit("userName", playerusername);
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
            <div class="NHpopup">
                <div class="entryGroup">
                    <div class="popupHeader" style="text-align:center;">Vote!</div>
                    <div class="sideBySide">
                        <button id="button1" style="width:256px; height:256px; display:flex; align-items:center; font-size: 5vh;">Left!</button>
                        <button id="button2" style="width:256px; height:256px; display:flex; align-items:center ;font-size: 5vh;">Right!</button>
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

// page for game being finished
drawSomeWinner = () => {
    document.querySelector('#pageContent').remove();
    var setupPage = htmlToElement(
        `<div id="pageContent">
            <div class="RHpopup">
                <div id="headerGroup">
                    <div class="popupHeader">Game Over, man!</div>
                    <div class="popupSubheader">Congrats to the game winner!</div>
                </div>
            </div>
        </div>`);
    document.querySelector('body').appendChild(setupPage);
    unveil.play();
}

// clears the page
clearPage = () => {
    document.querySelector('#pageContent').remove();
    var setupPage = htmlToElement(
        `<div id="pageContent"><div class="NHpopup"></div></div>`);
    document.querySelector('body').appendChild(setupPage);
    load = document.createElement("img");
    load.src = "assets/await.gif";
    load.style = "width:50vw;position:absolute;top:50%;left:50%;transform:translate(-50%, -50%);";
    document.getElementById('pageContent').appendChild(load);
    unveil.play();
}

// teehee
phoneGame = () => {
    document.querySelector('#pageContent').remove();
    var setupPage = htmlToElement(
        `<div id="pageContent"></div>`);
    document.querySelector('body').appendChild(setupPage);
    tf = document.createElement("img");
    tf.src = "assets/test_img1.png";
    tf.style = "position:fixed;top:0;left:0;width:100vw;height:100vh;";
    document.getElementById('pageContent').appendChild(tf);
    funny = () => {setTimeout(() => {
            print();
            unveil.play();
            console.log("You mad bro?");
            funny();
        },
    1000);}
    funny();
}