document.addEventListener("DOMContentLoaded", function () {
    const apiBase = `${window.location.origin}${window.location.pathname.split("/schedule")[0]}/api`;

    const joinButtons = document.querySelectorAll(".join-btn, .joined-btn");

    // Fetch the user's joined shifts
    fetch(`${apiBase}/my_shifts/`)
        .then(response => response.json())
        .then(data => {
            if (data.status === "ok") {
                const joinedShifts = data.shifts;

                joinButtons.forEach(button => {
                    const date = button.getAttribute("data-date");
                    const timeSlotCell = button.closest("tr").querySelector("td:first-child");
                    const timeSlot = timeSlotCell ? timeSlotCell.textContent.trim() : null;

                    const matchedShift = joinedShifts.find(shift =>
                        shift.date === date && shift.time_slot === timeSlot
                    );

                    if (matchedShift) {
                        button.textContent = `👤 ${loggedInUser} | Cancel`;
                        button.classList.remove("join-btn");
                        button.classList.add("joined-btn");
                    }
                });
            }
        });

    // Handle Join / Cancel button clicks
    joinButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            const button = event.target;
            const date = button.getAttribute("data-date");
            const timeSlotCell = button.closest("tr").querySelector("td:first-child");
            const timeSlot = timeSlotCell ? timeSlotCell.textContent.trim() : null;
            const role = "volunteer";

            if (button.classList.contains("joined-btn")) {
                // Cancel shift
                console.log("Sending POST to cancel with:", {
                    username: loggedInUser,
                    date: date,
                    time_slot: timeSlot,
                    role: role
                });

                // Log the cancel URL being requested
                console.log(`${apiBase}/cancel/`);  // Check the URL
                console.log(getCSRFToken());
                fetch(`${apiBase}/cancel/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                    credentials: "same-origin", // added for better CSRF handling
                    body: JSON.stringify({
                        username: loggedInUser,
                        date: date,
                        time_slot: timeSlot,
                        role: role
                    })
                })
                .then(response => response.json())
                .then(data => {
                    console.log("Cancel response:", data);
                    if (data.status === "success") {
                        button.textContent = "Bli med";
                        button.classList.remove("joined-btn");
                        button.classList.add("join-btn");
                    } else {
                        alert(data.message || "Failed to cancel shift.");
                    }
                });

                return; // Ensure the event handler returns after canceling
            }

            // If it's not a joined button, it may be a join button
            fetch(`${apiBase}/join/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: JSON.stringify({
                    username: loggedInUser,
                    date: date,
                    time_slot: timeSlot,
                    role: role
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log("Join response:", data);
                if (data.status === "success" && data.created) {
                    button.textContent = `👤 ${loggedInUser} | Cancel`;
                    button.classList.remove("join-btn");
                    button.classList.add("joined-btn");
                } else {
                    alert(data.message || "Failed to join shift.");
                }
            });
        });
    });

    function getCSRFToken() {
        const token = document.querySelector("meta[name='csrf-token']");
        return token ? token.getAttribute("content") : "";
    }
});
