let gameState = null;

async function fetchState() {
    const response = await fetch('/api/state');
    gameState = await response.json();
    render();
}

async function startGame() {
    await fetch('/api/start', { method: 'POST' });
    fetchState();
}

const headers = { 'Content-Type': 'application/json' };

async function takeFromDeck() {
    await fetch('/api/action/take_deck', {
        method: 'POST',
        headers: headers
    });
    fetchState();
}
async function takeFromTable(index) {
    await fetch(`/api/action/take_table`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ index: index })
    });
    fetchState();
}

async function placeTile(r, c) {
    await fetch('/api/action/place', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ row: r, col: c })
    });
    fetchState();
}

async function passTile() {
    await fetch('/api/action/pass', { method: 'POST' });
    fetchState();
}

function render() {
    if (!gameState) return;

    document.getElementById('message-box').innerText = gameState.message;
    document.getElementById('deck-count').innerText = gameState.closed_count;
    document.getElementById('table-count').innerText = gameState.opened_numbers.length;

    const handDisplay = document.getElementById('hand-display');
    if (gameState.current_tile !== null) {
        handDisplay.innerText = gameState.current_tile;
    } else {
        handDisplay.innerText = "-";
    }
    const tableDiv = document.getElementById('table-numbers');
    tableDiv.innerHTML = '';
    gameState.opened_numbers.forEach((num, idx) => {
        const tile = document.createElement('div');
        tile.className = 'table-tile';
        tile.innerText = num;
        tile.onclick = () => { if (!gameState.current_tile) takeFromTable(idx); };
        tableDiv.appendChild(tile);
    });

    renderGrid('player-grid', gameState.player_field, true);
    renderGrid('bot-grid', gameState.bot_field, false);

    const actionArea = document.getElementById('action-area');
    actionArea.innerHTML = '';

    if (gameState.game_over) {
        actionArea.innerHTML = '<h3>Игра окончена</h3>';
        return;
    }

    if (gameState.current_tile === null) {
        const btnDeck = document.createElement('button');
        btnDeck.className = 'btn btn-primary';
        btnDeck.innerText = 'Взять из колоды';
        btnDeck.disabled = gameState.closed_count === 0;
        btnDeck.onclick = takeFromDeck;
        actionArea.appendChild(btnDeck);

        if (gameState.opened_numbers.length > 0) {
            const info = document.createElement('div');
            info.style.marginTop = '10px';
            info.innerText = 'Или нажмите на число на столе';
            actionArea.appendChild(info);
        }
    } else {
        const btnPass = document.createElement('button');
        btnPass.className = 'btn btn-danger';
        btnPass.innerText = 'Сбросить на стол';
        btnPass.onclick = passTile;
        actionArea.appendChild(btnPass);

        const info = document.createElement('div');
        info.style.marginTop = '10px';
        info.innerText = 'Нажмите на подсвеченную клетку';
        actionArea.appendChild(info);
    }
}

function renderGrid(elementId, fieldData, isPlayer) {
    const grid = document.getElementById(elementId);
    grid.innerHTML = '';

    for (let r = 0; r < 4; r++) {
        for (let c = 0; c < 4; c++) {
            const cell = document.createElement('div');
            const val = fieldData[r][c];
            cell.className = `cell ${isPlayer ? 'player' : 'bot'} ${val === 0 ? 'empty' : ''}`;
            cell.innerText = val === 0 ? '' : val;

            if (isPlayer && !gameState.game_over && gameState.current_tile !== null) {
                cell.style.cursor = 'pointer';
                cell.onclick = () => placeTile(r, c);

                cell.onmouseover = () => { if (val === 0 || val === gameState.current_tile) cell.style.background = '#fff3cd'; };
                cell.onmouseout = () => { if (val === 0) cell.style.background = '#fafafa'; else cell.style.background = '#e3f2fd'; };
            }

            grid.appendChild(cell);
        }
    }
}
startGame();