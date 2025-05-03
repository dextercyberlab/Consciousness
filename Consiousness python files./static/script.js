// static/script.js
// Real-time notifications
const eventSource = new EventSource('/notifications-stream');

eventSource.onmessage = (event) => {
    const notification = JSON.parse(event.data);
    addNotification(notification);
};

function addNotification(notification) {
    const notificationsDiv = document.getElementById('notifications');
    const div = document.createElement('div');
    div.className = 'notification';
    div.innerHTML = `<strong>${notification.time}</strong>: ${notification.message}`;
    notificationsDiv.appendChild(div);
    notificationsDiv.scrollTop = notificationsDiv.scrollHeight;
}

// Chat functionality
async function askQuestion() {
    const input = document.getElementById('question-input');
    const question = input.value.trim();
    if (!question) return;

    const chatHistory = document.getElementById('chat-history');
    const questionDiv = document.createElement('div');
    questionDiv.className = 'chat-message question';
    questionDiv.textContent = `You: ${question}`;
    chatHistory.appendChild(questionDiv);

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({question})
        });
        
        const data = await response.json();
        const answerDiv = document.createElement('div');
        answerDiv.className = 'chat-message answer';
        answerDiv.innerHTML = `<strong>AI:</strong> ${data.answer}`;
        chatHistory.appendChild(answerDiv);
    } catch (error) {
        console.error('Error:', error);
    }
    
    input.value = '';
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Summary loading
async function loadSummary() {
    try {
        const response = await fetch('/get-summary');
        const summary = await response.text();
        document.getElementById('summary').textContent = summary;
    } catch (error) {
        console.error('Error loading summary:', error);
        document.getElementById('summary').textContent = "Failed to load summary.";
    }
}

// Load initial summary
loadSummary();

// Handle Enter key in chat
document.getElementById('question-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        askQuestion();
    }
});