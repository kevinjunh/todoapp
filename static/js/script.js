document.getElementById('project').addEventListener('change', function() {
    var newprojectInput = document.getElementById('new_project');
    newprojectInput.disabled = this.value !== 'new';

    if (this.value === 'new') {
        newprojectInput.removeAttribute('disabled');
        projectForm.classList.remove('hidden');
    }
});
