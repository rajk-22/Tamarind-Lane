(function () {
  // Mobile navigation
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Booking form: load available times for the chosen date
  var form = document.getElementById('booking-form');
  if (!form) return;

  var dateInput = form.elements.date;
  var guestsInput = form.elements.guests;
  var box = document.getElementById('slots');
  var hint = document.getElementById('slot-hint');
  var selected = box.dataset.selected || '';
  var lastData = null;

  function render() {
    box.innerHTML = '';
    if (!lastData) return;
    if (lastData.closed) { hint.textContent = lastData.message; return; }

    var guests = parseInt(guestsInput.value || '1', 10);
    var anyFree = false;

    lastData.slots.forEach(function (slot) {
      var label = document.createElement('label');
      label.className = 'slot';
      var input = document.createElement('input');
      input.type = 'radio';
      input.name = 'time';
      input.value = slot.time;
      var text = document.createElement('span');
      text.textContent = slot.label;

      if (slot.left < guests) {
        input.disabled = true;
        label.classList.add('full');
        label.title = 'Not enough seats left at this time';
      } else {
        anyFree = true;
        if (slot.time === selected) input.checked = true;
      }
      label.appendChild(input);
      label.appendChild(text);
      box.appendChild(label);
    });

    hint.textContent = anyFree ? '' : 'No tables left for this party size. Try another date.';
  }

  function load() {
    lastData = null;
    box.innerHTML = '';
    if (!dateInput.value) { hint.textContent = 'Pick a date to see available times.'; return; }
    hint.textContent = 'Checking tables...';
    fetch('/api/availability?date=' + encodeURIComponent(dateInput.value))
      .then(function (r) { return r.json(); })
      .then(function (data) { lastData = data; render(); })
      .catch(function () { hint.textContent = 'Could not load times. Check your connection and try again.'; });
  }

  box.addEventListener('change', function (e) {
    if (e.target.name === 'time') selected = e.target.value;
  });
  dateInput.addEventListener('change', load);
  guestsInput.addEventListener('change', render);
  if (dateInput.value) load();
})();
