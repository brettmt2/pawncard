export async function getUserData(username) {
    const res = await fetch(`http://localhost:3000/data/${username}`);
    const data = await res.json();

    return data;
}