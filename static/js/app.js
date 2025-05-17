document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const messagesContainer = document.getElementById('messages');
    const chatHistory = document.getElementById('chat-history');
    const webSearchToggle = document.getElementById('web-search-toggle');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    
    let currentChatId = Date.now().toString();
    let webSearchEnabled = false; // Default to disabled
    let isMobile = window.innerWidth <= 768;
    
    // Setup UI based on device size
    function setupUIForDeviceSize() {
        isMobile = window.innerWidth <= 768;
        
        // On desktop, make sure sidebar is visible and properly positioned
        if (!isMobile && sidebar) {
            sidebar.classList.remove('show'); // Remove the mobile-specific class
            sidebar.style.display = 'block'; // Ensure it's visible
            sidebar.style.left = '0'; // Ensure it's positioned correctly
            document.removeEventListener('click', closeSidebarOnClickOutside);
        }
    }
    
    // Run initial UI setup
    setupUIForDeviceSize();
    
    // Handle sidebar toggle for mobile devices
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
            // When sidebar is shown, add click event to close it when clicking outside
            if (sidebar.classList.contains('show')) {
                setTimeout(function() {
                    document.addEventListener('click', closeSidebarOnClickOutside);
                }, 10);
            }
        });
    }
    
    // Function to close sidebar when clicking outside on mobile
    function closeSidebarOnClickOutside(event) {
        if (!sidebar.contains(event.target) && event.target !== sidebarToggle) {
            sidebar.classList.remove('show');
            document.removeEventListener('click', closeSidebarOnClickOutside);
        }
    }
    
    // Initialize web search toggle state
    if (webSearchToggle) {
        webSearchToggle.checked = webSearchEnabled;
        
        // Add event listener for toggle changes
        webSearchToggle.addEventListener('change', function() {
            webSearchEnabled = this.checked;
            console.log('Web search ' + (webSearchEnabled ? 'enabled' : 'disabled'));
        });
    }
    
    // Load chat history when page loads
    loadChatHistory();
    
    // Fix for Android keyboard issues affecting viewport
    let viewportHeight = window.innerHeight;
    window.addEventListener('resize', function() {
        // If height decreased significantly (keyboard appeared)
        if (window.innerHeight < viewportHeight * 0.75) {
            document.body.classList.add('keyboard-open');
        } else {
            document.body.classList.remove('keyboard-open');
        }
        viewportHeight = window.innerHeight;
        
        // Handle layout changes on resize
        setupUIForDeviceSize();
    });
    
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
        
        // Close sidebar on mobile if open
        if (isMobile && sidebar.classList.contains('show')) {
            sidebar.classList.remove('show');
            document.removeEventListener('click', closeSidebarOnClickOutside);
        }
        
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
    
    // Function to load chat history from server
    function loadChatHistory() {
        fetch('/api/chat/history')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to load chat history');
                }
                return response.json();
            })
            .then(data => {
                if (data.messages && data.messages.length > 0) {
                    // Remove welcome message if present
                    const welcomeMessage = document.querySelector('.welcome-message');
                    if (welcomeMessage && welcomeMessage.parentNode === messagesContainer) {
                        messagesContainer.removeChild(welcomeMessage);
                    }
                    
                    // Display messages in the UI
                    data.messages.forEach(msg => {
                        const role = msg.role === 'model' ? 'ai' : 'user';
                        addMessage(msg.content, role);
                    });
                    
                    // Update sidebar with latest chat
                    const lastUserMessage = data.messages.filter(msg => msg.role === 'user').pop();
                    if (lastUserMessage) {
                        updateChatHistory(lastUserMessage.content);
                    }
                }
            })
            .catch(error => {
                console.error('Error loading chat history:', error);
            });
    }
    
    // Add message to UI with improved mobile handling
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
            
            // Make links open in new tabs
            messageDiv.querySelectorAll('a').forEach(link => {
                link.setAttribute('target', '_blank');
                link.setAttribute('rel', 'noopener noreferrer');
            });
            
            // Make images responsive
            messageDiv.querySelectorAll('img').forEach(img => {
                img.style.maxWidth = '100%';
                img.style.height = 'auto';
            });
        } else {
            messageDiv.textContent = text;
        }
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Fix for Android not scrolling properly
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 100);
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
    
    // Support for keyboard shortcuts and better mobile keyboard handling
    userInput.addEventListener('keydown', function(event) {
        // Submit on Enter (unless Shift is held, which allows for new lines)
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
    
    // Handle window resize to toggle mobile view
    window.addEventListener('resize', function() {
        isMobile = window.innerWidth <= 768;
        
        // Reset sidebar visibility when switching between mobile and desktop
        if (!isMobile && sidebar) {
            sidebar.classList.remove('show');
            document.removeEventListener('click', closeSidebarOnClickOutside);
        }
    });
    
    // Check for Android
    const isAndroid = /Android/i.test(navigator.userAgent);
    if (isAndroid) {
        document.body.classList.add('android-device');
        
        // Additional fixes for Android keyboard issues
        userInput.addEventListener('focus', function() {
            setTimeout(function() {
                window.scrollTo(0, 0);
                document.body.scrollTop = 0;
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }, 300);
        });
        
        userInput.addEventListener('blur', function() {
            setTimeout(function() {
                window.scrollTo(0, 0);
                document.body.scrollTop = 0;
            }, 300);
        });
    }
});
