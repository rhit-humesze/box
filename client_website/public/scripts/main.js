// sound effects
var click = new Audio('./assets/click.mp3');
var unveil = new Audio('./assets/unveil.mp3');
var timesUp = new Audio('./assets/times_up.mp3');

// music tracks
var music_lightFunky = new Audio('./assets/music_light_funky.mp3');
music_lightFunky.loop = true;
music_lightFunky.volume = 0.1;
var music_heavyFunky = new Audio('./assets/music_heavy_funky.mp3');
music_heavyFunky.loop = true;
music_heavyFunky.volume = 0.1;
var music_lightElectric = new Audio('./assets/music_light_electric.mp3');
music_lightElectric.loop = true;
music_lightElectric.volume = 0.1;
var music_heavyElectric = new Audio('./assets/music_heavy_electric.mp3');
music_heavyElectric.loop = true;
music_heavyElectric.volume = 0.1;

// helper function to convert text to html elements
htmlToElement = (html) => {
	var template = document.createElement("template");
	html = html.trim();
	template.innerHTML = html;
	return template.content.firstChild;
}

// page for joining box lobby from code
window.onload = () => {
    document.getElementById("joinSession").onclick = (event) => {
        music_lightFunky.play();
        var boxCode = document.getElementById("boxCode").value;
        console.log(boxCode)
        click.play();
        // TODO: send code to listing server and connect to box lobby
        playerSetup();
    }
}

// page for player setup on connected box lobby
playerSetup = () => {
    document.querySelector('#pageContent').remove();
    var setupPage = htmlToElement(
        `<div id="pageContent">
            <div id="loginInfo" class="RHpopup">
                <div>
                    <div class="popupHeader">Game found!</div>
                    <div class="popupSubheader">Please enter your name:</div>
                </div>
                <div class="entryGroup">
                    <input id="userName" maxlength="15" spellcheck="false" style='width: clamp(8rem, 50vw, 30rem) !important'>
                    <button id="addPlayer">Join Box</button>
                </div>
            </div>
        </div>`);
    document.querySelector('body').appendChild(setupPage);
    unveil.play()
    document.getElementById("addPlayer").onclick = (event) => {
        var userName = document.getElementById("userName").value;
        console.log(userName)
        click.play();
        // TODO: send username to box lobby server
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
    music_lightFunky.pause();
    music_heavyFunky.play();
    // TODO: fill page content from box lobby game stuff
}