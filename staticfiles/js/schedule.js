function joinShift(date, timeSlot, role, button) {
    fetch('/en/api/join/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        credentials: 'include',
        body: JSON.stringify({
            user_id: loggedInUserId,
            date: date,
            time_slot: timeSlot,
            role: role
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Shift joined successfully:', data);
        button.classList.remove('volunteer-btn');
        button.classList.add('joined-btn');
        button.textContent = 'Avbryt';
    })
    .catch(error => console.error('Join failed:', error));
}

function cancelShift(button) {
    const date = button.dataset.date;
    const timeSlot = button.dataset.timeSlot;
    const role = button.dataset.role;

    fetch('/en/api/cancel/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            user_id: loggedInUserId,
            date: date,
            time_slot: timeSlot,
            role: role
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Shift canceled:', data);
        if (data.status === 'success') {
            button.classList.remove('joined-btn');
            button.classList.add('volunteer-btn');
            button.textContent = 'Bli med';
        }
    })
    .catch(error => console.error('Cancel failed:', error));
}

document.addEventListener('DOMContentLoaded', () => {
    const csrfToken = document.querySelector('[name=csrf-token]').content;
    const loggedInUser = "{{ request.user.username|escapejs }}";
    const loggedInUserId = "{{ request.user.id }}";

    function joinShift(date, timeSlot, role, button) {
        fetch('/en/api/join/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
            credentials: 'include',
            body: JSON.stringify({ user_id: loggedInUserId, date: date, time_slot: timeSlot, role: role })
        })
        .then(res => res.json())
        .then(data => {
            button.classList.remove('volunteer-btn');
            button.classList.add('joined-btn');
            button.textContent = 'Avbryt';
        })
        .catch(err => console.error(err));
    }

    function cancelShift(button) {
        const date = button.dataset.date;
        const timeSlot = button.dataset.timeSlot;
        const role = button.dataset.role;

        fetch('/en/api/cancel/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
            body: JSON.stringify({ user_id: loggedInUserId, date: date, time_slot: timeSlot, role: role })
        })
        .then(res => res.json())
        .then(data => {
            button.classList.remove('joined-btn');
            button.classList.add('volunteer-btn');
            button.textContent = 'Bli med';
        })
        .catch(err => console.error(err));
    }

    document.querySelectorAll('.volunteer-slot').forEach(slot => {
        const date = slot.dataset.date;
        const timeSlot = slot.dataset.timeSlot;
        const role = slot.dataset.role;
        const currentUsers = slot.dataset.users ? slot.dataset.users.split(',') : [];
        const userAlreadyJoined = slot.dataset.userJoined === 'true';

        slot.textContent = '';

        // Show other users
        currentUsers.forEach(user => {
            const div = document.createElement('div');
            div.className = 'joined-user';
            div.textContent = user;
            slot.appendChild(div);
        });

        // Add one button per slot
        const button = document.createElement('button');
        button.type = 'button';
        button.dataset.date = date;
        button.dataset.timeSlot = timeSlot;
        button.dataset.role = role;

        if (userAlreadyJoined) {
            button.className = 'joined-btn';
            button.textContent = 'Avbryt';
            button.addEventListener('click', e => { e.preventDefault(); cancelShift(button); });
        } else {
            button.className = 'volunteer-btn';
            button.textContent = 'Bli med';
            button.addEventListener('click', e => { e.preventDefault(); joinShift(date, timeSlot, role, button); });
        }

        slot.appendChild(button);
    });
});
