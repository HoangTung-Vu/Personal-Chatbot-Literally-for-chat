document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const messagesContainer = document.getElementById('messages');
    const chatHistory = document.getElementById('chat-history');
    const webSearchToggle = document.getElementById('web-search-toggle');
    
    let currentChatId = Date.now().toString();
    let webSearchEnabled = true; // Default to enabled
    
    // Initialize web search toggle state
    if (webSearchToggle) {
        webSearchToggle.checked = webSearchEnabled;
        
        // Add event listener for toggle changes
        webSearchToggle.addEventListener('change', function() {
            webSearchEnabled = this.checked;
            console.log('Web search ' + (webSearchEnabled ? 'enabled' : 'disabled'));
        });
    }
    
    // Auto-resize textarea as user types
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        // Limit to 5 rows max
        if (this.scrollHeight > 150) {
            this.style.height = '150px';
        }
    });
    
    // Handle form submission
    chatForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const message = userInput.value.trim();
        if (!message) return;
        
        // Add user message to UI
        addMessage(message, 'user');
        
        // Clear input
        userInput.value = '';
        userInput.style.height = 'auto';
        
        // Show typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.innerHTML = '<span></span><span></span><span></span>';
        messagesContainer.appendChild(typingIndicator);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Call API
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                message, 
                web_search_enabled: webSearchEnabled 
            }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Remove typing indicator
            messagesContainer.removeChild(typingIndicator);
            
            // Add AI response to UI
            addMessage(data.response, 'ai');
            
            // If web search was used, indicate that in the UI
            if (data.used_web_search) {
                const webSearchIndicator = document.createElement('div');
                webSearchIndicator.className = 'web-search-indicator';
                webSearchIndicator.textContent = 'Web search was used to generate this response';
                messagesContainer.appendChild(webSearchIndicator);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
            // Update chat history if not already there
            updateChatHistory(message);
        })
        .catch(error => {
            // Remove typing indicator
            messagesContainer.removeChild(typingIndicator);
            
            // Show error message
            const errorMessage = document.createElement('div');
            errorMessage.className = 'ai-message error';
            errorMessage.textContent = 'Sorry, there was an error processing your request. Please try again.';
            messagesContainer.appendChild(errorMessage);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            
            console.error('Error:', error);
        });
    });
    
    // Add message to UI
    function addMessage(text, sender) {
        // Remove welcome message if present
        const welcomeMessage = document.querySelector('.welcome-message');
        if (welcomeMessage && welcomeMessage.parentNode === messagesContainer) {
            messagesContainer.removeChild(welcomeMessage);
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = sender + '-message';
        
        // If AI message, render markdown
        if (sender === 'ai') {
            const marked = window.marked; // Declare the marked variable
            messageDiv.innerHTML = marked.parse(text);
            
            // Apply syntax highlighting to code blocks
            messageDiv.querySelectorAll('pre code').forEach((block) => {
                block.innerHTML = block.innerHTML
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#039;');
            });
        } else {
            messageDiv.textContent = text;
        }
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Update chat history sidebar
    function updateChatHistory(message) {
        // Check if chat already exists in sidebar
        let existingChat = false;
        
        // If not, add new chat to sidebar
        if (!existingChat) {
            const listItem = document.createElement('li');
            // Truncate message if too long
            const truncatedMessage = message.length > 30 ? message.substring(0, 30) + '...' : message;
            listItem.textContent = truncatedMessage;
            listItem.dataset.id = currentChatId;
            
            chatHistory.insertBefore(listItem, chatHistory.firstChild);
        }
    }
    
    // Support for keyboard shortcuts
    userInput.addEventListener('keydown', function(event) {
        // Submit on Enter (unless Shift is held, which allows for new lines)
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
});
