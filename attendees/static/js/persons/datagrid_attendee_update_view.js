Attendees.datagridUpdate = {
  attendeeMainDxForm: null,  // will be assigned later, may not needed if use native form.submit()?
  attendeeAttrs: null,  // will be assigned later
  attendeeId: null,  // the attendee is being edited, since it maybe admin/parent editing another attendee
  attendeeAjaxUrl: null,
  attendeePhotoFileUploader: null,
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
    Attendees.datagridUpdate.displayNotifiers();
    Attendees.datagridUpdate.initAttendeeForm();
  },

  initListeners: () => {
    $("div.nav-buttons").on("click", "input#custom-control-edit-checkbox", e => Attendees.datagridUpdate.toggleEditing(Attendees.utilities.toggleEditingAndReturnStatus(e)));
    $("div.form-container").on("click", "button.attendingmeet-button",  e => Attendees.datagridUpdate.initAttendingmeetPopupDxForm(e));
    // add listeners for Contact, counselling, etc.
  },

  toggleEditing: (enabled) => {
    $('div.attendee-form-submits').dxButton('instance').option('disabled', !enabled);
    $('button.attendingmeet-button-new, button.family-button-new, button.contact-button-new, input.form-check-input').prop('disabled', !enabled);
    Attendees.datagridUpdate.attendeeMainDxForm.option("readOnly", !enabled);
    Attendees.datagridUpdate.attendeePhotoFileUploader.option("disabled", !enabled);
    Attendees.datagridUpdate.attendingmeetPopupDxForm && Attendees.datagridUpdate.attendingmeetPopupDxForm.option("readOnly", !enabled);
  },

  displayNotifiers: ()=> {
    const params = new URLSearchParams(location.search);
    if (params.has('success')) {
      DevExpress.ui.notify(
        {
          message: params.get('success'),
          width: 500,
          position: {
            my: 'center',
            at: 'center',
            of: window,
          }
        }, "success", 2500);
      params.delete('success');
      history.replaceState(null, '', '?' + params + location.hash);
    }
  },

  initAttendeeForm: () => {
    Attendees.datagridUpdate.attendeeAttrs = document.querySelector('div.datagrid-attendee-update');
    Attendees.datagridUpdate.attendeeId = document.querySelector('input[name="attendee-id"]').value;
    Attendees.datagridUpdate.attendeeAjaxUrl = Attendees.datagridUpdate.attendeeAttrs.dataset.attendeeEndpoint + Attendees.datagridUpdate.attendeeId + '/';
    $.ajaxSetup({headers: {"X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val()}})
    $.ajax({
      url    : Attendees.datagridUpdate.attendeeAjaxUrl,
      success: (response) => {
                 Attendees.datagridUpdate.attendeeFormConfigs.formData = response.data[0];
                 $('h3.page-title').text('Details of ' + Attendees.datagridUpdate.attendeeFormConfigs.formData.full_name);
                 Attendees.datagridUpdate.attendeeMainDxForm = $("div.datagrid-attendee-update").dxForm(Attendees.datagridUpdate.attendeeFormConfigs).dxForm("instance");
                 Attendees.datagridUpdate.initListeners();
               },
      error  : (response) => {
                 console.log("Failed to fetch data in Attendees.datagridUpdate.initAttendeeForm(), error: ", response);
               },
    });

  },

  attendeeFormConfigs: {
    readOnly: !Attendees.utilities.editingEnabled,
    onContentReady: () => {
      $('div.spinner-border').hide();
    },
    colCount: 24,
    formData: null, // will be fetched
    items: [

      {
        colSpan: 20,
        colCount: 20,
        itemType: "group",
//        caption: "basic info",
        items: [

          {
            colSpan: 7,
//            caption: "colSpan: 7",
            itemType: "group",
            items: [
              {
                dataField: "division",
                editorType: "dxSelectBox",
                isRequired: true,
                label: {
                  text: 'Major Division',
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
                dataField: "gender",
                editorType: "dxSelectBox",
                isRequired: true,
                editorOptions: {
                  dataSource: Attendees.utilities.genderEnums(),
                  valueExpr: "name",
                  displayExpr: "name",
                },
              },
              {
                dataField: "actual_birthday",
                editorType: "dxDateBox",
                editorOptions: {
                  placeholder: "click calendar",
                  elementAttr: {
                    title: 'month, day and year are all required',
                  },
                },
              },
            ],
          },
          {
            colSpan: 7,
//            caption: "colSpan: 7",
            itemType: "group",
            items: [
              {
                dataField: "first_name",
                editorOptions: {
                  placeholder: "English",
                },
              },
              {
                dataField: "last_name2",
              },
              {
                dataField: "estimated_birthday",
                editorType: "dxDateBox",
                editorOptions: {
                  placeholder: "click calendar",
                  elementAttr: {
                    title: 'pick any day of your best guess year for the age estimation',
                  },
                },
              },
            ],
          },
          {
            colSpan: 6,
//            caption: "colSpan: 6",
            itemType: "group",
            items: [
              {
                dataField: "last_name",
                editorOptions: {
                  placeholder: "English",
                },
              },
              {
                dataField: "first_name2",
              },
              {
                dataField: "deathday",
                editorType: "dxDateBox",
                editorOptions: {
                  placeholder: "click calendar",
                },
              },
            ],
          },
          {
            colSpan: 20,
            dataField: "attendeecontact_set",
            label: {
              text: 'addresses',
            },
            template: (data, itemElement) => {
              $("<button>").attr({disabled: !Attendees.utilities.editingEnabled, title: "+ Add the attendee to a new address", type: 'button', class: "contact-button-new contact-button btn-outline-primary btn button btn-sm "}).text("Add new address+").appendTo(itemElement);
              if (data.editorOptions && data.editorOptions.value && data.editorOptions.value > 1){
                data.editorOptions.value.forEach(attendeeContact => {
                  const $button = $('<button>', {
                    type: 'button',
                    class: "btn-outline-success contact-button btn button btn-sm attendee-contact-set", // or use btn-block class
                    value: attendeeContact.id,
                    text: attendeeContact.contact.street,
//                    'data-attendeecontact-id': attendeeContact.id,
                  });
                  itemElement.append($button);
                });
              }
            },
          },
          {
            colSpan: 20,
            colCount: 20,
//            caption: "20",
            itemType: "group",
            items: [
              {
                colSpan: 3,
                dataField: "attendeecontact_set[0]",
                name: "attendeecontact_set[0].display_name",
                label: {
                  visible: false,
//                  text: 'address type',
                },
                template: (data, itemElement) => {
                  if (data.editorOptions && data.editorOptions.value){
                    const $button = $('<button>', {
                      type: 'button',
                      title: "editing type of the address",
                      class: "btn-light attendeecontact-display-name btn button btn-sm attendee-contact-set",
                      value: data.editorOptions.value.id,
                      text: data.editorOptions.value.display_name,
                    });
                    itemElement.append($button);
                  }
                },
              },
              {
                colSpan: 17,
//                caption: "colSpan: 17",
                dataField: "attendeecontact_set[0]",
                name: "attendeecontact_set[0].contact.street",
                label: {
                  text: 'address',
                },
                template: (data, itemElement) => {
                  if (data.editorOptions && data.editorOptions.value){
                    const $button = $('<button>', {
                      type: 'button',
                      title: "editing street of the address",
                      class: "btn-outline-dark street btn button btn-sm attendee-contact-set",
                      value: data.editorOptions.value.id,
                      text: data.editorOptions.value.contact.street,
                    });
                    itemElement.append($button);
                  }
                },
              },
              {
                colSpan: 5,
                dataField: "attendeecontact_set[0]",
                name: "attendeecontact_set[0].contact.fields.fixed.phone1",
                label: {
                  text: 'phone',
                },
                template: (data, itemElement) => {
                  if (data.editorOptions && data.editorOptions.value){
                    const $button = $('<button>', {
                      type: 'button',
                      title: "editing phone1 in address",
                      class: "btn-outline-dark phone1 btn button btn-sm attendee-contact-set",
                      value: data.editorOptions.value.id,
                      text: data.editorOptions.value.contact.fields.fixed.phone1,
                    });
                    itemElement.append($button);
                  }
                },
              },
              {
                colSpan: 5,
                dataField: "attendeecontact_set[0]",
                name: "attendeecontact_set[0].contact.fields.fixed.phone2",
                label: {
                  visible: false,
                },
                template: (data, itemElement) => {
                  if (data.editorOptions && data.editorOptions.value){
                    const $button = $('<button>', {
                      type: 'button',
                      title: "editing phone2 in address",
                      class: "btn-outline-dark phone2 btn button btn-sm attendee-contact-set-first",
                      value: data.editorOptions.value.id,
                      text: data.editorOptions.value.contact.fields.fixed.phone2,
                    });
                    itemElement.append($button);
                  }
                },
              },
              {
                colSpan: 5,
                dataField: "attendeecontact_set[0]",
                name: "attendeecontact_set[0].contact.fields.fixed.email1",
                label: {
                  text: 'email',
                },
                template: (data, itemElement) => {
                  if (data.editorOptions && data.editorOptions.value){
                    const $button = $('<button>', {
                      type: 'button',
                      title: "editing email1 in address",
                      class: "btn-outline-dark email1 btn button btn-sm attendee-contact-set-first",
                      value: data.editorOptions.value.id,
                      text: data.editorOptions.value.contact.fields.fixed.email1,
                    });
                    itemElement.append($button);
                  }
                },
              },
              {
                colSpan: 5,
                dataField: "attendeecontact_set[0]",
                name: "attendeecontact_set[0].contact.fields.fixed.email2",
                label: {
                  visible: false,
                },
                template: (data, itemElement) => {
                  if (data.editorOptions && data.editorOptions.value){
                    const $button = $('<button>', {
                      type: 'button',
                      title: "editing email2 in address",
                      class: "btn-outline-dark email2 btn button btn-sm attendee-contact-set-first",
                      value: data.editorOptions.value.id,
                      text: data.editorOptions.value.contact.fields.fixed.email2,
                    });
                    itemElement.append($button);
                  }
                },
              },
            ],
          },
          {
            colSpan: 20,
            dataField: "familyattendee_set",
            label: {
              text: 'families',
            },
            template: (data, itemElement) => {
              $("<button>").attr({disabled: !Attendees.utilities.editingEnabled, title: "+ Add the attendee to a new family", type: 'button', class: "family-button-new family-button btn-outline-primary btn button btn-sm "}).text("Join new family+").appendTo(itemElement);
              if (data.editorOptions && data.editorOptions.value){
                data.editorOptions.value.forEach(familyAttendee => {
                  const buttonAttrs = {
//                    title: "since " + familyAttendee.created,  // waiting for FamilyAttendee.start/finish or from infos fields
                    type: 'button', class: "btn-outline-success family-button btn button btn-sm ",
                    value: familyAttendee.family.id,
                  }
                  $("<button>").attr(buttonAttrs).text(familyAttendee.family.display_name).appendTo(itemElement);
                });
              }
            },
          },
        ],
      },
      {
        colSpan: 4,
        itemType: "group",
//        caption: "photo",
        items: [

          {
            dataField: 'photo',
            label: {
              // location: 'top',
              text: ' ',  // empty space required for removing label
              showColon: false,
            },
            template: (data, itemElement) => {
              if (data.editorOptions && data.editorOptions.value){
                const $img = $('<img>', {src: data.editorOptions.value, class: 'attendee-photo-img'});
                const $imgLink = $('<a>', {href: data.editorOptions.value, target: '_blank'});
                itemElement.append($imgLink.append($img));
                // Todo: add check/uncheck photo-clear feature, store img link in data attributes when marking deleted
                const $inputDiv = $('<div>', {class: 'form-check', title: "If checked, it'll be deleted when you save"});
                const $clearInput = $('<input>', {
                  id: 'photo-clear',
                  disabled: !Attendees.utilities.editingEnabled,
                  type: 'checkbox',
                  name: 'photo-clear',
                  class: 'form-check-input',
                  onclick: "return confirm('Are you sure?')"
                });
                const $clearInputLabel = $('<label>', {for: 'photo-clear', text: 'delete photo', class: 'form-check-label'});
                $inputDiv.append($clearInput);
                $inputDiv.append($clearInputLabel);
                itemElement.append($inputDiv);
              } else {
                $('<img>', {src: $('div.datagrid-attendee-update').data('empty-image-link'), class: 'attendee-photo-img'}).appendTo(itemElement);
              }
            },
          },
          {
            template: (data, itemElement) => {
              photoFileUploader = $("<div>").attr("id", "dxfu1").dxFileUploader(
              {
                name: 'photo',
                disabled: !Attendees.utilities.editingEnabled,
                selectButtonText: "Select photo",
//                  labelText: "hi5",
                accept: "image/*",
                multiple: false,
                uploadMode: "useForm",
                onValueChanged: (e) => {
                  if (e.value.length) {
                    $('img.attendee-photo-img')[0].src = (window.URL ? URL : webkitURL).createObjectURL(e.value[0]);
                    Attendees.datagridUpdate.attendeeFormConfigs.formData['photo'] = e.value[0];
                  }
                },
              });
              Attendees.datagridUpdate.attendeePhotoFileUploader = photoFileUploader.dxFileUploader("instance");
              itemElement.append(photoFileUploader);
            },
          },
        ],
      },
      {
        colSpan: 24,
        dataField: "joined_meets",
        label: {
          text: 'joins',
        },
        template: (data, itemElement) => {
          $("<button>").attr({disabled: !Attendees.utilities.editingEnabled, title: "+ Add a new meet", type: 'button', class: "attendingmeet-button-new attendingmeet-button btn-outline-primary btn button btn-sm "}).text("Attend new +").appendTo(itemElement);
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
          text: "Save Attendee details and photo",
          icon: "save",
          hint: "save attendee data in the page",
          type: "default",
          useSubmitBehavior: false,
          onClick: (e) => {
            if (confirm("Are you sure?")){

              const userData = new FormData($('form#attendee-update-form')[0]);
              if(!$('input[name="photo"]')[0].value){userData.delete("photo")};

              userData._method = userData.id ? 'PUT' : 'POST';

              $.ajax({
                url    : Attendees.datagridUpdate.attendeeAjaxUrl,
                contentType: false,
                processData: false,
                dataType: 'json',
                data   : userData,
                method : 'POST',
                success: (response) => {  // Todo: update photo link, temporarily reload to bypass the requirement
                           console.log("success here is response: ", response);
                           const parser = new URL(window.location);
                           parser.searchParams.set('success', 'Saving attendee success');
                           window.location = parser.href;
                         },
                error  : (response) => {
                           console.log('Failed to save data for main AttendeeForm, error: ', response);
                           console.log('formData: ', [...userData]);
                           DevExpress.ui.notify(
                             {
                               message: "saving attendee error",
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
          readOnly: !Attendees.utilities.editingEnabled,
          formData: Attendees.datagridUpdate.attendingmeetDefaults,
          colCount: 2,
          scrollingEnabled: true,
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
              colSpan: 2,
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
              colSpan: 3,
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
                helpText: 'help text can be changed in /static/js /persons /datagrid_attendee_update_view.js',
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
                text: "Save Participation",
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
                                 console.log('Failed to save data for AttendingmeetForm in Popup, error: ', response);
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
