export async function fetchMessages() {
    const response = await fetch('/api/messages');
    if (response.ok) {
        return await response.json();
    } else {
        console.error("Failed to fetch messages:", response.statusText);
        return [];
    }
}

export async function postMessage(username, content) {
    const response = await fetch('/api/messages', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, content })
    });
    if (response.ok) {
        return await response.json();
    } else {
        console.error("Failed to post message:", response.statusText);
        return null;
    }
}

export async function fetchActiveUsers(username) {
    const response = await fetch(`/api/active-users?username=${username}`);
    if (response.ok) {
        const data = await response.json();
        return Array.isArray(data.users) ? data.users : [];
    } else {
        console.error("Failed to fetch active users:", response.statusText);
        return [];
    }
}
