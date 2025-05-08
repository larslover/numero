function joinShift(date, timeSlot, role, button) {
    console.log("Joining shift:", { loggedInUser, loggedInUserId, date, timeSlot, role });

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
        button.textContent = `${loggedInUser} | Avbryt`;
        location.reload();  // ⬅️ Add this line
    })
    .catch(error => {
        console.error('Join failed:', error);
    });
}

function cancelShift(button) {
    const date = button.getAttribute('data-date');
    const timeSlot = button.getAttribute('data-time-slot');
    const role = button.getAttribute('data-role');

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
            button.textContent = "Bli med";
            location.reload();  // ⬅️ Add this line
        }
    })
    .catch(error => {
        console.error('Cancel failed:', error);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    console.log("Logged in user:", loggedInUser);
    console.log("User ID:", loggedInUserId);

    window.csrfToken = document.querySelector('[name=csrf-token]').content;

    document.querySelectorAll('.volunteer-slot').forEach(slot => {
        const date = slot.dataset.date;
        const timeSlot = slot.dataset.timeSlot;
        const role = "volunteer";
        const currentUsers = slot.dataset.users ? slot.dataset.users.split(',') : [];
        const maxSlots = parseInt(slot.dataset.maxSlots, 10);
        const isStaff = slot.dataset.isStaff === "True";
        const userAlreadyJoined = currentUsers.includes(loggedInUser);

        slot.innerHTML = '';

        currentUsers.forEach(user => {
            if (user !== loggedInUser) {
                const nameTag = document.createElement('div');
                nameTag.textContent = user;
                nameTag.className = 'joined-user';
                slot.appendChild(nameTag);
            }
        });

        if (isStaff) {
            const staffTag = document.createElement('div');
            staffTag.textContent = "Ansatt";
            staffTag.className = 'staff-user';
            slot.appendChild(staffTag);
        } else {
            if (userAlreadyJoined) {
                const button = document.createElement("button");
                button.type = "button";
                button.setAttribute("data-date", date);
                button.setAttribute("data-time-slot", timeSlot);
                button.setAttribute("data-role", role);
                button.setAttribute("data-id", `${date}-${timeSlot}-${loggedInUser}`);
                button.className = "joined-btn";
                button.textContent = `${loggedInUser} | Avbryt`;

                slot.appendChild(button);

                button.addEventListener('click', (event) => {
                    event.preventDefault();
                    cancelShift(button);
                });
            } else {
                const remainingSlots = maxSlots - currentUsers.length;
                for (let i = 0; i < remainingSlots; i++) {
                    const button = document.createElement("button");
                    button.type = "button";
                    button.setAttribute("data-date", date);
                    button.setAttribute("data-time-slot", timeSlot);
                    button.setAttribute("data-role", role);
                    button.setAttribute("data-id", `${date}-${timeSlot}-${loggedInUser}-${i}`);
                    button.className = "volunteer-btn";
                    button.textContent = "Bli med";

                    slot.appendChild(button);

                    button.addEventListener('click', (event) => {
                        event.preventDefault();
                        joinShift(date, timeSlot, role, button);
                    });
                }
            }
        }
    });
});
