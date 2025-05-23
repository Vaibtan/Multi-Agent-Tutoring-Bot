class ChatInterface {
    constructor() {
        this.messagesArea = document.getElementById('messagesArea');
        this.messageForm = document.getElementById('messageForm');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.errorToast = document.getElementById('errorToast');
        this.init();
    }
    
    init() {
        this.messageForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.messageInput.addEventListener('input', () => this.handleInputChange());
        this.messageInput.focus();
        this.checkSystemHealth();
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        const message = this.messageInput.value.trim(); 
        if (!message) return;
        this.setInputState(false);
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.showTypingIndicator();
        try {
            const response = await this.sendMessage(message);
            this.hideTypingIndicator();
            this.addBotMessage(response);   
        } catch (error) {
            this.hideTypingIndicator();
            this.showError('Failed to get response. Please try again.');
            console.error('Chat error:', error);
        } finally {
            this.setInputState(true);
            this.messageInput.focus();
        }
    }
    
    async sendMessage(message) {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                student_id: this.getStudentId()
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Network error');
        }
        
        return await response.json();
    }
    
    addMessage(text, sender, metadata = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.textContent = text;
        
        const meta = document.createElement('div');
        meta.className = 'message-meta';
        
        if (sender === 'user') {
            meta.innerHTML = `
                <span class="timestamp">${this.formatTime(new Date())}</span>
                <span>You</span>
            `;
        } else if (metadata) {
            meta.innerHTML = `
                <span class="agent-name">${this.formatAgentName(metadata.agent)}</span>
                <span class="timestamp">${this.formatTime(new Date())}</span>
            `;  
            if (metadata.tools_used && metadata.tools_used.length > 0) {
                const toolsDiv = document.createElement('div');
                toolsDiv.className = 'tools-used';
                toolsDiv.innerHTML = `
                    <i class="fas fa-tools"></i> 
                    Tools used: ${metadata.tools_used.join(', ')}
                `;
                content.appendChild(toolsDiv);
            }
        }
        
        content.appendChild(messageText);
        content.appendChild(meta);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        this.messagesArea.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addBotMessage(response) {
        this.addMessage(response.response, 'bot', {
            agent: response.agent,
            subject: response.subject,
            tools_used: response.tools_used
        });
    }
    
    showTypingIndicator() {
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }
    
    setInputState(enabled) {
        this.messageInput.disabled = !enabled;
        this.sendButton.disabled = !enabled;
    }
    
    handleInputChange() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText;
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.messagesArea.scrollTop = this.messagesArea.scrollHeight;
        }, 100);
    }
    
    formatTime(date) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    formatAgentName(agentName) {
        const names = {
            'tutor_orchestrator': 'Tutor Orchestrator',
            'math_specialist': 'Math Specialist',
            'physics_specialist': 'Physics Specialist'
        };
        return names[agentName] || agentName;
    }
    
    getStudentId() {
        let studentId = localStorage.getItem('studentId');
        if (!studentId) {
            studentId = 'web_user_' + Date.now();
            localStorage.setItem('studentId', studentId);
        }
        return studentId;
    }

    showError(message) {
        const errorMessage = document.getElementById('errorMessage');
        errorMessage.textContent = message;
        this.errorToast.style.display = 'flex';
        setTimeout(() => this.hideError(), 5000);
    }
    
    hideError() {
        this.errorToast.style.display = 'none';
    }
    
    async checkSystemHealth() {
        try {
            const response = await fetch('/api/health');
            const health = await response.json();
            
            if (health.status === 'healthy') {
                document.getElementById('agentStatus').innerHTML = `
                    <span class="status-indicator active"></span>
                    <span>System Online</span>
                `;
            }
        } catch (error) {
            document.getElementById('agentStatus').innerHTML = `
                <span class="status-indicator" style="background: #f44336;"></span>
                <span>System Offline</span>
            `;
        }
    }
}

window.hideError = function() {
    document.getElementById('errorToast').style.display = 'none';
};

document.addEventListener('DOMContentLoaded', () => {
    new ChatInterface();
});
