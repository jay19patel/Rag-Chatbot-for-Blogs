class ChatApp {
    constructor() {
        this.currentSessionId = 'default';
        this.isLoading = false;
        this.chatSessions = JSON.parse(localStorage.getItem('chatSessions') || '[]');
        this.recentBlogs = [];
        this.isSearchMode = false;
        this.searchTimeout = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadRecentBlogs();
        this.autoResizeTextarea();
    }

    setupEventListeners() {
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const newChatBtn = document.getElementById('newChatBtn');
        const closeBlogModal = document.getElementById('closeBlogModal');
        const toggleSearchBtn = document.getElementById('toggleSearchBtn');
        const searchInput = document.getElementById('searchInput');
        const clearSearchBtn = document.getElementById('clearSearchBtn');

        // Message input events
        messageInput.addEventListener('input', () => {
            sendBtn.disabled = !messageInput.value.trim();
            this.autoResizeTextarea();
        });

        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Search functionality
        toggleSearchBtn.addEventListener('click', () => this.toggleSearchMode());

        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            clearSearchBtn.classList.toggle('hidden', !query);

            // Clear previous timeout
            if (this.searchTimeout) {
                clearTimeout(this.searchTimeout);
            }

            // Debounce search
            this.searchTimeout = setTimeout(() => {
                if (query) {
                    this.performSearch(query);
                } else {
                    this.showNoResults(false);
                    this.loadRecentBlogs();
                }
            }, 300);
        });

        clearSearchBtn.addEventListener('click', () => {
            searchInput.value = '';
            clearSearchBtn.classList.add('hidden');
            this.loadRecentBlogs();
            searchInput.focus();
        });

        // Button events
        sendBtn.addEventListener('click', () => this.sendMessage());
        newChatBtn.addEventListener('click', () => this.startNewChat());
        closeBlogModal.addEventListener('click', () => this.closeBlogModal());

        // Modal events
        document.getElementById('blogModal').addEventListener('click', (e) => {
            if (e.target.id === 'blogModal') {
                this.closeBlogModal();
            }
        });
    }

    autoResizeTextarea() {
        const textarea = document.getElementById('messageInput');
        textarea.style.height = 'auto';
        const newHeight = Math.min(textarea.scrollHeight, 120);
        textarea.style.height = newHeight + 'px';
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();

        if (!message || this.isLoading) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        messageInput.value = '';
        messageInput.style.height = '44px';
        document.getElementById('sendBtn').disabled = true;

        // Show typing indicator
        this.showTypingIndicator();
        this.isLoading = true;

        try {
            const response = await fetch('/api/v1/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.currentSessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Remove typing indicator
            this.hideTypingIndicator();

            // Add AI response to chat
            this.addMessage(data.response, 'ai');

            // Update session
            this.updateCurrentSession(message, data.response);

        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'ai', true);
            console.error('Error sending message:', error);
        } finally {
            this.isLoading = false;
        }
    }

    addMessage(content, sender, isError = false) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex items-start space-x-3 mb-4 message-enter`;

        if (sender === 'user') {
            messageDiv.innerHTML = `
                <div class="flex-1 flex justify-end">
                    <div class="bg-blue-600 text-white rounded-lg p-4 shadow-sm max-w-lg">
                        <p class="whitespace-pre-wrap">${this.escapeHtml(content)}</p>
                    </div>
                </div>
                <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <i class="fas fa-user text-blue-600 text-sm"></i>
                </div>
            `;
        } else {
            const bgColor = isError ? 'bg-red-50 border border-red-200' : 'bg-white';
            const textColor = isError ? 'text-red-800' : 'text-gray-800';

            messageDiv.innerHTML = `
                <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                    <i class="fas fa-robot text-white text-sm"></i>
                </div>
                <div class="${bgColor} rounded-lg p-4 shadow-sm max-w-2xl">
                    <div class="${textColor} whitespace-pre-wrap">${this.formatMessage(content)}</div>
                    ${!isError ? this.addActionButtons(content) : ''}
                </div>
            `;
        }

        chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatMessage(content) {
        // Convert markdown-like formatting to HTML
        let formatted = this.escapeHtml(content);

        // Bold text
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Headers
        formatted = formatted.replace(/^### (.*$)/gm, '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>');
        formatted = formatted.replace(/^## (.*$)/gm, '<h2 class="text-xl font-semibold mt-4 mb-2">$1</h2>');
        formatted = formatted.replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold mt-4 mb-2">$1</h1>');

        // Lists
        formatted = formatted.replace(/^\* (.*$)/gm, '<li class="ml-4">• $1</li>');
        formatted = formatted.replace(/^- (.*$)/gm, '<li class="ml-4">• $1</li>');

        return formatted;
    }

    addActionButtons(content) {
        // Check if the message contains blog-like content
        const hasBlogContent = content.toLowerCase().includes('blog') ||
                              content.toLowerCase().includes('title') ||
                              content.length > 500;

        if (hasBlogContent) {
            return `
                <div class="mt-3 pt-3 border-t border-gray-200 flex space-x-2">
                    <button class="save-blog-btn bg-green-100 hover:bg-green-200 text-green-800 text-xs font-medium px-3 py-1 rounded-full transition-colors duration-200">
                        <i class="fas fa-save mr-1"></i>
                        Save Blog
                    </button>
                    <button class="preview-blog-btn bg-blue-100 hover:bg-blue-200 text-blue-800 text-xs font-medium px-3 py-1 rounded-full transition-colors duration-200">
                        <i class="fas fa-eye mr-1"></i>
                        Preview
                    </button>
                </div>
            `;
        }
        return '';
    }

    showTypingIndicator() {
        const chatMessages = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typingIndicator';
        typingDiv.className = 'flex items-start space-x-3 mb-4';
        typingDiv.innerHTML = `
            <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <i class="fas fa-robot text-white text-sm"></i>
            </div>
            <div class="bg-white rounded-lg p-4 shadow-sm">
                <div class="flex space-x-1">
                    <div class="typing-indicator"></div>
                    <div class="typing-indicator"></div>
                    <div class="typing-indicator"></div>
                </div>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    startNewChat() {
        this.currentSessionId = 'session_' + Date.now();
        document.getElementById('chatMessages').innerHTML = this.getWelcomeMessage();
        document.getElementById('chatTitle').textContent = 'New Blog Creation';
        this.saveChatSession('New Chat', '', '');
        this.loadChatSessions();
    }

    updateCurrentSession(userMessage, aiResponse) {
        const sessionIndex = this.chatSessions.findIndex(s => s.id === this.currentSessionId);
        const title = userMessage.length > 50 ? userMessage.substring(0, 50) + '...' : userMessage;

        if (sessionIndex !== -1) {
            this.chatSessions[sessionIndex] = {
                ...this.chatSessions[sessionIndex],
                title: title,
                lastMessage: aiResponse.substring(0, 100) + (aiResponse.length > 100 ? '...' : ''),
                timestamp: new Date().toISOString()
            };
        } else {
            this.saveChatSession(title, userMessage, aiResponse);
        }

        localStorage.setItem('chatSessions', JSON.stringify(this.chatSessions));
        this.loadChatSessions();
    }

    saveChatSession(title, userMessage, aiResponse) {
        const session = {
            id: this.currentSessionId,
            title: title,
            lastMessage: aiResponse.substring(0, 100) + (aiResponse.length > 100 ? '...' : ''),
            timestamp: new Date().toISOString()
        };

        this.chatSessions.unshift(session);
        if (this.chatSessions.length > 10) {
            this.chatSessions = this.chatSessions.slice(0, 10);
        }

        localStorage.setItem('chatSessions', JSON.stringify(this.chatSessions));
    }

    async loadRecentBlogs() {
        this.showLoading(true);
        try {
            console.log('Fetching recent blogs...');
            const response = await fetch('/api/v1/blogs?limit=10');

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('API Response:', data);

            this.recentBlogs = data.blogs || [];

            if (this.recentBlogs.length === 0) {
                this.showNoResults(true, 'No blogs found in database');
            } else {
                this.displayBlogs(this.recentBlogs);
            }
        } catch (error) {
            console.error('Error loading recent blogs:', error);
            this.showNoResults(true, `Failed to load blogs: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    toggleSearchMode() {
        this.isSearchMode = !this.isSearchMode;
        const searchContainer = document.getElementById('searchContainer');
        const toggleBtn = document.getElementById('toggleSearchBtn');
        const sectionTitle = document.getElementById('sectionTitle');
        const searchInput = document.getElementById('searchInput');

        if (this.isSearchMode) {
            searchContainer.classList.remove('hidden');
            toggleBtn.innerHTML = '<i class="fas fa-times mr-1"></i>Cancel';
            sectionTitle.textContent = 'Search Blogs';
            searchInput.focus();
        } else {
            searchContainer.classList.add('hidden');
            toggleBtn.innerHTML = '<i class="fas fa-search mr-1"></i>Search';
            sectionTitle.textContent = 'Recent Blogs';
            searchInput.value = '';
            document.getElementById('clearSearchBtn').classList.add('hidden');
            this.loadRecentBlogs();
        }
    }

    async performSearch(query) {
        this.showLoading(true);
        try {
            console.log('Searching for:', query);
            const response = await fetch(`/api/v1/blogs/search?q=${encodeURIComponent(query)}&limit=10`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('Search results:', data);

            if (!data.results || data.results.length === 0) {
                this.showNoResults(true, `No blogs found for "${query}"`);
            } else {
                this.displayBlogs(data.results, true);
            }
        } catch (error) {
            console.error('Error searching blogs:', error);
            this.showNoResults(true, `Search failed: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    displayBlogs(blogs, isSearchResult = false) {
        const container = document.getElementById('contentContainer');
        container.innerHTML = '';

        if (!blogs || blogs.length === 0) {
            this.showNoResults(true, 'No blogs found');
            return;
        }

        blogs.forEach(blog => {
            const blogDiv = document.createElement('div');
            blogDiv.className = 'p-3 rounded-lg cursor-pointer transition-colors duration-200 hover:bg-gray-50 border border-gray-100 hover:border-gray-200';

            const date = blog.created_at ? new Date(blog.created_at).toLocaleDateString() : 'Unknown date';
            const title = blog.title || 'Untitled Blog';
            // Use excerpt for list view, content for search results
            const preview = blog.excerpt || (blog.content ? blog.content.substring(0, 80) + (blog.content.length > 80 ? '...' : '') : 'No content available');

            blogDiv.innerHTML = `
                <div class="text-sm font-medium text-gray-800 truncate">${this.escapeHtml(title)}</div>
                <div class="text-xs text-gray-600 mt-1 truncate">${this.escapeHtml(preview)}</div>
                <div class="flex items-center justify-between mt-2">
                    <div class="text-xs text-gray-500">${date}</div>
                    ${isSearchResult && blog.relevance_score ?
                        `<div class="text-xs text-blue-600">${Math.round(blog.relevance_score * 100)}% match</div>` :
                        ''
                    }
                </div>
                ${blog.category ? `<div class="text-xs text-purple-600 mt-1">#${blog.category}</div>` : ''}
            `;

            blogDiv.addEventListener('click', () => {
                this.loadBlogToChat(blog);
            });

            container.appendChild(blogDiv);
        });

        this.showNoResults(false);
    }

    async loadBlogToChat(blog) {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = this.getWelcomeMessage();

        // If we have the blog_id, fetch full content first
        if (blog.blog_id && !blog.content) {
            this.addMessage(`Show me the blog: "${blog.title}"`, 'user');
            this.showTypingIndicator();

            try {
                // For now, show the excerpt/available content
                const blogInfo = `**${blog.title}**\n\n${blog.excerpt || 'No content preview available'}\n\nBlog ID: ${blog.blog_id}\nCategory: ${blog.category || 'Uncategorized'}\nCreated: ${blog.created_at ? new Date(blog.created_at).toLocaleDateString() : 'Unknown'}`;

                this.hideTypingIndicator();
                this.addMessage(blogInfo, 'ai');
                this.addMessage('I can help you edit this blog, create a new version, or discuss its content. What would you like to do?', 'ai');
            } catch (error) {
                this.hideTypingIndicator();
                this.addMessage('Sorry, I could not load the full blog content.', 'ai', true);
            }
        } else {
            // Use available content
            this.addMessage(`Show me this blog: "${blog.title}"`, 'user');
            this.addMessage(blog.content || blog.excerpt || 'Blog content not available', 'ai');
        }

        document.getElementById('chatTitle').textContent = blog.title || 'Blog Discussion';
        this.currentSessionId = 'blog_' + (blog.blog_id || blog._id || Date.now());
    }

    showLoading(show) {
        const loadingIndicator = document.getElementById('loadingIndicator');
        const contentContainer = document.getElementById('contentContainer');

        if (show) {
            loadingIndicator.classList.remove('hidden');
            contentContainer.classList.add('hidden');
        } else {
            loadingIndicator.classList.add('hidden');
            contentContainer.classList.remove('hidden');
        }
    }

    showNoResults(show, message = 'No blogs found') {
        const noResultsMessage = document.getElementById('noResultsMessage');
        const contentContainer = document.getElementById('contentContainer');

        if (show) {
            noResultsMessage.classList.remove('hidden');
            noResultsMessage.querySelector('p').textContent = message;
            contentContainer.classList.add('hidden');
        } else {
            noResultsMessage.classList.add('hidden');
            contentContainer.classList.remove('hidden');
        }
    }

    loadChatSessions() {
        // This method is now replaced by loadRecentBlogs for database content
        this.loadRecentBlogs();
    }

    async viewAllBlogs() {
        try {
            const response = await fetch('/api/v1/blogs?limit=20');
            if (!response.ok) throw new Error('Failed to fetch blogs');

            const data = await response.json();
            this.showBlogsModal(data.blogs, 'All Saved Blogs');
        } catch (error) {
            console.error('Error fetching blogs:', error);
            this.addMessage('Failed to fetch blogs. Please try again.', 'ai', true);
        }
    }

    showSearchBlogs() {
        const query = prompt('Enter search query for blogs:');
        if (!query) return;

        this.searchBlogs(query);
    }

    async searchBlogs(query) {
        try {
            const response = await fetch(`/api/v1/blogs/search?q=${encodeURIComponent(query)}&limit=10`);
            if (!response.ok) throw new Error('Failed to search blogs');

            const data = await response.json();
            this.showBlogsModal(data.results, `Search Results for "${query}"`);
        } catch (error) {
            console.error('Error searching blogs:', error);
            this.addMessage('Failed to search blogs. Please try again.', 'ai', true);
        }
    }

    showBlogsModal(blogs, title) {
        const modal = document.getElementById('blogModal');
        const content = document.getElementById('blogContent');

        let html = `<h2 class="text-xl font-bold mb-4">${title}</h2>`;

        if (blogs.length === 0) {
            html += '<p class="text-gray-600">No blogs found.</p>';
        } else {
            html += '<div class="space-y-4">';
            blogs.forEach(blog => {
                const date = blog.created_at ? new Date(blog.created_at).toLocaleDateString() : 'Unknown date';
                html += `
                    <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow duration-200">
                        <h3 class="font-semibold text-lg text-gray-800">${this.escapeHtml(blog.title || 'Untitled')}</h3>
                        <p class="text-gray-600 mt-2">${this.escapeHtml((blog.content || '').substring(0, 200))}${blog.content && blog.content.length > 200 ? '...' : ''}</p>
                        <div class="mt-3 flex items-center justify-between text-sm text-gray-500">
                            <span>${date}</span>
                            ${blog.relevance_score ? `<span>Relevance: ${Math.round(blog.relevance_score * 100)}%</span>` : ''}
                        </div>
                    </div>
                `;
            });
            html += '</div>';
        }

        content.innerHTML = html;
        modal.classList.remove('hidden');
    }

    closeBlogModal() {
        document.getElementById('blogModal').classList.add('hidden');
    }

    getWelcomeMessage() {
        return `
            <div class="flex items-start space-x-3 mb-6">
                <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                    <i class="fas fa-robot text-white text-sm"></i>
                </div>
                <div class="bg-white rounded-lg p-4 shadow-sm max-w-lg">
                    <p class="text-gray-800">Hello! I'm your AI blog creation assistant. I can help you:</p>
                    <ul class="mt-2 text-sm text-gray-600 space-y-1">
                        <li>• Create engaging blog posts on any topic</li>
                        <li>• Generate ideas and outlines</li>
                        <li>• Write, edit, and improve content</li>
                        <li>• Save your blogs to the database</li>
                    </ul>
                    <p class="mt-3 text-gray-800">What kind of blog would you like to create today?</p>
                </div>
            </div>
        `;
    }
}

// Initialize the chat app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});