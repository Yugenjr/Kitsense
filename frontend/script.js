const apiBase = 'http://127.0.0.1:8000';
let currentIdentifier = '';

const chatWindow = document.getElementById('chatWindow');
const kitMeta = document.getElementById('kitMeta');

const fallbackKits = {
  'RX-101': {
    kit_id: 'RX-101',
    kit_name: 'Line Follower Robot',
    age_group: '10-14',
    difficulty: 'Beginner',
    next_questions: [
      'Do you need help with body making?',
      'Are you assembling parts or building the circuit?',
      'Would you like a story-based explanation first?'
    ]
  },
  'ORD-2201': {
    kit_id: 'RX-202',
    kit_name: 'Obstacle Avoider Robot',
    age_group: '12-16',
    difficulty: 'Intermediate',
    next_questions: [
      'Do you need help with body making?',
      'Are you assembling parts or building the circuit?',
      'Would you like a story-based explanation first?'
    ]
  }
};

function addBubble(text, role = 'bot') {
  const div = document.createElement('div');
  div.className = `bubble ${role}`;
  div.textContent = text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function buildFallbackReply(message) {
  const text = message.toLowerCase();
  if (text.includes('circuit') || text.includes('wire') || text.includes('sensor')) {
    return 'For Circuit Building: Connect sensors and motor driver using color-coded wires. Story card: Your robot is learning to read track signals and move with precision.';
  }
  return 'For Body Making: Assemble chassis, fix motors symmetrically, and tighten wheel mounts. Story card: You are designing a stable robot frame for smooth movement.';
}

function applySessionState(data) {
  kitMeta.textContent = `Kit: ${data.kit_name} | Age: ${data.age_group} | Difficulty: ${data.difficulty}`;
  addBubble(`Welcome to ${data.kit_name}. ${data.next_questions.join(' ')}`);
}

async function startSession() {
  const identifier = document.getElementById('identifier').value.trim();
  if (!identifier) return;

  currentIdentifier = identifier;

  try {
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
    applySessionState(data);
  } catch {
    const key = identifier.toUpperCase();
    const fallback = fallbackKits[key] || fallbackKits['RX-101'];
    applySessionState(fallback);
  }
}

async function sendMessage() {
  const input = document.getElementById('message');
  const message = input.value.trim();
  if (!message || !currentIdentifier) return;

  addBubble(message, 'user');
  input.value = '';

  try {
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
  } catch {
    addBubble(buildFallbackReply(message));
  }
}

document.getElementById('startBtn').addEventListener('click', startSession);
document.getElementById('sendBtn').addEventListener('click', sendMessage);
