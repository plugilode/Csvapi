// Check authentication status
function checkAuth() {
    const token = localStorage.getItem('jwt_token');
    if (token) {
        fetch('/auth/user', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Authentication failed');
        })
        .then(user => {
            document.getElementById('auth-section').innerHTML = `
                <span class="navbar-text me-3">Welcome, ${user.email}</span>
                <button class="btn btn-outline-light" onclick="logout()">Logout</button>
            `;
            document.getElementById('upload-section').style.display = 'block';
        })
        .catch(() => {
            localStorage.removeItem('jwt_token');
            updateAuthUI();
        });
    } else {
        updateAuthUI();
    }
}

function updateAuthUI() {
    document.getElementById('auth-section').innerHTML = `
        <a href="/auth/login" class="btn btn-outline-light me-2">Login</a>
        <a href="/auth/register" class="btn btn-light">Register</a>
    `;
    document.getElementById('upload-section').style.display = 'none';
}

function logout() {
    localStorage.removeItem('jwt_token');
    window.location.href = '/';
}

// Add authentication headers to fetch requests
function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem('jwt_token');
    if (token) {
        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };
    }
    return fetch(url, options);
}

// Initialize auth check
document.addEventListener('DOMContentLoaded', checkAuth);
