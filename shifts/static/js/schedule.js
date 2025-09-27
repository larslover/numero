document.addEventListener('DOMContentLoaded', () => {
    const csrfToken = document.querySelector('[name=csrf-token]').content;
    const loggedInUser = "{{ request.user.username|escapejs }}";
    const loggedInUserId = "{{ request.user.id }}";

    // Helper to update a volunteer slot
    function updateSlot(slot) {
        const date = slot.dataset.date;
        const timeSlot = slot.dataset.timeSlot;
        const role = slot.dataset.role;
        const maxSlots = parseInt(slot.dataset.maxSlots, 10);
        let currentUsers = slot.dataset.users ? slot.dataset.users.split(',') : [];

        slot.innerHTML = '';

        // Show existing users except logged in user
        currentUsers.forEach(user => {
            if (user !== loggedInUser) {
                const nameTag = document.createElement('div');
                nameTag.className = 'joined-user';
                nameTag.textContent = user;
                slot.appendChild(nameTag);
            }
        });

        const userAlreadyJoined = currentUsers.includes(loggedInUser);

        // Show button for logged in user
        if (!userAlreadyJoined && currentUsers.length < maxSlots) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'btn btn-outline-primary btn-sm volunteer-btn';
            btn.textContent = 'Bli frivillig';
            slot.appendChild(btn);

            btn.addEventListener('click', () => joinShift(slot, btn));
        }

        if (userAlreadyJoined) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'btn btn-success btn-sm joined-btn';
            btn.textContent = `${loggedInUser} | Avbryt`;
            slot.appendChild(btn);

            btn.addEventListener('click', () => cancelShift(slot, btn));
        }
    }

    function joinShift(slot, button) {
        const date = slot.dataset.date;
        const timeSlot = slot.dataset.timeSlot;
        const role = slot.dataset.role;

        fetch('/en/api/join/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
            body: JSON.stringify({ user_id: loggedInUserId, date, time_slot: timeSlot, role })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                let currentUsers = slot.dataset.users ? slot.dataset.users.split(',') : [];
                currentUsers.push(loggedInUser);
                slot.dataset.users = currentUsers.join(',');
                updateSlot(slot);
            }
        })
        .catch(err => console.error('Join failed:', err));
    }

    function cancelShift(slot, button) {
        const date = slot.dataset.date;
        const timeSlot = slot.dataset.timeSlot;
        const role = slot.dataset.role;

        fetch('/en/api/cancel/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
            body: JSON.stringify({ user_id: loggedInUserId, date, time_slot: timeSlot, role })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                let currentUsers = slot.dataset.users ? slot.dataset.users.split(',') : [];
                currentUsers = currentUsers.filter(u => u !== loggedInUser);
                slot.dataset.users = currentUsers.join(',');
                updateSlot(slot);
            }
        })
        .catch(err => console.error('Cancel failed:', err));
    }

    // Initialize all volunteer slots (desktop + mobile)
    document.querySelectorAll('.volunteer-slot').forEach(slot => {
        updateSlot(slot);
    });
});
