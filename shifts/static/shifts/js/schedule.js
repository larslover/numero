document.addEventListener("DOMContentLoaded", function () {
    const joinButtons = document.querySelectorAll(".join-btn, .joined-btn");

    // First: Fetch the user's joined shifts on page load
    fetch("/api/my_shifts/")
        .then(response => response.json())
        .then(data => {
            if (data.status === "ok") {
                const joinedShifts = data.shifts;  // List of shifts the user has joined

                // Loop through all join buttons
                joinButtons.forEach(button => {
                    const date = button.getAttribute("data-date");
                    const timeSlotCell = button.closest("tr").querySelector("td:first-child");  // Get the time slot from the current row
                    const timeSlot = timeSlotCell ? timeSlotCell.textContent.trim() : null;

                    // Check if this button corresponds to a shift the user has already joined
                    const matchedShift = joinedShifts.find(shift =>
                        shift.date === date && shift.time_slot === timeSlot
                    );

                    if (matchedShift) {
                        // User has joined this shift: Create the "Join" button as if they pressed it already
                        button.textContent = `👤 ${loggedInUser} | Cancel`;
                        button.classList.remove("join-btn");
                        button.classList.add("joined-btn");
                    }
                });
            }
        });

    // Handle click events for Join / Cancel
    joinButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            const button = event.target;
            const date = button.getAttribute("data-date");
            const timeSlotCell = button.closest("tr").querySelector("td:first-child");  // Use the current row
            const timeSlot = timeSlotCell ? timeSlotCell.textContent.trim() : null;
            const role = "volunteer";

            // 👇 Cancel logic
            if (button.classList.contains("joined-btn")) {
                fetch("/api/cancel/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                    body: JSON.stringify({
                        username: loggedInUser,
                        date: date,
                        time_slot: timeSlot
                    })
                })
                .then(response => response.json())
                .then(data => {
                    console.log("Cancel response from backend:", data);
                    if (data.status === "deleted") {
                        // Change button back to "Join" after cancellation
                        button.textContent = "Bli med";
                        button.classList.remove("joined-btn");
                        button.classList.add("join-btn");
                    }
                });

                return; // 🛑 Stop here — don't run join logic
            }

            // 👉 Join logic
            fetch("/api/join/", {
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
                console.log("Join response from backend:", data);
                if (data.status === "success" && data.created) {
                    button.textContent = `👤 ${loggedInUser} | Cancel`;
                    button.classList.remove("join-btn");
                    button.classList.add("joined-btn");
                }
            });
        });
    });

    function getCSRFToken() {
        const token = document.querySelector("meta[name='csrf-token']");
        return token ? token.getAttribute("content") : "";
    }
});
