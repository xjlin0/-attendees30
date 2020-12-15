Attendees.datagridUpdate = {
  init: () => {
    console.log("/static/js/persons/datagrid_attendee_update_view.js");
    Attendees.datagridUpdate.initForms();
  },

  formConfigs: {

    formData: {
      id: "a123",
      name: "John Heart",
      hireDate: new Date(2012, 4, 13),
      picture: "https://js.devexpress.com/Content/images/doc/20_2/PhoneJS/person2.png",
      phone: "+1(360)684-1334",
      notes: "John is ......",
    },
    items: [
      {
          dataField: "name",
          isRequired: true
      },
      {
          dataField: "picture",
          template: function (data, itemElement) {
              itemElement.append("<img src='" + data.editorOptions.value + "'>");
          }
      },
      {
        dataField: "hireDate",
        editorType: "dxDateBox",
      },
      {
          dataField: "phone",
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
    $(".datagrid-update").dxForm(Attendees.datagridUpdate.formConfigs);
    console.log("initForms called");
  },
}

$(document).ready(() => {
  Attendees.datagridUpdate.init();
});
