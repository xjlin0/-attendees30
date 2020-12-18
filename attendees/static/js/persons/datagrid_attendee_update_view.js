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
//          isRequired: true
      },
      {
          dataField: "picture",
          template: function (data, itemElement) {
              itemElement.append("<img src='" + data.editorOptions.value + "'>");
          }
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
        dataField: "notes",
        editorType: "dxTextArea",
        editorOptions: {
          placeholder: "Add notes...",
        }
      }
    ]

  },

  initForms: () => {
    const attendeeAttrs = document.querySelector('div.datagrid-update')
    const attendeeId = attendeeAttrs.id.replace("attendee_", "");
    const attendeeEndpoint = attendeeAttrs.dataset.attendeeEndpoint + attendeeId;
    const form = $(".datagrid-update").dxForm(Attendees.datagridUpdate.formConfigs).dxForm("instance");

    $.ajax
      ({
        url      : attendeeAttrs.dataset.attendeeEndpoint + attendeeId,
        success  : (response) => {
                      form.option("formData", response.data[0]);
                   },
//        error    : (response) => {
//                   },
      });

  },
}

$(document).ready(() => {
  Attendees.datagridUpdate.init();
});
