// Enhanced Chat Interface JavaScript
// AI Product Finder - Modern Chatbot Implementation
// Author: Aditya Tripathi
// Course: AI PBL - 5th Semester

const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const modal = document.getElementById('productModal');
const modalClose = document.getElementsByClassName('modal-close')[0];

// Auto-resize textarea
function autoResize() {
    if (chatInput) {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    }
}

// Add typing indicator
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message-modern typing-indicator';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = `
        <div class="message-avatar-modern">
            <span class="avatar-icon">🤖</span>
        </div>
        <div class="message-content-modern">
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Remove typing indicator
function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Add user message to chat
function addUserMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message-modern user-message';
    messageDiv.innerHTML = `
        <div class="message-avatar-modern">
            <span class="avatar-icon">👤</span>
        </div>
        <div class="message-content-modern">
            <div class="message-header">
                <span class="sender-name">You</span>
                <span class="message-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
            </div>
            <p class="message-text">${message}</p>
            <div class="message-status">
                <span class="status-icon">✓</span>
                <span>Sent</span>
            </div>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Add bot response to chat
function addBotMessage(message) {
    hideTypingIndicator();
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message-modern';
    messageDiv.innerHTML = `
        <div class="message-avatar-modern">
            <span class="avatar-icon">🤖</span>
        </div>
        <div class="message-content-modern">
            <div class="message-header">
                <span class="sender-name">AI Assistant</span>
                <span class="message-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
            </div>
            <p class="message-text">${message}</p>
            <div class="message-status">
                <span class="status-icon">✓</span>
                <span>Delivered</span>
            </div>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Send message function
async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    // Disable send button
    sendBtn.disabled = true;
    sendBtn.innerHTML = '<span class="btn-icon">⏳</span><span class="btn-text">Sending...</span>';
    
    // Add user message
    addUserMessage(message);
    
    // Clear input
    chatInput.value = '';
    autoResize();
    
    // Show typing indicator
    showTypingIndicator();

    try {
        // API call to chat endpoint
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        if (response.ok) {
            const data = await response.json();
            handleChatResponse(data);
        } else {
            hideTypingIndicator();
            addBotMessage('Sorry, I\'m having trouble connecting. Please try again.');
        }
    } catch (error) {
        console.error('Chat error:', error);
        hideTypingIndicator();
        addBotMessage('I\'m currently offline. Please try again later.');
    } finally {
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<span class="btn-icon">📤</span><span class="btn-text">Send</span>';
    }
}

// Modal functionality
if (modalClose) {
    modalClose.onclick = function() {
        modal.style.display = 'none';
    }
}

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}

// Show product details in popup
function showProductDetails(product) {
  const modalBody = document.getElementById('modalBody');
  
  // Get all product fields
  const fields = Object.keys(product);
  const detailsHTML = fields.map(key => {
    if (key === 'price' || key.toLowerCase().includes('price')) {
      return `
        <div class="detail-item">
          <div class="detail-label">${key}</div>
          <div class="detail-value product-price">₹${product[key]}</div>
        </div>
      `;
    }
    return `
      <div class="detail-item">
        <div class="detail-label">${key}</div>
        <div class="detail-value">${product[key] || 'N/A'}</div>
      </div>
    `;
  }).join('');
  
  modalBody.innerHTML = `
    <div class="product-header">
      <div>
        <h2 class="product-title">${product.brand || product.Brand || ''} ${product.model || product.Model || product.name || product.Name || 'Product'}</h2>
      </div>
    </div>
    <div class="product-details">
      ${detailsHTML}
    </div>
  `;
  
  modal.style.display = 'block';
}

// Add message to chat
function addMessage(content, isUser = false) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `chat-message ${isUser ? 'user-message' : 'bot-message'}`;
  
  // Use simple textual avatars for a more professional tone
  const avatar = isUser ? '' : '';
  
  messageDiv.innerHTML = `
    <div class="message-content">
      ${content}
    </div>
  `;
  
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Create product card for chat
function createChatProductCard(product, score) {
  const card = document.createElement('div');
  card.className = 'product-card';
  card.style.cursor = 'pointer';
  
  const brand = product.brand || product.Brand || '';
  const model = product.model || product.Model || product.name || product.Name || product.Title || '';
  
  // Find price from various possible column names
  const price = product.price || product.Price || product.selling_price || 
                product.Selling_Price || product['selling price'] || 
                product['Selling Price'] || product.Actual_Price || 
                product.actual_price || 'N/A';
  
  // Get key specs (exclude common fields)
  const excludeFields = ['brand', 'Brand', 'model', 'Model', 'name', 'Name', 'Title', 
                        'price', 'Price', 'selling_price', 'Selling_Price', 
                        'Actual_Price', 'actual_price', 'selling price', 'Selling Price'];
  const specs = Object.keys(product).filter(key => 
    !excludeFields.includes(key)
  ).slice(0, 2);
  
  const specsHTML = specs.map(key => `
    <div class="detail-item">
      <div class="detail-label">${key}</div>
      <div class="detail-value">${product[key] || 'N/A'}</div>
    </div>
  `).join('');
  
  const imageHTML = product.image ? `<div class="product-thumb-wrap"><img class="product-thumb" src="${product.image}" alt="${model}"/></div>` : '';

  card.innerHTML = `
    <div class="product-header">
      ${imageHTML}
      <div>
        <div class="product-title">${model}</div>
        <div class="product-brand">${brand}</div>
      </div>
      <div class="product-price">₹${price}</div>
    </div>
    <div class="product-details">
      ${specsHTML}
    </div>
    <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #666;">
      Relevance: ${(score * 100).toFixed(1)}%
    </div>
  `;
  
  card.addEventListener('click', () => {
    showProductDetails(product);
  });
  
  return card;
}

// Use suggestion function
function useSuggestion(text) {
  if (chatInput) {
    chatInput.value = text;
    chatInput.focus();
    autoResize();
    sendMessage();
  }
}

// Enhanced message handling for chat results
function handleChatResponse(data) {
    hideTypingIndicator();
    
    if (data.error) {
        addBotMessage(`❌ ${data.error}`);
        return;
    }
    
    // Create response message
    let responseContent = data.response || 'I found some results for you!';
    
    // Add suggestions if available
    if (data.suggestions && data.suggestions.length > 0) {
        const suggestionsHTML = data.suggestions.map(suggestion => 
            `<span class="suggestion-chip-modern" onclick="useSuggestion('${suggestion.replace(/'/g, "\\'")}')">${suggestion}</span>`
        ).join('');
        responseContent += `
            <div class="suggestions-modern" style="margin-top: 1rem;">
                <p class="suggestions-label-modern">Try asking:</p>
                <div class="suggestion-chips">
                    ${suggestionsHTML}
                </div>
            </div>
        `;
    }
    
    // Add bot message
    addBotMessage(responseContent);
    
    // Add products if available
    if (data.results && data.results.length > 0) {
        const productsGrid = document.createElement('div');
        productsGrid.className = 'chat-products-grid';
        productsGrid.style.cssText = `
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        `;
        
        data.results.forEach(hit => {
            const product = hit.data || hit.row || hit;
            const score = hit.score || 0;
            productsGrid.appendChild(createChatProductCard(product, score));
        });
        
        const productMessageDiv = document.createElement('div');
        productMessageDiv.className = 'chat-message-modern';
        productMessageDiv.innerHTML = `
            <div class="message-avatar-modern">
                <span class="avatar-icon">🤖</span>
            </div>
            <div class="message-content-modern">
                <div class="message-header">
                    <span class="sender-name">AI Assistant</span>
                    <span class="message-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                </div>
            </div>
        `;
        
        productMessageDiv.querySelector('.message-content-modern').appendChild(productsGrid);
        chatMessages.appendChild(productMessageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Event listeners setup
document.addEventListener('DOMContentLoaded', function() {
    // Auto-resize textarea on input
    if (chatInput) {
        chatInput.addEventListener('input', autoResize);
        
        // Send on Enter key (without Shift)
        chatInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    // Send button click
    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }

    // Suggestion chip clicks
    document.querySelectorAll('.suggestion-chip-modern').forEach(chip => {
        chip.addEventListener('click', function() {
            chatInput.value = this.textContent.replace(/"/g, '');
            autoResize();
            sendMessage();
        });
    });

    // Initial setup
    autoResize();
});

