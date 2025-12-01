// add games into game-list
var availableGames = ["rpslk"];
const gameTable = document.getElementById("game-list");
if (!gameTable) throw new Error('#game-list not found');

const gameFrag = document.createDocumentFragment();

availableGames.forEach(element => {
    const id = `game-${element}`;

    const input = document.createElement('input');
    input.type = 'radio';
    input.id = id;
    input.name = 'games';
    input.value = String(element);

    const label = document.createElement('label');
    label.htmlFor = id;
    label.textContent = ` ${element}`;

    gameFrag.appendChild(input);
    gameFrag.appendChild(label);
});

gameTable.appendChild(gameFrag);

//dynamically append input for players
const playCell = document.getElementById("players-cell");
if (!playCell) throw new Error('#players-cell not found');

const playerFrag = document.createDocumentFragment();

for (let i = 1; i <= 9; ++i) {
    const id = `player-${i}`;

    const input = document.createElement('input');
    input.type = 'radio';
    input.id = id;
    input.name = 'players';
    input.value = String(i);
    if(i != 1) input.disabled = true;

    const label = document.createElement('label');
    label.htmlFor = id;
    label.textContent = ` ${i}`;

    playerFrag.appendChild(input);
    playerFrag.appendChild(label);
}

playCell.appendChild(playerFrag);

//break functions
function increaseBreak() {
    const breakInput = document.getElementById("break-time");
    var breakTime = parseInt(breakInput.innerText);
    if(breakTime < 20) breakInput.innerText = breakTime + 1;
}

function decreaseBreak() {
    const breakInput = document.getElementById("break-time");
    var breakTime = parseInt(breakInput.innerText);
    if(breakTime > 5) breakInput.innerText = breakTime - 1;
}

//show qr
function showQr(html) {
    const resultMsg = document.getElementById('qr-cell');
    resultMsg.innerHTML = html;
}

//send backend
async function sendChoice(game, lifetime) {
    const endpoint = '/start-game';
    try {
        showQr("Waiting for pod generation...");

        const resp = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ game, lifetime })
        })

        if (!resp.ok) {
            const text = await resp.text().catch(()=>null);
            throw new Error(`Server returned ${resp.status}${text ? ': '+text : ''}`)
        }

        const data = await resp.json();
        
        const html = `Pod: <b>${data.pod}</b></br>
                    IP: <a href="http://${data.ip}/">http://${data.ip}/</a></br>
                    Lifetime: <b>${data.lifetime}</b></br>`;

        showQr(html);

    } catch (err) {
        console.error(err);
    }
};

//play button
const play = document.getElementById('play-button');
play.addEventListener('click', async () => {
    const selected = document.querySelector('input[name="games"]:checked');
    const breakInput = document.getElementById("break-time");
    var breakTime = parseInt(breakInput.innerText);
    if(selected && breakTime >= 5 && breakTime <= 20) await sendChoice(selected.value, breakTime);
});
