document.addEventListener('DOMContentLoaded', function () {
    var applicantSelect = document.querySelector('select[name="applicant_id"]');
    var resumeSelect = document.querySelector('select[name="resume_id"]');

    if (!applicantSelect || !resumeSelect) {
        return;
    }

    function renderResumeOptions(items, selectedValue) {
        resumeSelect.innerHTML = '';

        if (!items.length) {
            var emptyOption = document.createElement('option');
            emptyOption.value = '';
            emptyOption.textContent = 'Нет доступных резюме';
            resumeSelect.appendChild(emptyOption);
            return;
        }

        items.forEach(function (item, index) {
            var option = document.createElement('option');
            option.value = String(item.id);
            option.textContent = item.label;

            if (String(item.id) === String(selectedValue) || (!selectedValue && index === 0)) {
                option.selected = true;
            }

            resumeSelect.appendChild(option);
        });
    }

    function updateResumes(selectedValue) {
        if (!applicantSelect.value) {
            renderResumeOptions([], '');
            return;
        }

        fetch('/admin/panel/api/applicants/' + applicantSelect.value + '/resumes', {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error('Failed to load resumes');
                }
                return response.json();
            })
            .then(function (items) {
                renderResumeOptions(items, selectedValue || resumeSelect.value);
            })
            .catch(function () {
                renderResumeOptions([], '');
            });
    }

    applicantSelect.addEventListener('change', function () {
        updateResumes('');
    });

    updateResumes(resumeSelect.value);
});