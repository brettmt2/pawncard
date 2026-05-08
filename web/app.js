import { getUserData } from './api.js';

const input = document.getElementById('username-input');
const button = document.getElementById('search-btn');
const pawncard = document.getElementById('pawncard');

async function search() {
    const username = input.value.trim();
    if (!username) return;

    pawncard.hidden = true;

    try {
        const data = await getUserData(username);
        if (data['summary'] === null) return;

        console.log(data);

        document.getElementById('username-display').textContent = data['summary']['username'];
        document.getElementById('pfp').src = data['summary']['pfp'];
        document.getElementById('stat-followers').textContent = data['summary']['followers'];
        document.getElementById('stat-country').src = data['summary']['flag'];
        
        const stats = data['summary']['stats'];

        document.getElementById('rating-rapid').textContent = stats['rapid']['curr_rating'] ?? '—';
        document.getElementById('rating-blitz').textContent = stats['blitz']['curr_rating'] ?? '—';
        document.getElementById('rating-bullet').textContent = stats['bullet']['curr_rating'] ?? '—';

        document.getElementById('record-bullet').textContent = stats['bullet']['record'] ?? '—';
        document.getElementById('record-blitz').textContent = stats['blitz']['record'] ?? '—';
        document.getElementById('record-rapid').textContent = stats['rapid']['record'] ?? '—';

        pawncard.hidden = false;
    } catch (err) {
        console.error(err.message);
    }
}

button.addEventListener('click', search);
input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') search();
});