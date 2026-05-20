export async function getUserData(username) {
    const res = await fetch(`/data/${username}`);
    const data = await res.json();

    return data;
}

export async function analyzeGame(username, game_id) {
    const res = await fetch(`/analysis/${username}/${game_id}`);
    const data = await res.json();

    return data;
}

// http://localhost:3000