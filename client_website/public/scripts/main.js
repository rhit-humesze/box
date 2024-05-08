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
        console.log(boxCode)
        click.play();
        var serverLobby = "http://127.0.0.1:5100/"
        socket = io.connect(`${serverLobby}`);
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
            socket.close()
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
            // the connection was denied by the server
            console.log(error.message);
        }
    });
    socket.on("connect", () => {});
    document.querySelector('#pageContent').remove();
    var setupPage = htmlToElement(
        `<div id="pageContent">
            <div class="RHpopup">
                <div id="headerGroup">
                    <div class="popupHeader">Game found!</div>
                    <div class="popupSubheader">Please enter your name:</div>
                </div>
                <div class="entryGroup">
                    <input id="userName" maxlength="15" spellcheck="false" placeholder="(ex: Jack)" style='width: clamp(8rem, 50vw, 30rem) !important'>
                    <button id="addPlayer">Join Box</button>
                </div>
            </div>
        </div>`);
    document.querySelector('body').appendChild(setupPage);
    unveil.play()
    document.getElementById("addPlayer").onclick = (event) => {
        var userName = document.getElementById("userName").value;
        if(userName == "") {
            return;
        }
        console.log(userName)
        click.play();
        // TODO: send username to box lobby server
        socket.emit("userName", userName);
        boxLobby();
    }
}

// page for playing games within box lobby
boxLobby = () => {
    document.querySelector('#pageContent').remove();
    var setupPage = htmlToElement(
        `<div id="pageContent">
        </div>`);
    document.querySelector('body').appendChild(setupPage);
    unveil.play()
    // TODO: fill page content from box lobby game stuff
}