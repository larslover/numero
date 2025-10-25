console.log("✅ admin_schedule.js loaded!");

// === Global Variables ===
let draggedWorkerData = null;

// === Utility Functions ===
function allowDrop(event) {
  event.preventDefault();
}

// === Drag & Drop Handlers ===
function handleDragStart(event) {
  const el = event.target;
  if (!el.classList.contains('worker')) return;

  draggedWorkerData = {
    workerId: el.dataset.userid,
    username: el.dataset.username,
  };

  event.dataTransfer.setData('text/plain', JSON.stringify(draggedWorkerData));
  el.classList.add('dragging');
  console.debug('DragStart:', draggedWorkerData);
}

function handleSlotToTrashDragStart(event) {
  const el = event.target;
  const data = {
    workerId: el.dataset.userid,
    date: el.dataset.date,
    timeSlot: el.dataset.timeslot,
    timeSlotId: el.dataset.timeslotid,
  };
  event.dataTransfer.setData('application/json', JSON.stringify(data));
  console.debug('Trash dragStart:', data);
}

function handleDrop(event) {
  event.preventDefault();
  const slotEl = event.currentTarget;
  slotEl.classList.remove('drag-over');

  const raw = event.dataTransfer.getData('text/plain');
  if (!raw) return;

  let workerData;
  try { workerData = JSON.parse(raw); } catch { return; }

  const date = slotEl.dataset.date;
  const timeSlot = slotEl.dataset.timeSlot || slotEl.dataset.timeslot;
  const timeSlotId = slotEl.dataset.timeslotid;
  const role = slotEl.dataset.role === 'volunteer' || slotEl.classList.contains('volunteer-slot')
               ? 'volunteer' : 'worker';

  if (!workerData.workerId || !date || !timeSlot) return;

  assignWorkerToShift(workerData.workerId, date, timeSlot, role, timeSlotId);
  console.debug('Dropped worker:', workerData, 'into slot:', { date, timeSlot, role });
}

function handleTrashDrop(event) {
  event.preventDefault();
  const json = event.dataTransfer.getData('application/json') || event.dataTransfer.getData('text/plain');
  if (!json) return;

  let data;
  try { data = JSON.parse(json); } catch { return; }

  const { workerId, date, timeSlotId } = data;
  if (!workerId || !date || !timeSlotId) return;

  removeWorkerFromShift(workerId, date, timeSlotId);
  console.debug('Removed worker:', data);
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
    console.debug('Assign response:', data);
    if (data.status === 'success' || data.ok) location.reload();
  })
  .catch(err => console.error('Assign fetch failed:', err));
}

function removeWorkerFromShift(workerId, date, timeSlotId) {
  fetch('/en/api/remove/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
    body: JSON.stringify({ user_id: workerId, date, time_slot_id: timeSlotId })
  })
  .then(res => res.json())
  .then(() => location.reload())
  .catch(err => console.error('Remove fetch failed:', err));
}

// === Event Binding ===
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM fully loaded, binding events...');

  window.csrfToken = document.querySelector('[name=csrf-token]').content;

  // Sidebar draggable workers
  document.querySelectorAll('.worker').forEach(el => el.addEventListener('dragstart', handleDragStart));

  // Drop targets: slots (workers & volunteers)
  document.querySelectorAll('.worker-drop-target, .volunteer-slot, .worker-drop-zone, .worker-slot').forEach(slot => {
    slot.addEventListener('dragover', allowDrop);
    slot.addEventListener('drop', handleDrop);
    slot.addEventListener('dragenter', () => slot.classList.add('drag-over'));
    slot.addEventListener('dragleave', () => slot.classList.remove('drag-over'));
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

  // Save Daily Comment Button
  document.body.addEventListener('click', async (e) => {
    const btn = e.target.closest('.save-comment-btn');
    if (!btn) return;

    console.log('💾 Save button clicked!', btn);

    const container = btn.closest('.daily-comment-container');
    const textarea = container?.querySelector('.daily-comment');
    if (!textarea) {
      console.warn('Textarea not found for Save button!', btn);
      return;
    }

    const date = textarea.dataset.date;
    const comment = textarea.value.trim();

    console.log('Saving comment payload:', { date, comment });

    btn.disabled = true;
    const originalText = btn.textContent;
    btn.textContent = 'Saving…';

    try {
      const res = await fetch(window.scheduleConfig.saveDailyCommentUrl, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-CSRFToken': window.scheduleConfig.csrfToken
        },
        credentials: 'include',
        body: JSON.stringify({ date, comment })
      });

      const data = await res.json();
      console.log('Server response:', data);

      textarea.style.border = data.success ? '2px solid #28a745' : '2px solid red';
      setTimeout(() => textarea.style.border = '', 1200);

    } catch (err) {
      console.error('Save request failed', err);
      textarea.style.border = '2px solid red';
      setTimeout(() => textarea.style.border = '', 1200);
    } finally {
      btn.disabled = false;
      btn.textContent = originalText;
    }
  });

});
