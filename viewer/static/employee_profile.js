document.addEventListener('DOMContentLoaded', function() {
        var addButton = document.getElementById('add-contact-btn');
        var formContainer = document.getElementById('formset-container');
        var prefix = '{{ emergency_contact_formset.prefix }}';

        var totalForms = document.getElementById('id_' + prefix + '-TOTAL_FORMS');
        var maxForms = parseInt(document.getElementById('id_' + prefix + '-MAX_NUM_FORMS').value);
        var formNum = parseInt(totalForms.value);

        if (addButton) {
            addButton.addEventListener('click', function(e) {
                e.preventDefault();
                if (formNum < maxForms) {
                    // Clone the empty form template
                    var emptyFormDiv = document.getElementById('empty-form').firstElementChild.cloneNode(true);
                    var newForm = document.createElement('div');
                    newForm.innerHTML = emptyFormDiv.innerHTML;
                    newForm.classList.add('emergency-contact-form');

                    // Update form index
                    var formRegex = new RegExp('__prefix__', 'g');
                    newForm.innerHTML = newForm.innerHTML.replace(formRegex, formNum);

                    // Update labels
                    if (formNum == 1) {
                        newForm.querySelector('h4').innerText = 'Druhá osoba';
                    }

                    formContainer.appendChild(newForm);

                    formNum++;
                    totalForms.value = formNum;

                    // Hide the add button if we've reached max forms
                    if (formNum >= maxForms) {
                        addButton.style.display = 'none';
                    }
                }
            });
        }
    });