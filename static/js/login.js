document.addEventListener('DOMContentLoaded', function() {

    // ── If already logged in → skip to select-topic ──
    var existingToken = localStorage.getItem('access_token');
    if (existingToken) {
        window.location.href = '/select-topic/';
        return;
    }

    var loginForm = document.getElementById('loginForm');
    var alertBox  = document.getElementById('alertBox');
    var loginBtn  = document.getElementById('loginBtn');

    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
        });
    }

    if (loginBtn) {
        loginBtn.addEventListener('click', function() {
            loginUser();
        });
    }

    async function loginUser() {
        var username = document.getElementById('username').value.trim();
        var password = document.getElementById('password').value;

        if (!username) { showError('Enter username!'); return; }
        if (!password) { showError('Enter password!'); return; }

        loginBtn.disabled    = true;
        loginBtn.textContent = 'Logging in...';

        try {
            var res = await fetch('https://aiglms-learnora-production.up.railway.app/api/auth/login/', {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            var data = await res.json();
            console.log('Login response:', data);

            if (!res.ok) {
                showError(data.error || 'Invalid credentials!');
                loginBtn.disabled    = false;
                loginBtn.textContent = 'Login';
                return;
            }

            // Save tokens — stays until logout!
            localStorage.setItem('access_token',  data.tokens.access);
            localStorage.setItem('refresh_token', data.tokens.refresh);
            localStorage.setItem('username',      data.user.username);
            localStorage.setItem('user_id',       data.user.id);

            console.log('Login successful! Redirecting...');

            // Login → Select Topic
            window.location.href = '/select-topic/';

        } catch(err) {
            console.error('Login error:', err);
            showError('Connection failed!');
            loginBtn.disabled    = false;
            loginBtn.textContent = 'Login';
        }
    }

    function showError(msg) {
        if (alertBox) {
            alertBox.textContent   = msg;
            alertBox.style.display = 'block';
        }
    }
});