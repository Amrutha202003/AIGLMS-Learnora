const API_BASE = 'https://aiglms-learnora-production.up.railway.app';

// Get token from localStorage
const token = localStorage.getItem('access_token');
const username = localStorage.getItem('username') || 'Student';

// State
let selectedSubjectId = null;
let selectedSubjectName = '';
let selectedTopicId = null;
let selectedTopicName = '';

// ─────────────────────────────────────────
// ON PAGE LOAD
// ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // Show username
    const welcomeText = document.getElementById('welcomeText');
    if (welcomeText)
        welcomeText.textContent = 'Welcome, ' + username + '!';

    // Redirect to login if no token
    if (!token) {
        window.location.href = '/login/';
        return;
    }

    loadSubjects();

    // Back to subjects button
    document.getElementById('backToSubjects')
        .addEventListener('click', showSubjectSection);

    // Play button
    document.getElementById('playBtn')
        .addEventListener('click', startGame);
});

// ─────────────────────────────────────────
// LOAD SUBJECTS
// ─────────────────────────────────────────
async function loadSubjects() {
    showLoading();

    try {
        const res = await fetch(
            `${API_BASE}/api/academics/subjects/`, {
            headers: { 'Authorization': 'Bearer ' + token }
        });

        if (!res.ok) {
            if (res.status === 401) {
                // Token expired — go to login
                window.location.href = '/login/';
                return;
            }
            throw new Error('Failed to load subjects');
        }

        const subjects = await res.json();
        console.log('Subjects:', subjects);

        if (!subjects || subjects.length === 0) {
            showError('No subjects available yet!');
            return;
        }

        showContent();
        renderSubjects(subjects);

    } catch (err) {
        console.error('Load subjects error:', err);
        showError('Could not load subjects. ' +
            'Is Django running?');
    }
}

// ─────────────────────────────────────────
// RENDER SUBJECTS
// ─────────────────────────────────────────
function renderSubjects(subjects) {
    const grid = document.getElementById('subjectGrid');
    grid.innerHTML = '';

    // Subject emoji icons
    const icons = ['📚', '🔬', '📐', '🌍', '🎨',
        '🎵', '💻', '📝', '🧮', '🏛️'];

    subjects.forEach((subject, i) => {
        const card = document.createElement('div');
        card.className = 'subject-card';
        card.innerHTML = `
            <div class="card-icon">
                ${icons[i % icons.length]}
            </div>
            <h3 class="card-title">${subject.name}</h3>
            <p class="card-subtitle">
                Click to see topics
            </p>
        `;

        card.addEventListener('click', () => {
            selectedSubjectId   = subject.id;
            selectedSubjectName = subject.name;
            loadTopics(subject.id, subject.name);
        });

        grid.appendChild(card);
    });
}

// ─────────────────────────────────────────
// LOAD TOPICS FOR SUBJECT
// ─────────────────────────────────────────
async function loadTopics(subjectId, subjectName) {
    // Show topic section
    document.getElementById('subjectSection')
        .classList.add('hidden');
    document.getElementById('topicSection')
        .classList.remove('hidden');
    document.getElementById('selectedSubjectName')
        .textContent = subjectName;

    const topicGrid = document.getElementById('topicGrid');
    topicGrid.innerHTML =
        '<div class="loading-inline">Loading topics...</div>';

    try {
        const res = await  fetch(
          `${API_BASE}/api/academics/subjects/${subjectId}/topics/`, {
            headers: { 'Authorization': 'Bearer ' + token }
        });

        if (!res.ok)
            throw new Error('Failed to load topics');

        const topics = await res.json();
        console.log('Topics:', topics);

        if (!topics || topics.length === 0) {
            topicGrid.innerHTML =
                '<p class="no-data">No topics available!</p>';
            return;
        }

        renderTopics(topics);

    } catch (err) {
        console.error('Load topics error:', err);
        topicGrid.innerHTML =
            '<p class="no-data">Could not load topics!</p>';
    }
}

// ─────────────────────────────────────────
// RENDER TOPICS
// ─────────────────────────────────────────
function renderTopics(topics) {
    const grid = document.getElementById('topicGrid');
    grid.innerHTML = '';

    const difficultyColors = {
        'EASY':   '#22c55e',
        'MEDIUM': '#f59e0b',
        'HARD':   '#ef4444'
    };

    topics.forEach(topic => {
        const color = difficultyColors[
            topic.difficulty_level] || '#6366f1';

        const card = document.createElement('div');
        card.className = 'topic-card';
        card.innerHTML = `
            <div class="topic-difficulty"
                style="background:${color}">
                ${topic.difficulty_level || 'ALL'}
            </div>
            <h3 class="card-title">${topic.name}</h3>
            <p class="card-subtitle">
                Tap to select this topic
            </p>
        `;

        card.addEventListener('click', () => {
            // Remove active from others
            document.querySelectorAll('.topic-card')
                .forEach(c => c.classList.remove('active'));
            card.classList.add('active');

            selectedTopicId   = topic.id;
            selectedTopicName = topic.name;

            // Show selected panel
            showSelectedPanel();
        });

        grid.appendChild(card);
    });
}

// ─────────────────────────────────────────
// SHOW SELECTED PANEL
// ─────────────────────────────────────────
function showSelectedPanel() {
    const panel = document.getElementById('selectedPanel');
    panel.classList.remove('hidden');

    document.getElementById('displaySubject')
        .textContent = selectedSubjectName;
    document.getElementById('displayTopic')
        .textContent = selectedTopicName;

    const playBtn = document.getElementById('playBtn');
    playBtn.disabled = false;
    playBtn.textContent =
        'Play "' + selectedTopicName + '"!';
}

// ─────────────────────────────────────────
// START GAME — CREATE SESSION
// ─────────────────────────────────────────
async function startGame() {
    if (!selectedTopicId || !selectedSubjectId) {
        alert('Please select a topic first!');
        return;
    }

    const playBtn = document.getElementById('playBtn');
    playBtn.disabled    = true;
    playBtn.textContent = 'Starting game...';

    try {
        // Create game session
        const res = await  fetch(`${API_BASE}/api/game/start-session/`, {
            method:  'POST',
            headers: {
                'Content-Type':  'application/json',
                'Authorization': 'Bearer ' + token
            },
            body: JSON.stringify({
                subject_id:    selectedSubjectId,
                topic_id:      selectedTopicId,
                num_questions: 5
            })
        });

        const json = await res.json();
        console.log('Session started:', json);

        if (!res.ok) {
            playBtn.disabled    = false;
            playBtn.textContent =
                'Play "' + selectedTopicName + '"!';
            alert('Could not start session: ' +
                (json.error || 'Unknown error'));
            return;
        }

        // Save selection to localStorage for Unity
        localStorage.setItem('selected_topic_id',
            selectedTopicId);
        localStorage.setItem('selected_topic_name',
            selectedTopicName);
        localStorage.setItem('selected_subject_id',
            selectedSubjectId);
        localStorage.setItem('session_id',
            json.session_id);

        playBtn.textContent = 'Launching game...';

        // Redirect to game launch page
        setTimeout(() => {
            window.location.href = '/dashboard/';
        }, 500);

    } catch (err) {
        console.error('Start game error:', err);
        playBtn.disabled    = false;
        playBtn.textContent =
            'Play "' + selectedTopicName + '"!';
        alert('Connection failed!');
    }
}

// ─────────────────────────────────────────
// UI HELPERS
// ─────────────────────────────────────────
function showLoading() {
    document.getElementById('loadingDiv')
        .classList.remove('hidden');
    document.getElementById('errorDiv')
        .classList.add('hidden');
    document.getElementById('contentDiv')
        .classList.add('hidden');
}

function showContent() {
    document.getElementById('loadingDiv')
        .classList.add('hidden');
    document.getElementById('errorDiv')
        .classList.add('hidden');
    document.getElementById('contentDiv')
        .classList.remove('hidden');
}

function showError(msg) {
    document.getElementById('loadingDiv')
        .classList.add('hidden');
    document.getElementById('errorDiv')
        .classList.remove('hidden');
    document.getElementById('contentDiv')
        .classList.add('hidden');
    document.getElementById('errorMsg')
        .textContent = msg;
}

function showSubjectSection() {
    document.getElementById('topicSection')
        .classList.add('hidden');
    document.getElementById('subjectSection')
        .classList.remove('hidden');
    document.getElementById('selectedPanel')
        .classList.add('hidden');

    // Reset selection
    selectedTopicId   = null;
    selectedTopicName = '';
}