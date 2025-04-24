document.addEventListener("DOMContentLoaded", function () {
  const dateInput = document.querySelector("#id_date");
  const timeSlotSelect = document.querySelector("#id_time_slot");

  function updateTimeSlots() {
    const selectedDate = dateInput.value;
    console.log("Selected date:", selectedDate);  // DEBUG

    if (!selectedDate) return;

    fetch(`/get-time-slots/?date=${selectedDate}`)

      .then(response => response.json())
      .then(data => {
        // Clear existing options
        timeSlotSelect.innerHTML = "";

        // Add new options
        data.forEach(slot => {
          const option = document.createElement("option");
          option.value = slot.id;
          option.textContent = slot.label;
          timeSlotSelect.appendChild(option);
        });
      })
      .catch(error => {
        console.error("Error fetching time slots:", error);
      });
  }

  if (dateInput && timeSlotSelect) {
    dateInput.addEventListener("input", updateTimeSlots); // triggers when typing or using picker
    dateInput.addEventListener("blur", updateTimeSlots);  // triggers when focus leaves
    console.log("Event listeners attached to #id_date");
  }
});
