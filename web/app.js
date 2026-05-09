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

        document.getElementById('download-btn').addEventListener('click', async () => {
            const btn = document.getElementById('download-btn');
            const banner = document.querySelector('.pawncard-banner');
            
            btn.style.visibility = 'hidden';
            banner.style.display = 'flex';

            const canvas = await html2canvas(pawncard, { 
                useCORS: true, 
                backgroundColor: '#3a3837' 
            });

            btn.style.visibility = 'visible';
            banner.style.display = 'none';

            const link = document.createElement('a');
            link.download = 'pawncard.png';
            link.href = canvas.toDataURL();
            link.click();
        });

        pawncard.hidden = false;

        const feedContainer = document.getElementById('feed');

        if (data['feed'] && data['feed'].length > 0) {
            feedContainer.hidden = false;
            feedContainer.innerHTML = '';

            data['feed'].forEach((item, index) => {
                const boardId = `board-${index}`;

                const card = document.createElement('div');
                card.className = 'feed-card';

                // left: chess board
                const boardDiv = document.createElement('div');
                boardDiv.id = boardId;
                boardDiv.className = 'feed-board';

                // right: game info
                const infoDiv = document.createElement('div');
                infoDiv.className = 'feed-info';

                const timeClassIcon = `https://www.chess.com/bundles/web/images/color-icons/${item.time_class}.svg`;

                const resultLabel = item.win_color.charAt(0).toUpperCase() + item.win_color.slice(1) + ' wins';

                infoDiv.innerHTML = `
                    <img src="${timeClassIcon}" class="feed-time-icon" />
                    <div class="feed-matchup">
                        <div class="feed-player-row">
                            <span class="feed-player">${data['summary']['username']}</span>
                            <span class="feed-rating">${data['summary']['stats'][item.time_class]?.curr_rating ?? '—'}</span>
                        </div>
                        <span class="feed-vs">vs</span>
                        <div class="feed-player-row">
                            <span class="feed-player">${item.opponent.username}</span>
                            <span class="feed-rating">${item.opponent.rating}</span>
                        </div>
                    </div>
                    <div class="feed-result">
                        <span class="feed-result-label">${resultLabel}</span>
                        <span class="feed-result-condition">${item.win_condition}</span>
                    </div>
                    <div class="feed-accuracy">
                        <span class="feed-accuracy-item white">♔ ${item.accuracies.white}%</span>
                        <span class="feed-accuracy-item black">♚ ${item.accuracies.black}%</span>
                    </div>
                `;

                card.appendChild(boardDiv);
                card.appendChild(infoDiv);
                feedContainer.appendChild(card);

                Chessboard(boardId, {
                    position: item.fen,
                    pieceTheme: './static/pieces/{piece}.png',
                    showNotation: false
                });
            });
        }

    } catch (err) {
        console.error(err.message);
    }
}

button.addEventListener('click', search);
input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') search();
});