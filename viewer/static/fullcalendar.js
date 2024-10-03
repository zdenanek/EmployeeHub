document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: '/your-events-endpoint/', // Změň na URL endpoint pro události
        selectable: true,
        select: function(info) {
            // Zpracování výběru data
            var title = prompt('Název události:');
            var start = info.startStr;
            var end = info.endStr;

            // AJAX požadavek na vytvoření události
            fetch('/create-event/', { // Změň na URL pro vytvoření události
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') // Zde získáš CSRF token
                },
                body: JSON.stringify({ title: title, start: start, end: end })
            }).then(response => {
                if (response.ok) {
                    // Úspěšně vytvořeno
                    calendar.refetchEvents();
                } else {
                    // Chybová hlášení
                }
            });
        }
    });
    calendar.render();
});

// Funkce pro získání CSRF tokenu
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Zkontroluj, zda se cookie shoduje s požadovaným jménem
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
