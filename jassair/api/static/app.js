let socket;
let detectedCards = []; // 🔥 local array to keep track

function updateGameState(data) {
  const { game_state, detection_state, bot_state } = data;

  // Update local detectedCards array
  if (detection_state.detected_cards) {
    detectedCards = detection_state.detected_cards;
  } else if (detection_state.last_detected_card) {
    // Fallback if only last detected is available
    detectedCards.push(detection_state.last_detected_card);
  }

  // Render Trick
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

  // Render Detected Cards Carousel
  const detectionHtml = detectedCards.map(card => `
    <div class="card-frame">
      <img class="card" src="/static/cards/${card}.png" alt="${card}">
    </div>
  `).join('');

  document.getElementById('detection-state').innerHTML = `
    <div><strong>Detected Cards:</strong></div>
    <div class="carousel-container">${detectionHtml}</div>
  `;

  // Bot Action
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

function connectWebSocket() {
  socket = new WebSocket(`ws://${location.host}/ws`);

  socket.onopen = function() {
    console.log('WebSocket connection established');
  };

  socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    updateGameState(data);
  };

  socket.onclose = function() {
    console.log('WebSocket connection closed. Reconnecting in 2s...');
    setTimeout(connectWebSocket, 2000);
  };
}

connectWebSocket();

async function submitCorrection() {
  const input = document.getElementById('correction-input');
  const correctCard = input.value.trim();

  if (!correctCard) {
    alert("Please enter a card code!");
    return;
  }

  await fetch('/correction', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({correct_card: correctCard})
  });

  input.value = '';
}

async function nextPlayer() {
  await fetch('/next_player', {
    method: 'POST'
  });
}

async function pushAction() {
  await fetch('/push', {
    method: 'POST'
  });
}
