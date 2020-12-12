Attendees.formsetUpdate = {
  init: () => {
    console.log("/static/js/persons/attendees_update_view.js");

    Attendees.formsetUpdate.expandAccordionAndEnableEditButton();
  },

  expandAccordionAndEnableEditButton: ()=>{
    document.querySelector('a[data-toggle="collapse"]').click(); // open the first
    document.querySelector('button.enable-edit').disabled = false;
  },
}

$(document).ready(() => {
  Attendees.formsetUpdate.init();
});
