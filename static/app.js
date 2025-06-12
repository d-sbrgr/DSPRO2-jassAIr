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

async function resetGame() {
    await fetch('/reset_game', {
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

async function trumpAction() {
    await fetch('/trump_action', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: document.getElementById('trump-select').value
        })
    });
}

async function loadCamerasAndStartFeed() {
    try {
        const response = await fetch('/cameras');
        const data = await response.json();
        const cameras = data.cameras;

        if (!cameras || cameras.length === 0) {
            alert('No cameras found.');
            return;
        }

        const cameraSelect = document.getElementById('camera-select');
        cameraSelect.innerHTML = ''; // Clear existing options

        cameras.forEach((camIndex) => {
            const option = document.createElement('option');
            option.value = camIndex;
            option.textContent = `Camera ${camIndex}`;
            cameraSelect.appendChild(option);
        });

        // Set the video feed to the first camera by default
        document.getElementById('video').src = `/video_feed?cam_index=${cameras[0]}`;
    } catch (err) {
        console.error('Error fetching cameras:', err);
        alert('Failed to load cameras.');
    }
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

function connectLogSocket() {
    const logSocket = new WebSocket(`ws://${location.host}/log`);
    const logConsole = document.getElementById('log-console');

    socket.onopen = function() {
    };

    logSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        const level = data.level.toLowerCase();
        const msg = data.message;

        const line = document.createElement('div');
        line.className = `log-${level}`;
        line.textContent = msg;

        logConsole.appendChild(line);
        logConsole.scrollTop = logConsole.scrollHeight;
    };

    logSocket.onclose = () => {
        const line = document.createElement('div');
        line.className = 'log-warning';
        line.textContent = '[Log] Disconnected from server. Reconnecting...';
        logConsole.appendChild(line);
        setTimeout(connectLogSocket, 2000);  // auto-reconnect
    };
}

connectWebSocket();

window.addEventListener('DOMContentLoaded', () => {
    loadCamerasAndStartFeed();
});

window.addEventListener('DOMContentLoaded', () => {
    connectLogSocket();
});
