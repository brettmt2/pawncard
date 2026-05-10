import { getUserData } from './api.js';

function generateUserProfileSection(data) {
    if (data === null) return;

    document.getElementById('pfp').src = data['pfp'];
    document.getElementById('username-subtitle').textContent = data['username'];
    document.getElementById('location-subtitle').textContent = data['location'] || '';

    document.getElementById('followers-count').textContent = data['followers'] || '';

    const country = document.getElementById('country');
    country.src = data['flag'] || '';
    country.style.display = data['flag'] ? 'block' : 'none';
}

function generateUserStatsSection(data) {
    if (data === null) return;

    if (data['rapid'] != null) {
        const dataRapid = data['rapid'];
        document.getElementById('rating-rapid').textContent = dataRapid['curr_rating'];
        document.getElementById('record-rapid').textContent = dataRapid['record'];
    }

    if (data['blitz'] != null) {
        const dataBlitz = data['blitz'];
        document.getElementById('rating-blitz').textContent = dataBlitz['curr_rating'];
        document.getElementById('record-blitz').textContent = dataBlitz['record'];
    }

    if (data['bullet'] != null) {
        const dataBullet = data['bullet'];
        document.getElementById('rating-bullet').textContent = dataBullet['curr_rating'];
        document.getElementById('record-bullet').textContent = dataBullet['record'];
    }
}

function generateChessBoard(fen, feed_id, container, win_color) {
    const div = document.createElement('div');
    div.id = "board-" + feed_id;
    div.style.width = '260px';
    container.appendChild(div);

    window.Chessboard("board-" + feed_id, {
        position: fen,
        pieceTheme: './static/pieces/{piece}.png',
        showNotation: false,
        orientation: win_color
    });
}

function generateFeedItemSummary(feed_item_data, username) {
    const div = document.createElement('div');
    div.className = 'feed-summary';

    const user_rating = feed_item_data.new_rating || '-';
    const opponent_username = feed_item_data.opponent.username;
    const opponent_rating = feed_item_data.opponent.rating;
    const win_con = feed_item_data.win_condition;
    const win_color = feed_item_data.win_color;

    let accuracyHTML = '';
    if (feed_item_data['accuracies']) {
        const acc = feed_item_data['accuracies'];
        accuracyHTML = `
            <div class="feed-accuracies">
                <span class="feed-accuracy"><span class="acc-bubble white-bubble"></span>${acc['white']}%</span>
                <span class="feed-accuracy"><span class="acc-bubble black-bubble"></span>${acc['black']}%</span>
            </div>
        `;
    }

    const topPlayer = win_color === 'white'
    ? `<span class="feed-player you">${username} (${user_rating})</span>`
    : `<span class="feed-player opp">${opponent_username} (${opponent_rating})</span>`;

    const bottomPlayer = win_color === 'white'
        ? `<span class="feed-player opp">${opponent_username} (${opponent_rating})</span>`
        : `<span class="feed-player you">${username} (${user_rating})</span>`;

    div.innerHTML = `
        <div class="feed-matchup">
            ${topPlayer}
            <span class="feed-vs">vs</span>
            ${bottomPlayer}
        </div>

        <span class="feed-win">${win_color.charAt(0).toUpperCase() + win_color.slice(1)} wins</span>

        <span class="feed-condition">${win_con}</span>

        ${accuracyHTML}
    `;

    return div;
}

function generateUserFeed(data, username) {
    document.getElementById('feed').innerHTML = '';
    document.getElementById('feed').removeAttribute('hidden');

    const header = document.createElement('div');
    header.className = 'feed-header';
    header.innerHTML = '<h2 class="feed-title">Check out some of my recent wins!</h2>';
    document.getElementById('feed').appendChild(header);

    data.forEach(item => {
        const card = document.createElement('div');
        card.className = 'feed-card';
        card.id = item['feed_id'];

        const timeIcon = document.createElement('img');
        timeIcon.src = `https://www.chess.com/bundles/web/images/color-icons/${item['time_class']}.svg`;
        timeIcon.className = 'feed-time-icon';
        timeIcon.alt = item['time_class'];
        card.appendChild(timeIcon);

        const leftSection = document.createElement('div');
        leftSection.className = 'feed-left';

        const rightSection = document.createElement('div');
        rightSection.className = 'feed-right';

        card.appendChild(leftSection);
        card.appendChild(rightSection);

        document.getElementById('feed').appendChild(card);

        generateChessBoard(item['fen'], item['feed_id'], leftSection, item['win_color']);

        const summary = generateFeedItemSummary(item, username);
        rightSection.appendChild(summary);
    });
}

async function generate(username){
    username = username.trim()
    if (!username) return;

    const res = await getUserData(username);

    console.log(res);

    if (!res || !res['summary']) return;

    generateUserProfileSection(res['summary']);
    generateUserStatsSection(res['summary']['stats']);

    if (!res['feed'] || res['feed'].length < 1) {
        document.getElementById('feed').innerHTML = '';
        document.getElementById('feed').textContent = 'No recent highlights for this user.'
        return;
    }

    generateUserFeed(res['feed'], username);
}

let usernameInput = document.getElementById('username-input');
let searchButton = document.getElementById('search-btn');

searchButton.addEventListener('click', () => generate(usernameInput.value));
usernameInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') generate(usernameInput.value);
});

const downloadButton = document.getElementById('download-btn');
const pawncard = document.getElementById('pawncard');

downloadButton.addEventListener('click', () => {
    downloadButton.style.visibility = 'hidden';
    document.getElementById('chess-logo').style.display = 'block';
    document.getElementById('pawncard-banner').style.display = 'flex';

    html2canvas(pawncard, {useCORS: true, backgroundColor: '#3a3837'}).then((canvas) => {
        const image = canvas.toDataURL("image/png")

        const link = document.createElement('a');
        link.href = image;
        link.download = 'pawncard.png';

        link.click();
        downloadButton.style.visibility = 'visible';
        document.getElementById('pawncard-banner').style.display = 'none';
        document.getElementById('chess-logo').style.display = 'none';
    });
});