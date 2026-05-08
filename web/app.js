import { getUserData } from './api.js';

const input = document.getElementById('username-input');
const button = document.getElementById('search-btn');
const output = document.getElementById('json-output');

async function search() {
    const username = input.value.trim();
    if (!username) return;

    output.textContent = 'Loading...'

    try {
        const data = await getUserData(username);
        if (data['summary'] === null) {
            output.textContent = "Sorry, can't find data for this profile!"
            return;
        }

        document.getElementById('username-display').textContent = data['summary']['username'];
        
        const pfp = document.getElementById('pfp');
        pfp.src = data['summary']['pfp'];
        pfp.hidden = false;

        if (data['feed'].length === 0) {
            output.textContent = "No games found for this profile."
            return;
        }

        output.textContent = JSON.stringify(data, null, 2);
    } catch (err) {
        output.textContent = `Error: ${err.message}`;
    }
}

button.addEventListener('click', search);

input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') search();
});