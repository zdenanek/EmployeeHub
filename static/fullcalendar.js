document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');

    function openCreateEventForm() {
        // AJAX request to load available groups
        $.getJSON('/get-groups/', function(groups) {
            var optionsHtml = '';
            groups.forEach(function(group) {
                optionsHtml += `<option value="${group.name}">${group.name}</option>`;
            });

            // Create the HTML form for event creation
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
    }

    // *** Start of new function openUpdateEventForm ***
    function openUpdateEventForm(event) {
        // AJAX request to load available groups
        $.getJSON('/get-groups/', function(groups) {
            var optionsHtml = '';
            groups.forEach(function(group) {
                optionsHtml += `<option value="${group.name}">${group.name}</option>`;
            });

            // Create the HTML form for event update
            var formHtml = `
                <div id="eventForm" style="position: fixed; z-index: 1000; background: white; border: 1px solid #ccc; padding: 10px; top: 100px; left: 100px;">
                    <label>Název události:</label>
                    <input type="text" id="eventTitle" value="${event.title}" required>
                    <br>
                    <label>Datum a čas začátku:</label>
                    <input type="text" id="startDate" class="datepicker" value="${moment(event.start).format('YYYY-MM-DD')}" required>
                    <select id="startHour">
                        ${generateHourOptions(moment(event.start).format('HH'))}
                    </select> :
                    <select id="startMinute">
                        ${generateMinuteOptions(moment(event.start).format('mm'))}
                    </select>
                    <br>
                    <label>Datum a čas konce:</label>
                    <input type="text" id="endDate" class="datepicker" value="${moment(event.end).format('YYYY-MM-DD')}" required>
                    <select id="endHour">
                        ${generateHourOptions(moment(event.end).format('HH'))}
                    </select> :
                    <select id="endMinute">
                        ${generateMinuteOptions(moment(event.end).format('mm'))}
                    </select>
                    <br>
                    <label>Skupiny:</label>
                    <select id="eventGroup">
                        ${optionsHtml}
                    </select>
                    <br>
                    <button id="updateEvent">Aktualizovat událost</button>
                    <button id="deleteEvent">Smazat událost</button>
                    <button id="cancelEvent">Zrušit</button>
                </div>
            `;
            $('body').append(formHtml);
            $('.datepicker').datepicker({ dateFormat: 'yy-mm-dd' });

            // Set selected group
            $('#eventGroup').val(event.extendedProps.group);

            $('#updateEvent').on('click', function() {
                var title = $('#eventTitle').val();
                var startDate = moment($('#startDate').val() + ' ' + $('#startHour').val() + ':' + $('#startMinute').val(), 'YYYY-MM-DD HH:mm').format('YYYY-MM-DDTHH:mm');
                var endDate = moment($('#endDate').val() + ' ' + $('#endHour').val() + ':' + $('#endMinute').val(), 'YYYY-MM-DD HH:mm').format('YYYY-MM-DDTHH:mm');
                var group = $('#eventGroup').val();

                if (title) {
                    fetch('/update-event/' + event.id + '/', {
                        method: 'PUT',
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
                            alert('Chyba při aktualizaci události');
                        }
                    });
                } else {
                    alert('Musíte zadat název události.');
                }
            });

            $('#deleteEvent').on('click', function() {
                if (confirm('Opravdu chcete smazat tuto událost?')) {
                    fetch('/delete-event/' + event.id + '/', {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    }).then(response => {
                        if (response.ok) {
                            calendar.refetchEvents();
                            $('#eventForm').remove();
                        } else {
                            alert('Chyba při mazání události');
                        }
                    });
                }
            });

            $('#cancelEvent').on('click', function() {
                $('#eventForm').remove();
            });
        }).fail(function() {
            alert('Chyba při načítání skupin. Ujistěte se, že je dostupný endpoint /get-groups/.');
        });
    }



    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today createEventButton',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        customButtons: {
            createEventButton: {
                text: 'Vytvořit událost',
                click: function() {
                    openCreateEventForm();
                }
            }
        },
        events: '/events-feed/',
        displayEventEnd: true,
        eventTimeFormat: {
            hour: '2-digit',
            minute: '2-digit',
            meridiem: false,
            hour12: false
        },
        eventContent: function(arg) {
            let timeText = arg.timeText;
            let title = arg.event.title;
            let groupName = arg.event.extendedProps.group;
            let html = `
                <div class="fc-event-time">${timeText}</div>
                <div class="fc-event-title">${title} (${groupName})</div>
            `;
            return { html: html };
        },
        eventClick: function(info) {
        openUpdateEventForm(info.event);
        }
    });

    calendar.render();
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

function generateHourOptions(selectedHour = null) {
    let options = '';
    for (let i = 0; i < 24; i++) {
        let hour = i.toString().padStart(2, '0');
        let selected = (hour === selectedHour) ? ' selected' : '';
        options += `<option value="${hour}"${selected}>${hour} hod.</option>`;
    }
    return options;
}

function generateMinuteOptions(selectedMinute = null) {
    let options = '';
    for (let i = 0; i < 60; i += 5) {
        let minute = i.toString().padStart(2, '0');
        let selected = (minute === selectedMinute) ? ' selected' : '';
        options += `<option value="${minute}"${selected}>${minute}</option>`;
    }
    return options;
}
