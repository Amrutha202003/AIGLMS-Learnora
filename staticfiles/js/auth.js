// ── Global Auth Helper ──

function getToken() {
    return localStorage.getItem('access_token');
}

function getUsername() {
    return localStorage.getItem('username') || 'Student';
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('username');
    localStorage.removeItem('user_id');
    localStorage.removeItem('selected_topic_id');
    localStorage.removeItem('selected_topic_name');
    localStorage.removeItem('session_id');
    window.location.href = '/login/';
}

function checkAuth() {
    var token = getToken();
    if (!token) {
        window.location.href = '/login/';
        return false;
    }
    return true;
}

// At top of login page script only
function checkLoginPage() {
    var token = localStorage.getItem('access_token');
    if (token) {
        // Already logged in → go to select topic
        window.location.href = '/select-topic/';
    }
}
// Auto refresh token if expired
async function refreshToken() {
    var refresh = localStorage.getItem('refresh_token');
    if (!refresh) {
        logout();
        return null;
    }

    try {
        var res = await fetch('/api/auth/token/refresh/', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ refresh: refresh })
        });

        var data = await res.json();
        if (res.ok && data.access) {
            localStorage.setItem('access_token', data.access);
            return data.access;
        } else {
            logout();
            return null;
        }
    } catch(err) {
        console.error('Refresh failed:', err);
        logout();
        return null;
    }
}

// Smart fetch — auto refreshes token on 401
async function authFetch(url, options) {
    options = options || {};
    options.headers = options.headers || {};
    options.headers['Authorization'] = 'Bearer ' + getToken();

    var res = await fetch(url, options);

    // Token expired — refresh and retry
    if (res.status === 401) {
        console.log('Token expired, refreshing...');
        var newToken = await refreshToken();

        if (newToken) {
            options.headers['Authorization'] = 'Bearer ' + newToken;
            res = await fetch(url, options);
        }
    }

    return res;
}