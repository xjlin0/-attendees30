Attendees.datagridUpdate = {
  attendeeMainDxForm: null,  // will be assigned later, may not needed if use native form.submit()?
  attendeeAttrs: null,  // will be assigned later
  attendeeId: null,  // the attendee is being edited, since it maybe admin/parent editing another attendee
  attendingmeetPopupDxForm: null,  // for getting formData
  attendingmeetPopupDxFormData: {},  // for storing formData
  attendingmeetPopupDxFormCharacterSelect: null,
  attendingmeetPopup: null,  // for show/hide popup
  attendingmeetDefaults: {
    category: 'primary',
    start: new Date(),
    finish: new Date().setFullYear(new Date().getFullYear() + 1), // 1 years from now
  },

  init: () => {
    console.log("/static/js/persons/datagrid_attendee_update_view.js");
    Attendees.datagridUpdate.initAttendeeForm();
  },

  initListeners: () => {
    $("div.nav-buttons").on("click", "input#custom-control-edit-checkbox", e => Attendees.datagridUpdate.toggleEditing(Attendees.utilities.toggleEditingAndReturnStatus(e)));
    $("div.main-container").on("click", "button.attendingmeet-button",  e => Attendees.datagridUpdate.initAttendingmeetPopupDxForm(e));
    // add listeners for Contact, counselling, etc.
  },

  toggleEditing: (enabled) => {
    $('div.attendee-form-submits').dxButton('instance').option('disabled', !enabled);
    $('button.attendingmeet-button-new').prop('disabled', !enabled);
  },

  initAttendeeForm: () => {
    Attendees.datagridUpdate.attendeeAttrs = document.querySelector('div.datagrid-attendee-update');
    Attendees.datagridUpdate.attendeeId = document.querySelector('input[name="attendee-id"]').value;
    $.ajaxSetup({headers: {"X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val()}})
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

  attendeeFormConfigs: {

    formData: null, // will be fetched
    items: [
      {
        dataField: "division",
        editorType: "dxSelectBox",
  //              disabled: true,
        isRequired: true,
        label: {
          text: 'Major Division',
          showColon: true,
        },
        editorOptions: {
          valueExpr: "id",
          displayExpr: "display_name",
          placeholder: "Select a value...",
          dataSource: new DevExpress.data.DataSource({
            store: new DevExpress.data.CustomStore({
              key: "id",
              loadMode: "raw",
              load: () => {
                const d = $.Deferred();
                $.get($('div.datagrid-attendee-update').data('divisions-endpoint')).done((response) => {
                  d.resolve(response.data);
                });
                return d.promise();
              }
            })
          }),
        },
      },
      {
          dataField: "first_name",
          isRequired: true,
      },
      {
          dataField: "full_name",
          disabled: true,
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
          $("<button>").attr({disabled: !Attendees.utilities.editingEnabled, title: "+ Add a new meet", type: 'button', class: "attendingmeet-button-new attendingmeet-button btn-outline-primary btn button btn-sm "}).text("Attend new meet").appendTo(itemElement);
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
          elementAttr: {
            class: 'attendee-form-submits',
          },
          disabled: !Attendees.utilities.editingEnabled,
          text: "Save",
          icon: "save",
          hint: "save attendee data in the page",
          type: "default",
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
        of: window,
      },
      dragEnabled: true,
      contentTemplate: (e) => {
        const formContainer = $('<div class="attendingMeetForm">');
        Attendees.datagridUpdate.attendingmeetPopupDxForm = formContainer.dxForm({
          formData: Attendees.datagridUpdate.attendingmeetDefaults,
          scrollingEnabled: true,
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
            {
              dataField: "attending",
              editorType: "dxSelectBox",
//              disabled: true,
              editorOptions: {
                valueExpr: "id",
                displayExpr: "attending_label",
                placeholder: "Select a value...",
                dataSource: new DevExpress.data.DataSource({
                    store: new DevExpress.data.CustomStore({
                        key: "id",
                        loadMode: "raw",
                        load: () => {
                          const d = $.Deferred();
                          const attendeeData={'attendee-id': Attendees.datagridUpdate.attendeeId}; // maybe header is safer
                          $.get($('div.datagrid-attendee-update').data('attendings-endpoint'), attendeeData).done((response) => {
                              d.resolve(response.data)
                          });
                          return d.promise();
                        }
                    })
                }),
              },
            },
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
                dataField: "category",
                helpText: 'help text can be changed in /static/js/persons/datagrid_attendee_update_view.js',
                isRequired: true,
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
//              colSpan: 2,
              buttonOptions: {
                elementAttr: {
                  class: 'attendee-form-submits',
                },
                disabled: !Attendees.utilities.editingEnabled,
                text: "Save",
                icon: "save",
                hint: "save attendingmeet data in the popup",
                type: "default",
                useSubmitBehavior: false,
                onClick: (clickEvent) => {
                  if(confirm('are you sure to submit the popup attendingMeetForm?')){
                    const userData = Attendees.datagridUpdate.attendingmeetPopupDxForm.option('formData');
                    userData._method = userData.id ? 'PUT' : 'POST';

                    $.ajax({
                      url    : ajaxUrl,
                      data   : userData,
                      method : 'POST',
                      success: (response) => {
                                 Attendees.datagridUpdate.attendingmeetPopup.hide();
                                 DevExpress.ui.notify(
                                   {
                                     message: "saving attendingmeet success",
                                     width: 500,
                                     position: {
                                      my: 'center',
                                      at: 'center',
                                      of: window,
                                     }
                                    }, "success", 2500);
                               },
                      error  : (response) => {
                                 console.log('Failed to fetch data for AttendingmeetForm in Popup, error: ', response);
                                 console.log('formData: ', userData);
                                 DevExpress.ui.notify(
                                   {
                                     message: "saving attendingmeet error",
                                     width: 500,
                                     position: {
                                      my: 'center',
                                      at: 'center',
                                      of: window,
                                     }
                                    }, "error", 5000);
                      },
                    });
                  }
                }
              },
            },
//            {
//              itemType: "button",
//              horizontalAlignment: "left",
//              buttonOptions: {
//                text: "Cancel",
//                icon: "close",
//                hint: "don't save and close the pop up",
//                type: "normal",
//                onClick: (clickEvent) => {
//                  if(confirm('are you sure to cancel your change and close the popup?')){
//                    Attendees.datagridUpdate.attendingmeetPopup.hide();
//                  }
//                }
//              },
//            },
          ]
        }).dxForm("instance");
        e.append(formContainer);
      }
    };

  },
}

$(document).ready(() => {
  Attendees.datagridUpdate.init();
});
