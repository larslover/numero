// === Global Variables ===
let draggedWorkerId = null;
let draggedWorkerName = null;

// === Utility Functions ===
function allowDrop(event) {
  event.preventDefault(); // Allows the drop
}

// === Drag & Drop Handlers ===

// From worker list to slot
function handleDragStart(event) {
  const workerElement = event.target;

  if (!workerElement.classList.contains('worker')) {
    console.warn("The target is not a worker element.");
    return;
  }

  const workerId = workerElement.getAttribute('data-userid');
  const workerUsername = workerElement.getAttribute('data-username');

  if (!workerId || !workerUsername) {
    console.error("Missing worker ID or Username");
    return;
  }

  draggedWorkerId = workerId;
  draggedWorkerName = workerUsername;

  event.dataTransfer.setData('text/plain', JSON.stringify({
    workerId: workerId,
    username: workerUsername
  }));

  workerElement.classList.add('dragging');
}

function handleDragOver(event) {
  event.preventDefault();
  event.target.classList.add('drag-over');
}

// From slot to trash
function handleSlotToTrashDragStart(event) {
  const el = event.target;
  const workerId = el.dataset.userid;
  const timeSlot = el.dataset.timeslot;
  const date = el.dataset.date;
  const timeSlotId = el.dataset.timeslotid;

  const data = JSON.stringify({ workerId, date, timeSlot, timeSlotId });
  event.dataTransfer.setData('application/json', data);
  event.dataTransfer.setData('text/plain', data);

  console.log("Dragging to trash:", { workerId, date, timeSlotId });
}

function handleDrop(event) {
  event.preventDefault();
  event.target.classList.remove('drag-over');

  const workerData = JSON.parse(event.dataTransfer.getData('text/plain'));
  const date = event.target.getAttribute('data-date');
  const timeSlot = event.target.getAttribute('data-time-slot');

  console.log("Dropped on:", { date, timeSlot });

  if (!workerData.workerId || !date || !timeSlot) {
    console.warn("Missing drop data");
    return;
  }

  assignWorkerToShift(workerData.workerId, date, timeSlot);
}

function handleTrashDrop(event) {
  event.preventDefault();

  const json = event.dataTransfer.getData('application/json') || event.dataTransfer.getData('text/plain');
  if (!json) {
    console.warn("❗ No transferable data found");
    return;
  }

  let transferData;
  try {
    transferData = JSON.parse(json);
  } catch (err) {
    console.error("❗ JSON parsing error:", err, json);
    return;
  }

  const { workerId, date, timeSlotId } = transferData;

  if (!workerId || !date || !timeSlotId) {
    console.warn("❗ Missing data for deletion");
    return;
  }

  removeWorkerFromShift(workerId, date, timeSlotId);
}

// === API Communication ===
function assignWorkerToShift(workerId, date, timeSlot) {
  console.log(`Assigning worker ${workerId} to ${date} / ${timeSlot}`);

  fetch('/en/api/assign/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    },
    credentials: 'include',
    body: JSON.stringify({ user_id: workerId, date, time_slot: timeSlot })
  })
    .then(response => {
      if (!response.ok) throw new Error('Network response was not ok');
      return response.json();
    })
    .then(data => {
      console.log('Assigned successfully:', data);
      if (data.status === 'success') location.reload();
    })
    .catch(error => console.error('Assignment failed:', error));
}

function removeWorkerFromShift(workerId, date, timeSlotId) {
  fetch('/en/api/remove/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({ user_id: workerId, date, time_slot_id: timeSlotId })
  })
    .then(response => response.json())
    .then(data => {
      console.log('✅ Removed successfully:', data);
      location.reload();
    })
    .catch(error => console.error('❌ Remove failed:', error));
}

// === DOM Ready / Event Binding ===
document.addEventListener('DOMContentLoaded', () => {
  window.csrfToken = document.querySelector('[name=csrf-token]').content;

  document.querySelectorAll('.worker').forEach(worker => {
    worker.addEventListener('dragstart', handleDragStart);
  });

  document.querySelectorAll('.time-slot, .worker-drop-target').forEach(slot => {
    slot.addEventListener('dragover', handleDragOver);
    slot.addEventListener('drop', handleDrop);
  });

  document.querySelectorAll('.worker-name').forEach(el => {
    el.addEventListener('drop', e => e.stopPropagation());
    el.addEventListener('dragover', e => e.preventDefault());
    el.addEventListener('dragstart', handleSlotToTrashDragStart);
  });

  document.querySelectorAll('.trash-bin').forEach(trashBin => {
    trashBin.addEventListener('dragover', allowDrop);
    trashBin.addEventListener('drop', handleTrashDrop);
  });
});
