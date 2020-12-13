Attendees.formsetUpdate = {
  init: () => {
    console.log("/static/js/persons/attendees_update_view.js");
    document.querySelector('a[data-toggle="collapse"]').click(); // open the first Accordion.
    Attendees.formsetUpdate.enableEditButtonSwitching();
  },

  enableEditButtonSwitching: ()=>{
    const enableEditButton = document.querySelector('button.enable-edit');
    const editableFields = document.querySelectorAll('.changeable');
    const editButtons = document.querySelectorAll('input.cancel-edit-reset,input.submit-formset,input.reset-editing');
    enableEditButton.disabled = false;

    document.querySelector('form.attendees-formset').addEventListener('click', ()=>{
      switch(true) {
        case /enable-edit/.test(event.target.className):
          enableEditButton.classList.add('d-none');
          editButtons.forEach(ele => ele.classList.remove('d-none'));
          editableFields.forEach(ele => ele.disabled=false)
          break;

        case /cancel-edit-reset/.test(event.target.className):
          enableEditButton.classList.remove('d-none');
          editButtons.forEach(ele => ele.classList.add('d-none'));
          editableFields.forEach(ele => ele.disabled=true)
          break;

        default:
      }
    }, false);
  },
}

$(document).ready(() => {
  Attendees.formsetUpdate.init();
});
