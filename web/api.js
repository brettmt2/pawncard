export async function getUserData(username) {
    const res = await fetch(`/data/${username}`);
    const data = await res.json();

    return data;
}

// http://localhost:3000