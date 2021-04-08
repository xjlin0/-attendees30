Attendees.datagridUpdate = {
  attendeeMainDxForm: null,  // will be assigned later, may not needed if use native form.submit()?
  attendeeAttrs: null,  // will be assigned later
  attendeeId: null,  // the attendee is being edited, since it maybe admin/parent editing another attendee
  attendingmeetPopupDxForm: null,  // for getting formData
  attendingmeetPopupDxFormData: {},  // for storing formData
  attendingmeetPopupDxFormCharacterSelect: null,
  attendingmeetPopup: null,  // for show/hide popup

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
              $("<img>").attr({src: data.editorOptions.value, class: "attendee-photo"}).appendTo(itemElement);
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
        label: {
          text: 'Participation (joined meets)',
        },
        template: (data, itemElement) => {
          $("<button>").attr({title: "+ Add a new meet", type: 'button', class: "attendingmeet-button btn-outline-primary btn button btn-sm "}).text("Attend new meet").appendTo(itemElement);
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

  initAttendingmeetPopupDxForm: (event) => {
    const meetButton = event.target;
    Attendees.datagridUpdate.attendingmeetPopup = $("div.popup-attendingmeet-update").dxPopup(Attendees.datagridUpdate.attendingmeetPopupDxFormConfig(meetButton)).dxPopup("instance");
    Attendees.datagridUpdate.fetchAttendingmeetFormData(meetButton);
  },

  fetchAttendingmeetFormData: (meetButton) => {
    if (meetButton.value){
      $.ajax({
        url    : $('form#attendingmeet-update-popup-form').attr('action') + meetButton.value + '/',
        success: (response) => {
                   Attendees.datagridUpdate.attendingmeetPopupDxFormData = response.data[0];
                   Attendees.datagridUpdate.attendingmeetPopupDxForm.option('formData', response.data[0]);
                 },
        error  : (response) => console.log("Failed to fetch data for AttendingmeetForm in Popup, error: ", response),
      });
    }
  },

  attendingmeetPopupDxFormConfig: (meetButton) => {
    const ajaxUrl=$('form#attendingmeet-update-popup-form').attr('action') + meetButton.value + '/';
    return {
      visible: true,
      title: meetButton.value ? 'Viewing participation' : 'Creating participation',
      minwidth: "20%",
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
          formData: {},
          readOnly: false,
          showColonAfterLabel: false,
          requiredMark: "*",
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
//            {
//              dataField: "division",
//              editorType: "dxSelectBox",
//              disabled: true,
//              editorOptions: {
//                valueExpr: "id",
//                displayExpr: "display_name",
//                placeholder: "Select a value...",
//                dataSource: new DevExpress.data.DataSource({
//                    store: new DevExpress.data.CustomStore({
//                        key: "id",
//                        loadMode: "raw",
//                        load: () => {
//                          const d = $.Deferred();
//                          $.get($('div.datagrid-attendee-update').data('divisions-endpoint')).done((response) => {
//                              d.resolve(response.data)
//                          });
//                          return d.promise();
//                        }
//                    })
//                }),
//              },
//            },
            {
              dataField: "assembly",
              editorType: "dxSelectBox",
//              disabled: true,
              isRequired: true,
              label: {
                text: 'Belonging Group (Assembly)',
                showColon: true,
              },
              editorOptions: {
                valueExpr: "id",
                displayExpr: "division_assembly_name",
                placeholder: "Select a value...",
                dataSource: new DevExpress.data.DataSource({
                  store: new DevExpress.data.CustomStore({
                    key: "id",
                    loadMode: "raw",
                    load: () => {
                      const d = $.Deferred();
                      $.get($('div.datagrid-attendee-update').data('assemblies-endpoint')).done((response) => {
                        d.resolve(response.data);
                      });
                      return d.promise();
                    }
                  })
                }),
                onValueChanged: (e) => {
                  const characterSelectBox = Attendees.datagridUpdate.attendingmeetPopupDxForm.getEditor("character");
                  const meetSelectBox = Attendees.datagridUpdate.attendingmeetPopupDxForm.getEditor("meet");
                  meetSelectBox.getDataSource().reload();
                  meetSelectBox.reset();
                  characterSelectBox.getDataSource().reload();
                  characterSelectBox.reset();
                },
              },
            },
            {
              dataField: "meet",
              editorType: "dxSelectBox",
//              disabled: true,
              isRequired: true,
              label: {
                text: 'Participating activity',
                showColon: true,
              },
              editorOptions: {
                showClearButton: true,
                valueExpr: "id",
                displayExpr: "display_name",
                placeholder: "Select a value...",
                dataSource: new DevExpress.data.DataSource({
                  store: new DevExpress.data.CustomStore({
                    key: "id",
                    loadMode: "raw",
                    load: () => {
                      const selectedAssemblyId = Attendees.datagridUpdate.attendingmeetPopupDxForm.option('formData').assembly;
                      if (selectedAssemblyId){
                        const d = $.Deferred();
                        const data = {'assemblies[]': selectedAssemblyId};
                        $.get($('div.datagrid-attendee-update').data('meets-endpoint'), data).done((response) => {
                          d.resolve(response.data);
                        });
                        return d.promise();
                      }
                    }
                  })
                }),
                onValueChanged: (e) => {
                  const characterSelectBox = Attendees.datagridUpdate.attendingmeetPopupDxForm.getEditor("character");
                  characterSelectBox.getDataSource().reload();
                  characterSelectBox.reset();
                },
              },
            },
            {
              dataField: "character",
              editorType: "dxSelectBox",
//              disabled: true,
              label: {
                text: '(Optional) Participating character',
                showColon: true,
              },
              editorOptions: {
                showClearButton: true,
                valueExpr: "id",
                displayExpr: "display_name",
                placeholder: "Select a value...",
                dataSource: new DevExpress.data.DataSource({
                  store: new DevExpress.data.CustomStore({
                    key: "id",
                    loadMode: "raw",
                    load: () => {
                      const selectedAssemblyId = Attendees.datagridUpdate.attendingmeetPopupDxForm.option('formData').assembly;
                      if (selectedAssemblyId){
                        const d = $.Deferred();
                        const data = {'assemblies[]': selectedAssemblyId};
                        $.get($('div.datagrid-attendee-update').data('characters-endpoint'), data).done((response) => {
                          d.resolve(response.data);
                        });
                        return d.promise();
                      }
                    }
                  })
                }),
              },
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
                  if(confirm('are you sure to submit the popup attendingMeetForm?')){
                    console.log('user confirmed. Pretending Submitting popup attendingMeetForm by AJAX of formData: ', Attendees.datagridUpdate.attendingmeetPopupDxForm.option('formData'));  // clickEvent.component is the clicked button parent object, don't have form data
                    console.log("pretend submitting to ajaxUrl: ", ajaxUrl);
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
    };

  },

  initListeners: () => {
    $("div.main-container").on("click", "button.attendingmeet-button",  e => Attendees.datagridUpdate.initAttendingmeetPopupDxForm(e))
    // add listeners for Contact, counselling, etc.
  },
}

$(document).ready(() => {
  Attendees.datagridUpdate.init();
});
