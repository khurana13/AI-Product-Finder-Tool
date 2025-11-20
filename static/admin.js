// Admin Page JavaScript

// Show toast notification
function showToast(message, duration = 3000) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.add('show');
  
  setTimeout(() => {
    toast.classList.remove('show');
  }, duration);
}

// Show result in admin card
function showResult(elementId, message, isSuccess = true) {
  const resultDiv = document.getElementById(elementId);
  resultDiv.className = `admin-result ${isSuccess ? 'success' : 'error'}`;
  resultDiv.textContent = message;
  resultDiv.style.display = 'block';
  
  setTimeout(() => {
    resultDiv.style.display = 'none';
  }, 5000);
}

// Get admin token
function getAdminToken() {
  return document.getElementById('adminToken').value.trim();
}

// Rebuild index
async function rebuildIndex() {
  const token = getAdminToken();
  
  if (!token) {
    showResult('rebuildResult', 'Please enter admin token', false);
    return;
  }
  
  const btn = document.getElementById('rebuildBtn');
  btn.disabled = true;
  btn.textContent = '🔄 Rebuilding...';
  
  try {
    const response = await fetch('/admin/rebuild', {
      method: 'POST',
      headers: {
        'X-Admin-Token': token
      }
    });
    
    const data = await response.json();
    
    if (response.ok) {
      showResult('rebuildResult', data.message || 'Index rebuilt successfully!', true);
      showToast('✅ Index rebuilt successfully!');
    } else {
      showResult('rebuildResult', data.error || 'Failed to rebuild index', false);
    }
  } catch (error) {
    showResult('rebuildResult', `Error: ${error.message}`, false);
  } finally {
    btn.disabled = false;
    btn.textContent = '🔄 Rebuild Search Index';
  }
}

// Rotate token
async function rotateToken() {
  const token = getAdminToken();
  
  if (!token) {
    showResult('rotateResult', 'Please enter current admin token', false);
    return;
  }
  
  const btn = document.getElementById('rotateBtn');
  btn.disabled = true;
  btn.textContent = '🔑 Rotating...';
  
  try {
    const response = await fetch('/admin/rotate', {
      method: 'POST',
      headers: {
        'X-Admin-Token': token
      }
    });
    
    const data = await response.json();
    
    if (response.ok) {
      const newToken = data.new_token || 'See server logs';
      showResult('rotateResult', `New token: ${newToken}`, true);
      showToast('✅ Token rotated successfully!');
      
      // Update token field with new token
      document.getElementById('adminToken').value = newToken;
    } else {
      showResult('rotateResult', data.error || 'Failed to rotate token', false);
    }
  } catch (error) {
    showResult('rotateResult', `Error: ${error.message}`, false);
  } finally {
    btn.disabled = false;
    btn.textContent = '🔑 Rotate Admin Token';
  }
}

// Reset password
async function resetPassword() {
  const token = getAdminToken();
  const username = document.getElementById('newUsername').value.trim();
  const password = document.getElementById('newPassword').value.trim();
  
  if (!token) {
    showResult('resetResult', 'Please enter admin token', false);
    return;
  }
  
  if (!username || !password) {
    showResult('resetResult', 'Please enter both username and password', false);
    return;
  }
  
  const btn = document.getElementById('resetBtn');
  btn.disabled = true;
  btn.textContent = '🔒 Resetting...';
  
  try {
    const response = await fetch('/admin/reset_password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Token': token
      },
      body: JSON.stringify({
        new_username: username,
        new_password: password
      })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      showResult('resetResult', data.message || 'Password reset successfully!', true);
      showToast('✅ Password reset successfully!');
      
      // Clear password fields
      document.getElementById('newUsername').value = '';
      document.getElementById('newPassword').value = '';
    } else {
      showResult('resetResult', data.error || 'Failed to reset password', false);
    }
  } catch (error) {
    showResult('resetResult', `Error: ${error.message}`, false);
  } finally {
    btn.disabled = false;
    btn.textContent = '🔒 Reset Password';
  }
}

// Event listeners
document.getElementById('rebuildBtn').addEventListener('click', rebuildIndex);
document.getElementById('rotateBtn').addEventListener('click', rotateToken);
document.getElementById('resetBtn').addEventListener('click', resetPassword);

// Allow Enter key in password field
document.getElementById('newPassword').addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    resetPassword();
  }
});
