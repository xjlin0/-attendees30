Attendees.datagridUpdate = {
  init: () => {
    console.log("/static/js/persons/datagrid_attendee_update_view.js");
    Attendees.datagridUpdate.initAttendeeForm();
  },

  attendeeFormConfigs: {

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
              $("<img>").attr({src: data.editorOptions.value, class: "photo " + Attendees.datagridUpdate.attendeeAttrs.id}).appendTo(itemElement);
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
        dataField: "progressions.belief",
        editorType: "dxTextArea",
        editorOptions: {
          placeholder: "Add notes...",
        }
      },
      {
        dataField: "joined_meets",
        template: (data, itemElement) => {
          $("<button>").attr({title: "+ Add a new meet", type: 'button', class: "attendingmeet btn-outline-primary btn button btn-sm "}).text("Attend new meet").appendTo(itemElement);
          if (data.editorOptions && data.editorOptions.value){
            data.editorOptions.value.forEach(attending => {
              const buttonClass = Date.now() < Date.parse(attending.attending_finish) ? 'btn-outline-success' : 'btn-outline-secondary';
              const buttonAttrs = {
                title: "since " + attending.attending_start,
                type: 'button', class: buttonClass + " attendingmeet-button btn button btn-sm ",
                value: attending.attendingmeet_id
              }
              $("<button>").attr(buttonAttrs).text(attending.meet_name).appendTo(itemElement);
            });
          }
        }, // try this next https://supportcenter.devexpress.com/ticket/details/t717702
      },
      { // https://supportcenter.devexpress.com/ticket/details/t681806
        itemType: "button",
        name: "mainAttendeeFormSubmit",
        horizontalAlignment: "left",
        buttonOptions: {
          text: "Save",
          type: "success",
          useSubmitBehavior: true,
        },
        onClick: () => {
          console.log('mainAttendeeFormSubmit clicked!');
        }
      },
    ]

  },

  attendeeMainDxForm: null, // will be assigned later
  attendeeAttrs: null, // will be assigned later
  attendeeId: null, // will be assigned later
  attendingmeetPopupDxForm: null,

  initAttendeeForm: () => {
    Attendees.datagridUpdate.attendeeAttrs = document.querySelector('div.datagrid-attendee-update');
    Attendees.datagridUpdate.attendeeId = Attendees.datagridUpdate.attendeeAttrs.dataset.attendeeId;

    $.ajax
      ({
        url      : Attendees.datagridUpdate.attendeeAttrs.dataset.attendeeEndpoint + Attendees.datagridUpdate.attendeeId + '/',
        success  : (response) => {
                      Attendees.datagridUpdate.attendeeFormConfigs.formData = response.data[0];
                      Attendees.datagridUpdate.attendeeMainDxForm = $("div.datagrid-attendee-update").dxForm(Attendees.datagridUpdate.attendeeFormConfigs).dxForm("instance");
                      Attendees.datagridUpdate.initListeners();
                   },
//        error    : (response) => {
//                   },
      });

  },

  initAttendingmeetUpdate: (event) => {
    const meetButton = event.target;
    console.log("hi 96 clicked! here is meetButton.value: ", meetButton.value);

    $("div.popup-attendingmeet-update").dxPopup({
      visible: true,
      title: meetButton.innerText,
      minwidth: "30%",
      minheight: "30%",
      position: {
        my: 'center',
        at: 'center',
        of: window
      },
      dragEnabled: true,
      contentTemplate: (e) => {
        const formContainer = $("<div class='attendingMeetForm'>");
        Attendees.datagridUpdate.attendingmeetPopupDxForm = formContainer.dxForm({
          readOnly: false,
          showColonAfterLabel: false,
          labelLocation: "top",
          minColWidth: "20%",
          showValidationSummary: true,
          items: [
//              "hi there",
            {
              dataField: "customer_name",
              label: { text: "Name" },
              editorOptions: {
              },
              validationRules: [{
                type: "required",
                message: "Customer Name is required"
              }]
            },
            {
              itemType: "button",
              horizontalAlignment: "left",
              colSpan: 2,
              buttonOptions: {
                text: "Save",
                type: "success",
                useSubmitBehavior: false,
                onClick: function() {
                  console.log("attending meet popup submit button clicked!");
                  Attendees.datagridUpdate.attendeeMainDxForm.getEditor("mainAttendeeFormSubmit").option("useSubmitBehavior", false);
                  $("form#attendingmeet-update-popup-form").submit();
                }
              },
            },
//            { // https://supportcenter.devexpress.com/ticket/details/t681806
//              itemType: "button",
//              name: "attendingmeetPopupDxFormCancel",
//              horizontalAlignment: "left",
//              buttonOptions: {
//                text: "Cancel/Reset",
//                type: "reset",
//                useSubmitBehavior: false,
//                onClick: () => {
//                  console.log('attendingmeetPopupDxFormCancel clicked!');
////                  Attendees.datagridUpdate.attendingmeetPopupDxForm.cancelEditData();
//                },
//              },
//            },
          ]
        }).dxForm("instance");
        e.append(formContainer);
//        $("#popupForm").on("submit", function(e) {
//          alert('#popupForm submit pressed');
//        });
      }
    });

  },

  initListeners: () => {
    $("div.main-container").on("click", "button.attendingmeet-button",  e => Attendees.datagridUpdate.initAttendingmeetUpdate(e))
    // add listeners for Contact, etc.
  },
}

$(document).ready(() => {
  Attendees.datagridUpdate.init();
});
