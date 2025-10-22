// === Global Variables ===
let draggedWorkerData = null;

// === Utility Functions ===
function allowDrop(event) {
  event.preventDefault();
}

// === Drag & Drop Handlers ===

// Start dragging from sidebar list
function handleDragStart(event) {
  const el = event.target;
  if (!el.classList.contains('worker')) return;

  draggedWorkerData = {
    workerId: el.dataset.userid,
    username: el.dataset.username,
  };

  event.dataTransfer.setData('text/plain', JSON.stringify(draggedWorkerData));
  el.classList.add('dragging');
}

// Start dragging an assigned name (from slot) to trash
function handleSlotToTrashDragStart(event) {
  const el = event.target;
  const data = {
    workerId: el.dataset.userid,
    date: el.dataset.date,
    timeSlot: el.dataset.timeslot,
    timeSlotId: el.dataset.timeslotid,
  };
  event.dataTransfer.setData('application/json', JSON.stringify(data));
}

// Handle dropping onto a slot
function handleDrop(event) {
  event.preventDefault();

  const slotEl = event.currentTarget; // always the td/slot
  slotEl.classList.remove('drag-over');

  const raw = event.dataTransfer.getData('text/plain');
  if (!raw) return;

  let workerData;
  try { workerData = JSON.parse(raw); } 
  catch { return; }

  const date = slotEl.dataset.date;
  const timeSlot = slotEl.dataset.timeSlot || slotEl.dataset.timeslot;
  const timeSlotId = slotEl.dataset.timeslotid;
  const role = slotEl.dataset.role === 'volunteer' || slotEl.classList.contains('volunteer-slot')
               ? 'volunteer' : 'worker';

  if (!workerData.workerId || !date || !timeSlot) return;

  assignWorkerToShift(workerData.workerId, date, timeSlot, role, timeSlotId);
}

// Handle dropping onto trash
function handleTrashDrop(event) {
  event.preventDefault();

  const json = event.dataTransfer.getData('application/json') || event.dataTransfer.getData('text/plain');
  if (!json) return;

  let data;
  try { data = JSON.parse(json); } catch { return; }

  const { workerId, date, timeSlotId } = data;
  if (!workerId || !date || !timeSlotId) return;

  removeWorkerFromShift(workerId, date, timeSlotId);
}

// === API Communication ===
function assignWorkerToShift(workerId, date, timeSlot, role='worker', timeSlotId=null) {
  const payload = { user_id: workerId, date, time_slot: timeSlot, role };
  if (timeSlotId) payload.time_slot_id = timeSlotId;

  fetch('/en/api/assign/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
    credentials: 'include',
    body: JSON.stringify(payload)
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success' || data.ok) location.reload();
    else console.warn('Assignment failed:', data);
  })
  .catch(err => console.error(err));
}

function removeWorkerFromShift(workerId, date, timeSlotId) {
  fetch('/en/api/remove/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
    body: JSON.stringify({ user_id: workerId, date, time_slot_id: timeSlotId })
  })
  .then(res => res.json())
  .then(() => location.reload())
  .catch(err => console.error(err));
}

// === Event Binding ===
document.addEventListener('DOMContentLoaded', () => {
  window.csrfToken = document.querySelector('[name=csrf-token]').content;

  // Sidebar draggable workers
  document.querySelectorAll('.worker').forEach(el => el.addEventListener('dragstart', handleDragStart));

  // Drop targets: slots (workers & volunteers)
  document.querySelectorAll('.worker-drop-target, .volunteer-slot, .worker-drop-zone, .worker-slot').forEach(slot => {
    slot.addEventListener('dragover', allowDrop);
    slot.addEventListener('drop', handleDrop);
  });

  // Assigned names draggable (to trash)
  document.querySelectorAll('.worker-name, .volunteer-name, .user-name').forEach(el => {
    el.addEventListener('dragstart', handleSlotToTrashDragStart);
  });

  // Trash bin(s)
  document.querySelectorAll('#trash-bin, .trash-bin').forEach(bin => {
    bin.addEventListener('dragover', allowDrop);
    bin.addEventListener('drop', handleTrashDrop);
  });
});
