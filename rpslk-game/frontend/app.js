//arrow logic
function connectArrowASCII(fromEl, toEl, arrowEl, charWidth = 8) {
  // container: element that holds both options and the .arrows overlay
  const container = document.getElementById('pentagon');
  const containerRect = container.getBoundingClientRect();
  const fromRect = fromEl.getBoundingClientRect();
  const toRect   = toEl.getBoundingClientRect();

  // center points relative to container
  const x1 = (fromRect.left + fromRect.width / 2) - containerRect.left;
  const y1 = (fromRect.top  + fromRect.height/ 2) - containerRect.top;
  const x2 = (toRect.left   + toRect.width  / 2) - containerRect.left;
  const y2 = (toRect.top    + toRect.height / 2) - containerRect.top;

  const dx = x2 - x1;
  const dy = y2 - y1;
  const distance = Math.sqrt(dx*dx + dy*dy);

  // compute angle in degrees
  const angle = Math.atan2(dy, dx) * 180 / Math.PI;

  // position arrow start point at (x1, y1), rotate around left middle
  arrowEl.style.left = `${x1}px`;
  arrowEl.style.top  = `${y1}px`;
  arrowEl.style.width = `${Math.max(0, distance)}px`;

  // translateY(-50%) centers arrow vertically at the midpoint of the from element
  arrowEl.style.transform = `translateY(-50%) rotate(${angle}deg)`;

  // fill arrow with repeated '-' and a '>' arrowhead
  // charWidth approximates how many pixels each dash takes (tweak if needed)
  const dashCount = Math.max(1, Math.floor(distance / (charWidth)));
  arrowEl.textContent = '-'.repeat(dashCount - 14) + '>';
}

const rock = document.querySelector('.pentagon .rock');
const paper = document.querySelector('.pentagon .paper');
const scissors = document.querySelector('.pentagon .scissors');
const lizard = document.querySelector('.pentagon .lizard');
const spock = document.querySelector('.pentagon .spock');

const arrowRtS = document.querySelector('.arrow.rock-to-scissors');
connectArrowASCII(rock, scissors, arrowRtS);

const arrowStP = document.querySelector('.arrow.scissors-to-paper');
connectArrowASCII(scissors, paper, arrowStP);

const arrowPtS = document.querySelector('.arrow.paper-to-spock');
connectArrowASCII(paper, spock, arrowPtS);

const arrowStR = document.querySelector('.arrow.spock-to-rock');
connectArrowASCII(spock, rock, arrowStR);

const arrowRtL = document.querySelector('.arrow.rock-to-lizard');
connectArrowASCII(rock, lizard, arrowRtL);

const arrowLtP = document.querySelector('.arrow.lizard-to-paper');
connectArrowASCII(lizard, paper, arrowLtP);

const arrowPtR = document.querySelector('.arrow.paper-to-rock');
connectArrowASCII(paper, rock, arrowPtR);

const arrowStS = document.querySelector('.arrow.spock-to-scissors');
connectArrowASCII(spock, scissors, arrowStS);

const arrowLtS = document.querySelector('.arrow.lizard-to-spock');
connectArrowASCII(lizard, spock, arrowLtS);

const arrowStL = document.querySelector('.arrow.scissors-to-lizard');
connectArrowASCII(scissors, lizard, arrowStL);

//show result
function showResult(html) {
    const resultMsg = document.getElementById('result-message');
    resultMsg.innerHTML = html;
}

//hide/show and wait for response
function displayPentagon(enable) {
    const pentagon = document.getElementById('pentagon');
    pentagon.style.display = enable ? 'block' : 'none';
    
    const resultBox = document.getElementById('result-box');
    resultBox.style.display = enable ? 'none' : 'block';

    const restartBtn = document.getElementById('restart');
    restartBtn.style.display = 'none';
}

//send backend
async function sendChoice(option) {
    const endpoint = '/play';
    try {
        displayPentagon(false);
        showResult("Waiting for result...");

        const resp = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ option })
        })

        if (!resp.ok) {
            const text = await resp.text().catch(()=>null);
            throw new Error(`Server returned ${resp.status}${text ? ': '+text : ''}`)
        }

        const data = await resp.json();

        const tone = (data.result === 'win') ? 'You win!' : (data.result === 'lose') ? 'You lose' : "It's a draw";
        const html =
                    `${tone}</br>
                    You: <b>${data.player}</b></br>
                    Computer: <b>${data.computer}</b></br>
                    ${data.message}`;

        showResult(html);

        const restart = document.getElementById('restart');
        restart.style.display = 'block';
        if (restart) restart.addEventListener('click', () => {
            displayPentagon(true);
            // remove highlights
            options.forEach(o => o.classList.remove('player-selected','computer-selected'));
        });

    } catch (err) {
        console.error(err);
    }
};

//select option
document.querySelectorAll('.pentagon .option').forEach(option => {
  option.addEventListener('click', async () => {
    var choice = option.className.split(" ")[1];
    await sendChoice(choice);
  });
});
