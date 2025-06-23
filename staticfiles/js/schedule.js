console.log("👋 Hello from inside schedule.js!");

// Event delegation for join/cancel buttons
document.addEventListener("click", function (event) {
    if (event.target.classList.contains("join-btn")) {
        joinShift(event.target);
    } else if (event.target.classList.contains("joined-btn")) {
        cancelShift(event.target);
    }
});

document.addEventListener("DOMContentLoaded", function () {
    console.log("Join script loaded!");
    console.log("Logged in user:", loggedInUser);  // Log the logged-in user for debugging
});

// Function to handle "Join" action
function joinShift(button) {
    console.log("Join button clicked!", button); 

    const date = button.dataset.date;
    const timeSlot = button.dataset.timeSlot;
    const role = button.dataset.role;

    console.log("Join button data:", { date, time_slot: timeSlot, role, action: "join" });

    fetch("/api/join/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content,
        },
        body: JSON.stringify({
            date: date,
            time_slot: timeSlot,
            role: role,
            action: "join",
        })
    })
    .then(response => {
        console.log("Response status:", response.status);
        return response.json();
    })
    .then(data => {
        console.log("Join success response:", data);
        if (data.status === "success") {
            button.textContent = `${data.username} | Avbryt`;
            button.classList.remove("join-btn");
            button.classList.add("joined-btn");
            button.style.backgroundColor = "#dc3545";
        } else {
            alert("Could not join shift. Please try again.");
        }
    })
    .catch(error => {
        console.error("Error during join request:", error);
        alert("There was an error while joining the shift.");
    });
}

// Function to handle "Cancel" action
function cancelShift(button) {
    console.log("Cancel button clicked!", button); 

    const date = button.dataset.date;
    const timeSlot = button.dataset.timeSlot;
    const role = button.dataset.role;

    console.log("Cancel button data:", { date, time_slot: timeSlot, role, action: "cancel" });

    fetch("/api/join/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content,
        },
        body: JSON.stringify({
            date: date,
            time_slot: timeSlot,
            role: role,
            action: "cancel",
        })
    })
    .then(response => {
        console.log("Response status:", response.status);
        return response.json();
    })
    .then(data => {
        console.log("Cancel success response:", data);
        if (data.status === "deleted" && data.count > 0) {
            button.textContent = "Bli med";
            button.classList.remove("joined-btn");
            button.classList.add("join-btn");
            button.style.backgroundColor = "#28a745";
        } else {
            alert("Could not cancel shift. Please try again.");
        }
    })
    .catch(error => {
        console.error("Error during cancel request:", error);
        alert("There was an error while canceling the shift.");
    });
}
