Attendees.datagridUpdate = {
  attendeeMainDxForm: null,  // will be assigned later
  attendeeAttrs: null,  // will be assigned later
  attendeeId: null,  // will be assigned later
  attendingmeetPopupDxForm: null,  // will be assigned later
  attendingmeetPopup: null,  // will be assigned later

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
          useSubmitBehavior: false,
          onClick: (e) => {
            console.log("mainAttendeeFormSubmit clicked! here is : Attendees.datagridUpdate.attendeeMainDxForm.option('formData'): ", Attendees.datagridUpdate.attendeeMainDxForm.option('formData'));
            if (confirm("Are you sure?")){
              console.log("user confirmed");
              $("form#attendee-update-form").submit();
            }
          }
        },
      },
//      { // https://supportcenter.devexpress.com/ticket/details/t681806
//        itemType: "button",
//        name: "mainAttendeeFormReset",
//        horizontalAlignment: "left",
//        buttonOptions: {
//          text: "Cancel/Reset",
//          type: "reset",
//          useSubmitBehavior: false,
//          onClick: () => {
//            console.log('mainAttendeeFormReset clicked!');
//            Attendees.datagridUpdate.attendeeMainDxForm.resetValues();
//          },
//        },
//      },
    ]

  },

  initAttendeeForm: () => {
    Attendees.datagridUpdate.attendeeAttrs = document.querySelector('div.datagrid-attendee-update');
    Attendees.datagridUpdate.attendeeId = document.querySelector('input[name="attendee-id"]').value;

    $.ajax({
      url    : Attendees.datagridUpdate.attendeeAttrs.dataset.attendeeEndpoint + Attendees.datagridUpdate.attendeeId + '/',
      success: (response) => {
                 Attendees.datagridUpdate.attendeeFormConfigs.formData = response.data[0];
                 Attendees.datagridUpdate.attendeeMainDxForm = $("div.datagrid-attendee-update").dxForm(Attendees.datagridUpdate.attendeeFormConfigs).dxForm("instance");
                 Attendees.datagridUpdate.initListeners();
               },
      error  : (response) => {
                 console.log("Failed to fetch data in Attendees.datagridUpdate.initAttendeeForm(), error: ", response);
               },
    });

  },

  detchDataForAttendingmeetForm: (event) => {
    const meetButton = event.target;
    const ajaxUrl=$('form#attendingmeet-update-popup-form').attr('action') + meetButton.value + '/';

    $.ajax({
      url    : ajaxUrl,
      success: (response) => {
                 console.log("ajax for AttendingmeetForm success, here is the response: ", response);
                 Attendees.datagridUpdate.initAttendingmeetUpdate(response.data[0], meetButton, ajaxUrl);
               },
      error  : (response) => {
                 console.log("Failed to fetch data for AttendingmeetForm in Popup, error: ", response);
               },
    });
  },

  initAttendingmeetUpdate: (attendingmeetFormData, meetButton, ajaxUrl) => {
    Attendees.datagridUpdate.attendingmeetPopup = $("div.popup-attendingmeet-update").dxPopup({
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
        const formContainer = $('<div class="attendingMeetForm">');
        Attendees.datagridUpdate.attendingmeetPopupDxForm = formContainer.dxForm({
          formData: attendingmeetFormData,
          readOnly: false,
          showColonAfterLabel: false,
          labelLocation: "top",
          minColWidth: "20%",
          showValidationSummary: true,
          items: [
//            {
//              dataField: "customer_name",
//              label: { text: "Name" },
//              editorOptions: {
//              },
//              validationRules: [{
//                type: "required",
//                message: "Customer Name is required"
//              }]
//            },
            {
              dataField: "character_name",
              label: { text: "character_name" },
            },
            {
              dataField: "start",
              editorType: "dxDateBox",
              editorOptions: {
                type: "datetime",
              },
            },
            {
              dataField: "finish",
              editorType: "dxDateBox",
              editorOptions: {
                type: "datetime",
              },
            },
            {
              itemType: "button",
              horizontalAlignment: "left",
              colSpan: 2,
              buttonOptions: {
                text: "Save",
                type: "success",
                useSubmitBehavior: false,
                onClick: (clickEvent) => {
                  console.log("attending meet popup submit button clicked!");
                  if(confirm('are you sure to submit the popup attendingMeetForm?')){
                    console.log('user confirmed. Pretending Submitting popup attendingMeetForm by AJAX of formData: ', Attendees.datagridUpdate.attendingmeetPopupDxForm.option('formData'));  // clickEvent.component is the clicked button parent object, don't have form data
                    console.log("submitting to ajaxUrl: ", ajaxUrl);
                    Attendees.datagridUpdate.attendingmeetPopup.hide();
                  }
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
//                  Attendees.datagridUpdate.attendingmeetPopupDxForm.resetValues();
//                },
//              },
//            },
          ]
        }).dxForm("instance");
        e.append(formContainer);
      }
    }).dxPopup("instance");

  },

  initListeners: () => {
    $("div.main-container").on("click", "button.attendingmeet-button",  e => Attendees.datagridUpdate.detchDataForAttendingmeetForm(e))
    // add listeners for Contact, counselling, etc.
  },
}

$(document).ready(() => {
  Attendees.datagridUpdate.init();
});
