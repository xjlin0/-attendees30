Attendees.formsetUpdate = {
  init: () => {
    console.log("/static/js/persons/attendees_update_view.js");

    Attendees.formsetUpdate.expandAccordionAndEnableEditButton();
    Attendees.formsetUpdate.switchEditModeUponButtons();
  },

  editButtonSelectors: 'input.cancel-edit-reset,input.submit-formset,input.reset-editing',

  expandAccordionAndEnableEditButton: ()=>{
    const editButton = document.querySelector('button.enable-edit');

    document.querySelector('a[data-toggle="collapse"]').click(); // open the first Accordion.

    editButton.disabled = false;
    editButton.addEventListener('click', ()=>{
      editButton.classList.add('d-none');
      document.querySelectorAll(Attendees.formsetUpdate.editButtonSelectors).forEach(ele => ele.classList.remove('d-none'));
    }, false);
  },

  switchEditModeUponButtons: () => {
    const editButton = document.querySelector('button.enable-edit');
  },
}

$(document).ready(() => {
  Attendees.formsetUpdate.init();
});
