"""
function allowDrop(event) {
  event.preventDefault(); // Allows the drop
}

document.addEventListener('DOMContentLoaded', () => {
  const csrfToken = document.querySelector('[name=csrf-token]').content;

  // Set up weekday time slots
  document.querySelectorAll('.time-slot').forEach(slot => {
    slot.addEventListener('dragover', handleDragOver);
    slot.addEventListener('drop', handleDrop);
  });

  // Set up weekend time slots
  document.querySelectorAll('.worker-drop-target').forEach(slot => {
    slot.addEventListener('dragover', handleDragOver);
    slot.addEventListener('drop', handleDrop);
  });

  // Prevent nested dragging issues
  document.querySelectorAll('.worker-name').forEach(el => {
    el.addEventListener('drop', e => e.stopPropagation());
    el.addEventListener('dragover', e => e.preventDefault());
  });
  
  // Handle drag start
  window.handleDragStart = function(event) {
    const el = event.target;
    const workerId = el.dataset.userid;
    const username = el.dataset.username;
    const date = el.dataset.date;
    const timeSlot = el.dataset.timeslot;
    const timeSlotId = el.dataset.timeslotid; // Use this for storing timeSlotId
    
    // Set the transfer data, including timeSlotId
    event.dataTransfer.setData('text/plain', JSON.stringify({ workerId, date, timeSlot, timeSlotId }));
    
    console.log(`Dragging: ${username} (ID: ${workerId})`);
  };
  

  // Drop onto a shift slot
  window.drop = function(event, date, timeSlot) {
    event.preventDefault();
    event.target.classList.remove('drag-over');
    const workerData = JSON.parse(event.dataTransfer.getData('text/plain'));

    if (!workerData.workerId || !date || !timeSlot) {
      console.warn("Missing drop data");
      return;
    }

    assignWorkerToShift(workerData.workerId, date, timeSlot);
    location.reload();
  };

  function handleDragOver(event) {
    event.preventDefault(); // Necessary to allow drop
    event.target.classList.add('drag-over');
  }

  function handleDrop(event) {
    event.preventDefault();
    event.target.classList.remove('drag-over');

    const workerData = JSON.parse(event.dataTransfer.getData('text/plain'));
    const date = event.target.getAttribute('data-date');
    const timeSlot = event.target.getAttribute('data-time-slot');

    if (!workerData.workerId || !date || !timeSlot) {
      console.warn("Missing drop data");
      return;
    }

    assignWorkerToShift(workerData.workerId, date, timeSlot);
  }

  // 🗑️ Handle drop on trash bin
  window.handleTrashDrop = function(event) {
    event.preventDefault();
    console.log(event.dataTransfer.getData('application/json'));
    console.log("initiated handletrasdrop")

    // Change 'text/plain' to 'application/json' to match the drag data format
    const workerData = JSON.parse(event.dataTransfer.getData('application/json'));
    const { workerId, date, timeSlot } = workerData;
  
    if (!workerId || !date || !timeSlot) {
      console.warn("Missing data for deletion");
      return;
    }
  
    if (!confirm("Fjern denne personen fra skiftet?")) return;
  
    console.log(`Removing worker ${workerId} from ${date} / ${timeSlot}`);
  
    fetch('/en/api/remove/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({
        user_id: workerId,
        date: date,
        time_slot: timeSlot
      })
    })
    .then(response => response.json())
    .then(data => {
      console.log('Removed successfully:', data);
      location.reload();
    })
    .catch(error => {
      console.error('Remove failed:', error);
    });
  };
  
  function assignWorkerToShift(workerId, date, timeSlot) {
    console.log(`Assigning worker ${workerId} to ${date} / ${timeSlot}`);
  
    fetch('/en/api/assign/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      credentials: 'include',
      body: JSON.stringify({
        user_id: workerId,
        date: date,
        time_slot: timeSlot
      })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      console.log('Assigned successfully:', data);
      
      // Ensure that the API response contains the worker's name
      if (data && data.worker_name) {
        updateShiftSlot(date, timeSlot, data.worker_name);
      } else {
        console.warn('Worker name not found in API response');
      }
    })
    .catch(error => {
      console.error('Assignment failed:', error);
    });
  }
  
  function updateShiftSlot(date, timeSlot, workerName) {
    const targetSlot = document.querySelector(`#slot-${date}-${timeSlot}-worker`);
    
    // Check if the target slot exists
    if (targetSlot) {
      console.log(`Updating shift slot: ${date} / ${timeSlot}`);
  
      // Create a new div for the worker's name
      const workerDiv = document.createElement('div');
      workerDiv.classList.add('worker-name');
      workerDiv.textContent = workerName;  // Assuming workerName is returned
  
      // Clear existing workers and append the new worker
      targetSlot.innerHTML = '';  // Clear the current content
      targetSlot.appendChild(workerDiv);
  
      console.log(`Worker ${workerName} assigned to ${date} / ${timeSlot}`);
    } else {
      console.warn(`Slot for ${date} / ${timeSlot} not found in the DOM.`);
    }
  }
  
  
});
// Fallback for any elements using ondragstart="drag(event)"
function drag(event) {
  const target = event.target;

  // From worker list (e.g. assigning someone to a shift)
  if (target.classList.contains('worker-name')) {
      const workerId = target.id.replace('worker-', '');
      const payload = JSON.stringify({
          type: 'worker',
          worker_id: workerId
      });
      event.dataTransfer.setData('application/json', payload);
  }

  // From slot (e.g. removing someone via trash)
  else if (target.classList.contains('joined-btn') || target.classList.contains('assigned-worker')) {
      const dataId = target.getAttribute('data-id');
      const payload = JSON.stringify({
          type: 'assignment',
          data_id: dataId
      });
      event.dataTransfer.setData('application/json', payload);
  }

  event.target.classList.add('dragging');
}



"""