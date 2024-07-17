let chatHistory = [];

        function addMessage(message, isUser) {
            const chatMessages = document.getElementById('chatMessages');
            const messageElement = document.createElement('div');
            messageElement.classList.add('message');
            messageElement.classList.add(isUser ? 'user-message' : 'bot-message');
            messageElement.textContent = message;
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function sendMessage() {
            const userInput = document.getElementById('userInput');
            const message = userInput.value.trim();

            if (message) {
                addMessage(message, true);
                chatHistory.push(message);
                userInput.value = '';

                try {
                    console.log("Sending message:", message);
                    const response = await fetch('/query', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ message: message, history: chatHistory }),
                    });

                    console.log("Response received:", response);

                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }

                    const data = await response.json();
                    console.log("Data received:", data);
                    addMessage(data.response, false);
                    chatHistory.push(data.response);

                } catch (error) {
                    console.error('Error:', error);
                    addMessage('Sorry, there was an error processing your request.', false);
                }
            }
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        document.getElementById('userInput').addEventListener('keypress', handleKeyPress);