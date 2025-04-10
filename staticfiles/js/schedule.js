document.addEventListener("DOMContentLoaded", function () {
    const buttons = document.querySelectorAll(".join-btn");

    buttons.forEach(button => {
        button.addEventListener("click", function () {
            this.textContent = "Cancel";
            this.style.backgroundColor = "#dc3545"; // Change to red
            this.removeEventListener("click", arguments.callee); // Remove the old event
            this.addEventListener("click", cancelShift);
        });
    });

    function cancelShift() {
        this.textContent = "Join";
        this.style.backgroundColor = "#28a745"; // Change to green
        this.removeEventListener("click", arguments.callee);
        this.addEventListener("click", function () {
            this.textContent = "Cancel";
            this.style.backgroundColor = "#dc3545";
            this.removeEventListener("click", arguments.callee);
            this.addEventListener("click", cancelShift);
        });
    }
});
