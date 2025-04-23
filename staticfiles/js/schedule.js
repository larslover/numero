console.log("👋 Hello from inside schedule.js!");


document.addEventListener("DOMContentLoaded", function () {
    console.log("Join script loaded!");
    console.log("Logged in user:", loggedInUser);  // Log the logged-in user for debugging

    const buttons = document.querySelectorAll(".join-btn, .joined-btn");

    // Loop through all buttons and attach appropriate listeners
    buttons.forEach(button => {
        console.log("Found button:", button); // Debugging each button

        if (button.classList.contains("join-btn")) {
            console.log("Attaching joinShift listener for button:", button); // Debugging
            button.addEventListener("click", joinShift);
        } else if (button.classList.contains("joined-btn")) {
            console.log("Attaching cancelShift listener for button:", button); // Debugging
            button.addEventListener("click", cancelShift);
        }
    });

    // Function to handle "Join" action
    function joinShift(event) {
        event.preventDefault();  // Stop default behavior (if any)
        console.log("Join button clicked!"); // Debugging
        const button = event.currentTarget;
        console.log("Button clicked:", button); // Debugging

        const date = button.dataset.date;
        const timeSlot = button.dataset.timeSlot;
        const role = button.dataset.role; // Added role from the data attribute
        console.log("Join button data:", { date, time_slot: timeSlot, role, action: "join" });

        // Log the fetch request details
        console.log("Sending POST request to /api/join/ with data:", {
            date: date,
            time_slot: timeSlot,
            role: role,
            action: "join",  // Specify action as "join"
        });

        // Send a POST request to the server to join the shift
        fetch("/api/join/", {
            method: "POST",  // Ensure POST method is used
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content,
            },
            body: JSON.stringify({
                date: date,
                time_slot: timeSlot,
                role: role,
                action: "join",  // Specify action as "join"
            })
        })
        .then(response => {
            console.log("Response status:", response.status); // Log the response status
            if (response.status !== 200) {
                console.error("Unexpected response status:", response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log("Join success response:", data); // Debugging
            if (data.status === "success") {
                console.log("Join success:", data); // Debugging
                // Update the button state after joining
                button.textContent = `${data.username} | Avbryt`;  // Assuming response returns username
                button.classList.remove("join-btn");
                button.classList.add("joined-btn");
                button.style.backgroundColor = "#dc3545"; // Red color for "Cancel"
                button.removeEventListener("click", joinShift);
                button.addEventListener("click", cancelShift);
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
    function cancelShift(event) {
        event.preventDefault();  // Stop default behavior
        console.log("Cancel button clicked!"); // Debugging
        const button = event.currentTarget;
        console.log("Button clicked:", button); // Debugging

        const date = button.dataset.date;
        const timeSlot = button.dataset.timeSlot;
        const role = button.dataset.role; // Added role from the data attribute
        console.log("Cancel button data:", { date, time_slot: timeSlot, role, action: "cancel" });

        // Log the fetch request details
        console.log("Sending POST request to /api/join/ with data:", {
            date: date,
            time_slot: timeSlot,
            role: role,
            action: "cancel",  // Specify action as "cancel"
        });

        // Send a POST request to the server to cancel the shift
        fetch("/api/join/", {
            method: "POST",  // Ensure POST method is used
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content,
            },
            body: JSON.stringify({
                date: date,
                time_slot: timeSlot,
                role: role,
                action: "cancel",  // Specify action as "cancel"
            })
        })
        .then(response => {
            console.log("Response status:", response.status); // Log the response status
            return response.json();
        })
        .then(data => {
            console.log("Cancel success response:", data); // Debugging
            if (data.status === "deleted" && data.count > 0) {
                console.log("Cancel success:", data); // Debugging
                // Update the button state after canceling
                button.textContent = "Bli med";
                button.classList.remove("joined-btn");
                button.classList.add("join-btn");
                button.style.backgroundColor = "#28a745"; // Green color for "Join"
                button.removeEventListener("click", cancelShift);
                button.addEventListener("click", joinShift);
            } else {
                alert("Could not cancel shift. Please try again.");
            }
        })
        .catch(error => {
            console.error("Error during cancel request:", error);
            alert("There was an error while canceling the shift.");
        });
    }
});
