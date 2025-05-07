document.addEventListener('DOMContentLoaded', () => {
    console.log("Logged in user:", loggedInUser);
    console.log("User ID:", loggedInUserId);

    const csrfToken = document.querySelector('[name=csrf-token]').content;

    // ✅ REPLACEMENT: volunteer-slot button and user display
    document.querySelectorAll('.volunteer-slot').forEach(slot => {
        const date = slot.dataset.date;
        const timeSlot = slot.dataset.timeSlot;
        const role = "volunteer";
        const currentUsers = slot.dataset.users ? slot.dataset.users.split(',') : [];
        const maxSlots = parseInt(slot.dataset.maxSlots, 10);
        const isStaff = slot.dataset.isStaff === "True";  // Checking if the user is a staff member (Ansatt)
        const userAlreadyJoined = currentUsers.includes(loggedInUser);

        slot.innerHTML = '';

        // Render non-logged-in users as names
        currentUsers.forEach(user => {
            if (user !== loggedInUser) {
                const nameTag = document.createElement('div');
                nameTag.textContent = user;
                nameTag.className = 'joined-user';
                slot.appendChild(nameTag);
            }
        });

        // If user is staff, display their name without a button (Ansatt)
        if (isStaff) {
            const staffTag = document.createElement('div');
            staffTag.textContent = "Ansatt";  // Show text for staff users
            staffTag.className = 'staff-user';
            slot.appendChild(staffTag);
        } else {
            // Render volunteer button for users who aren't staff
            if (userAlreadyJoined || currentUsers.length < maxSlots) {
                const button = document.createElement("button");
                button.type = "button";
                button.setAttribute("data-date", date);
                button.setAttribute("data-time-slot", timeSlot);
                button.setAttribute("data-role", role);
                button.setAttribute("data-id", `${date}-${timeSlot}-${loggedInUser}`);
                button.setAttribute("draggable", "true");

                if (userAlreadyJoined) {
                    button.className = "joined-btn";
                    button.textContent = `${loggedInUser} | Avbryt`;
                } else {
                    button.className = "volunteer-btn";
                    button.textContent = "Bli med";
                }

                slot.appendChild(button);

                button.addEventListener('dragstart', handleDragStart);
                button.addEventListener('click', (event) => {
                    event.preventDefault();
                    if (button.classList.contains('volunteer-btn')) {
                        joinShift(date, timeSlot, role, button);
                    } else if (button.classList.contains('joined-btn')) {
                        cancelShift(button);
                    }
                });
            }
        }
    });

    // 🔁 Keep the rest
    document.querySelectorAll('.volunteer-drop-target').forEach(slot => {
        slot.addEventListener('dragover', handleDragOver);
        slot.addEventListener('drop', handleDrop);
    });

   


    function handleDrop(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('drag-over');

        const dataId = event.dataTransfer.getData('text/plain');
        const droppedButton = document.querySelector(`[data-id="${dataId}"]`);
        if (!droppedButton) return;

        const newDate = event.currentTarget.dataset.date;
        const newTimeSlot = event.currentTarget.dataset.timeSlot;
        const role = droppedButton.dataset.role;

        joinShift(newDate, newTimeSlot, role, droppedButton);
    }

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
            }
        })
        .catch(error => {
            console.error('Cancel failed:', error);
        });
    }
});
