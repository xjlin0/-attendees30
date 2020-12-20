Attendees.datagridUpdate = {
  init: () => {
    console.log("/static/js/persons/datagrid_attendee_update_view.js");
    Attendees.datagridUpdate.initForms();
  },

  formConfigs: {

    formData: null, // will be fetched
    items: [
      {
          dataField: "first_name",
          isRequired: true
      },
      {
          dataField: "full_name",
          disabled: true
      },
      {
          dataField: "photo",
          template: function (data, itemElement) {
            if (data.editorOptions && data.editorOptions.value){
              $("<img>").attr({src: data.editorOptions.value, class: "photo"}).appendTo(itemElement);
            }
          },
      },
      {
        dataField: "actual_birthday",
        editorType: "dxDateBox",
      },
      {
          dataField: "self_phone_numbers",
          helpText: "Example: +1(111)111-1111"
      },
      {
        dataField: "progressions",
        editorType: "dxTextArea",
        editorOptions: {
          placeholder: "Add notes...",
        }
      }
    ]

  },

  dxForm: null, // will be assigned later
  attendeeAttrs: null, // will be assigned later
  attendeeId: null, // will be assigned later

  initForms: () => {
    Attendees.datagridUpdate.attendeeAttrs = document.querySelector('div.datagrid-update');
    Attendees.datagridUpdate.attendeeId = Attendees.datagridUpdate.attendeeAttrs.id.replace("attendee_", "");

    $.ajax
      ({
        url      : Attendees.datagridUpdate.attendeeAttrs.dataset.attendeeEndpoint + Attendees.datagridUpdate.attendeeId + '/',
        success  : (response) => {
                      Attendees.datagridUpdate.formConfigs.formData = response.data[0];
                      Attendees.datagridUpdate.dxForm = $(".datagrid-update").dxForm(Attendees.datagridUpdate.formConfigs).dxForm("instance");
                   },
//        error    : (response) => {
//                   },
      });

  },
}

$(document).ready(() => {
  Attendees.datagridUpdate.init();
});
