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
    var breakTime = parseInt(breakInput.value);
    if(breakTime < 20) breakInput.value = breakTime + 1;
}

function decreaseBreak() {
    const breakInput = document.getElementById("break-time");
    var breakTime = parseInt(breakInput.value);
    if(breakTime > 5) breakInput.value = breakTime - 1;
}