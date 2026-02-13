const apiBase = 'http://127.0.0.1:8000';
let currentIdentifier = '';

const chatWindow = document.getElementById('chatWindow');
const kitMeta = document.getElementById('kitMeta');

function addBubble(text, role = 'bot') {
  const div = document.createElement('div');
  div.className = `bubble ${role}`;
  div.textContent = text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function startSession() {
  const identifier = document.getElementById('identifier').value.trim();
  if (!identifier) return;

  const res = await fetch(`${apiBase}/api/session/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ identifier })
  });

  if (!res.ok) {
    addBubble('Could not find kit. Please verify your Order ID / Kit ID.');
    return;
  }

  const data = await res.json();
  currentIdentifier = identifier;
  kitMeta.textContent = `Kit: ${data.kit_name} | Age: ${data.age_group} | Difficulty: ${data.difficulty}`;
  addBubble(`Welcome to ${data.kit_name}. ${data.next_questions.join(' ')}`);
}

async function sendMessage() {
  const input = document.getElementById('message');
  const message = input.value.trim();
  if (!message || !currentIdentifier) return;

  addBubble(message, 'user');
  input.value = '';

  const res = await fetch(`${apiBase}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ identifier: currentIdentifier, message })
  });

  if (!res.ok) {
    addBubble('I had trouble generating guidance. Try again.');
    return;
  }

  const data = await res.json();
  addBubble(`${data.response} [Stage: ${data.predicted_stage} | Confidence: ${data.confidence}]`);
}

document.getElementById('startBtn').addEventListener('click', startSession);
document.getElementById('sendBtn').addEventListener('click', sendMessage);
