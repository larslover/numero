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

  // keep your existing check (sidebar items have class 'worker' in your reverted version)
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

  // store a JSON payload so removal also works (slot items use same JSON)
  event.dataTransfer.setData('text/plain', JSON.stringify({
    workerId: workerId,
    username: workerUsername
  }));

  workerElement.classList.add('dragging');
}

function handleDragOver(event) {
  event.preventDefault();
  // Use currentTarget if present to avoid styling inner elements
  const el = event.currentTarget || event.target;
  el.classList.add('drag-over');
}

// From slot to trash (dragging an assigned name)
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

// DROP handler — updated to detect role
function handleDrop(event) {
  event.preventDefault();

  // remove drag-over class from the element that has the handler
  const slotEl = event.currentTarget || event.target;
  slotEl.classList.remove('drag-over');

  // The sidebar and slot drags set 'text/plain' JSON; slot-to-trash sets 'application/json' too
  const raw = event.dataTransfer.getData('text/plain') || event.dataTransfer.getData('application/json');
  if (!raw) {
    console.warn("No transferable data found");
    return;
  }

  let workerData;
  try {
    workerData = JSON.parse(raw);
  } catch (err) {
    console.error("Failed parsing drop data:", err, raw);
    return;
  }

  // get attributes from the element that has the event listener (the slot)
  const date = slotEl.getAttribute('data-date');
  const timeSlot = slotEl.getAttribute('data-time-slot') || slotEl.getAttribute('data-timeslot'); // accept both names
  const timeSlotId = slotEl.getAttribute('data-timeslotid');
  // detect role based on slot class or data-role attribute
  const role = slotEl.classList.contains('volunteer-slot') || slotEl.getAttribute('data-role') === 'volunteer'
    ? 'volunteer'
    : 'worker';

  console.log("Dropped on:", { date, timeSlot, role, workerData });

  if (!workerData.workerId || !date || !timeSlot) {
    console.warn("Missing drop data");
    return;
  }

  // call assign and include role & timeslotId where available
  assignWorkerToShift(workerData.workerId, date, timeSlot, role, timeSlotId);
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
// note: now accepts `role` and optional timeSlotId
function assignWorkerToShift(workerId, date, timeSlot, role = 'worker', timeSlotId = null) {
  console.log(`Assigning ${role} ${workerId} to ${date} / ${timeSlot} (timeslotId=${timeSlotId})`);

  const payload = { user_id: workerId, date, time_slot: timeSlot, role };
  if (timeSlotId) payload.time_slot_id = timeSlotId;

  fetch('/en/api/assign/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    },
    credentials: 'include',
    body: JSON.stringify(payload)
  })
    .then(response => {
      if (!response.ok) throw new Error('Network response was not ok: ' + response.status);
      return response.json();
    })
    .then(data => {
      console.log('Assigned successfully:', data);
      // backend returns {"ok": True, "status":"success", ...} — your previous code checked data.status === 'success'
      // here we check both common variants
      if (data.status === 'success' || data.ok === true) {
        location.reload();
      } else {
        console.warn('Assignment did not return success:', data);
        // optionally show an error to user here
      }
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
  // ensure csrfToken is available globally (your template defines csrftoken earlier)
  window.csrfToken = document.querySelector('[name=csrf-token]').content;

  // sidebar worker items (draggable user list)
  document.querySelectorAll('.worker').forEach(worker => {
    worker.addEventListener('dragstart', handleDragStart);
  });

  // Add drop listeners to all slot types, including volunteer slots
  document.querySelectorAll('.time-slot, .worker-drop-target, .worker-drop-zone, .worker-drop-target, .volunteer-slot, .worker-slot').forEach(slot => {
    slot.addEventListener('dragover', handleDragOver);
    slot.addEventListener('drop', handleDrop);
  });

  // assigned names inside slots (so admin can drag them to trash)
  document.querySelectorAll('.worker-name, .volunteer-name, .user-name').forEach(el => {
    el.addEventListener('drop', e => e.stopPropagation());
    el.addEventListener('dragover', e => e.preventDefault());
    el.addEventListener('dragstart', handleSlotToTrashDragStart);
  });

  // trash bin(s)
  document.querySelectorAll('.trash-bin, #trash-bin').forEach(trashBin => {
    trashBin.addEventListener('dragover', allowDrop);
    trashBin.addEventListener('drop', handleTrashDrop);
  });
});
