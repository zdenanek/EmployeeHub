document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: '/events-feed/', // URL endpoint pro načítání událostí
        selectable: true,
        select: function(info) {
            $('#createEventButton').click(); // Automatické vyvolání formuláře
        },
        slotLabelFormat: {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        },
        eventTimeFormat: {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        }
    });

    calendar.render();

    $('#createEventButton').on('click', function() {
        // AJAX požadavek pro načtení dostupných skupin
        $.getJSON('/get-groups/', function(groups) {
            var optionsHtml = '';
            groups.forEach(function(group) {
                optionsHtml += `<option value="${group.name}">${group.name}</option>`;
            });

            // Vytvoření HTML formuláře pro vytvoření události
            var formHtml = `
                <div id="eventForm" style="position: fixed; z-index: 1000; background: white; border: 1px solid #ccc; padding: 10px; top: 100px; left: 100px;">
                    <label>Název události:</label>
                    <input type="text" id="eventTitle" required>
                    <br>
                    <label>Datum a čas začátku:</label>
                    <input type="text" id="startDate" class="datepicker" required>
                    <select id="startHour">
                        ${generateHourOptions()}
                    </select> :
                    <select id="startMinute">
                        ${generateMinuteOptions()}
                    </select>
                    <br>
                    <label>Datum a čas konce:</label>
                    <input type="text" id="endDate" class="datepicker" required>
                    <select id="endHour">
                        ${generateHourOptions()}
                    </select> :
                    <select id="endMinute">
                        ${generateMinuteOptions()}
                    </select>
                    <br>
                    <label>Skupiny:</label>
                    <select id="eventGroup">
                        ${optionsHtml}
                    </select>
                    <br>
                    <button id="saveEvent">Uložit událost</button>
                    <button id="cancelEvent">Zrušit</button>
                </div>
            `;
            $('body').append(formHtml);
            $('.datepicker').datepicker({ dateFormat: 'yy-mm-dd' });

            $('#saveEvent').on('click', function() {
                var title = $('#eventTitle').val();
                var startDate = moment($('#startDate').val() + ' ' + $('#startHour').val() + ':' + $('#startMinute').val(), 'YYYY-MM-DD HH:mm').format('YYYY-MM-DDTHH:mm');
                var endDate = moment($('#endDate').val() + ' ' + $('#endHour').val() + ':' + $('#endMinute').val(), 'YYYY-MM-DD HH:mm').format('YYYY-MM-DDTHH:mm');
                var group = $('#eventGroup').val();

                if (title) {
                    fetch('/create-event/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({
                            title: title,
                            start_time: startDate,
                            end_time: endDate,
                            group: group
                        })
                    }).then(response => {
                        if (response.ok) {
                            calendar.refetchEvents();
                            $('#eventForm').remove();
                        } else {
                            alert('Chyba při vytváření události');
                        }
                    });
                } else {
                    alert('Musíte zadat název události.');
                }
            });

            $('#cancelEvent').on('click', function() {
                $('#eventForm').remove();
            });
        }).fail(function() {
            alert('Chyba při načítání skupin. Ujistěte se, že je dostupný endpoint /get-groups/.');
        });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function generateHourOptions() {
    let options = '';
    for (let i = 0; i < 24; i++) {
        options += `<option value="${i.toString().padStart(2, '0')}">${i.toString().padStart(2, '0')} hod.</option>`;
    }
    return options;
}

function generateMinuteOptions() {
    let options = '';
    for (let i = 0; i < 60; i += 5) {
        options += `<option value="${i.toString().padStart(2, '0')}">${i.toString().padStart(2, '0')}</option>`;
    }
    return options;
}