let socket;

function updateGameState(data) {
  const { game_state, detection_state, bot_state } = data;

  let trickHtml = "";
  for (let i = 0; i < 4; i++) {
    const card = game_state.current_trick[i];
    if (card) {
      const imgSrc = `/static/cards/${card}.png`;
      trickHtml += `
        <div class="card-frame">
          <img class="card" src="${imgSrc}" alt="${card}">
        </div>`;
    } else {
      trickHtml += `<div class="card-placeholder"></div>`;
    }
  }

  document.getElementById('game-state').innerHTML = `
    <div><strong>Current Player:</strong> ${game_state.current_player}</div>
    <div><strong>Current Trumpf:</strong> ${game_state.current_trumpf}</div>
    <div><strong>Current Trick:</strong><br><div class="trick-container">${trickHtml}</div></div>
  `;

  const detectionHtml = detection_state.detected_cards.map(card => `
    <div class="card-frame">
      <img class="card" src="/static/cards/${card}.png" alt="${card}">
    </div>
  `).join('');

  document.getElementById('detection-state').innerHTML = `
    <div><strong>Detected Cards:</strong></div>
    <div class="carousel-container">${detectionHtml}</div>
  `;

  const agentCard = bot_state.last_agent_play;
  document.getElementById('bot-state').innerHTML = `
    <div class="card-container">
      ${
        agentCard
          ? `<div class="card-frame">
               <img class="card" src="/static/cards/${agentCard}.png" alt="${agentCard}">
             </div>`
          : `<div class="card-placeholder">No play</div>`
      }
      <div><strong>${agentCard ?? ''}</strong></div>
    </div>
  `;
}

function resetGame() {
    fetch('/reset_game', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            dealer: document.getElementById('dealer-select').value,
            player: document.getElementById('player-select').value
        })
    });
}

function trumpAction() {
    fetch('/trump_action', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: document.getElementById('trump-select').value
        })
    });
}

async function updateFeed() {
    var camIndex = document.getElementById('camera-select').value;
    document.getElementById('video').src = '/video_feed?cam_index=' + camIndex;
}

function connectWebSocket() {
  socket = new WebSocket(`ws://${location.host}/ws`);

  socket.onopen = function() {
  };

  socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    updateGameState(data);
  };

  socket.onclose = function() {
    setTimeout(connectWebSocket, 2000);
  };
}

connectWebSocket();
