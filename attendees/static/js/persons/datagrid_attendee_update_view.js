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
  addressId: null, // for sending address data by AJAX
  placePopup: null, // for show/hide popup
  placePopupDxForm: null,  // for getting formData
  placePopupDxFormData: {},  // for storing formData
  placeDefaults: {
    address: {},
    display_order: 0,
    display_name: 'other',
    content_type: parseInt(document.querySelector('div.datagrid-attendee-update').dataset.attendeeContenttypeId),
  },
  familyAttrPopup: null,

  init: () => {
    console.log("/static/js/persons/datagrid_attendee_update_view.js");
    Attendees.datagridUpdate.displayNotifiers();
    Attendees.datagridUpdate.initAttendeeForm();
  },

  initListeners: () => {
    $("div.nav-buttons").on("click", "input#custom-control-edit-checkbox", e => Attendees.datagridUpdate.toggleEditing(Attendees.utilities.toggleEditingAndReturnStatus(e)));
    $("div.form-container").on("click", "button.attendingmeet-button",  e => Attendees.datagridUpdate.initAttendingmeetPopupDxForm(e));
    $("div.form-container").on("click", "button.attendee-place-button",  e => Attendees.datagridUpdate.initPlacePopupDxForm(e));
    $("div.form-container").on("click", "button.family-button",  e => Attendees.datagridUpdate.initFamilyAttrPopupDxForm(e));
    // add listeners for Family, counselling, etc.
  },

  toggleEditing: (enabled) => {
    $('div.attendee-form-submits').dxButton('instance').option('disabled', !enabled);
    $('button.attendingmeet-button-new, button.family-button-new, button.place-button-new, input.form-check-input').prop('disabled', !enabled);
    Attendees.datagridUpdate.attendeeMainDxForm.option("readOnly", !enabled);
    Attendees.datagridUpdate.attendeePhotoFileUploader.option("disabled", !enabled);
    Attendees.datagridUpdate.attendingmeetPopupDxForm && Attendees.datagridUpdate.attendingmeetPopupDxForm.option("readOnly", !enabled);
    $("div#family-attendee-datagrid-container").dxDataGrid("instance").clearGrouping();
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


  ///////////////////////  Main Attendee DxForm and Submit ///////////////////////


  initAttendeeForm: () => {
    Attendees.datagridUpdate.attendeeAttrs = document.querySelector('div.datagrid-attendee-update');
    Attendees.datagridUpdate.attendeeId = document.querySelector('input[name="attendee-id"]').value;
    Attendees.datagridUpdate.placeDefaults.object_id = Attendees.datagridUpdate.attendeeId;
    Attendees.datagridUpdate.attendeeAjaxUrl = Attendees.datagridUpdate.attendeeAttrs.dataset.attendeeEndpoint + Attendees.datagridUpdate.attendeeId + '/';
    $.ajaxSetup({headers: {"X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val()}})
    $.ajax({
      url    : Attendees.datagridUpdate.attendeeAjaxUrl,
      success: (response) => {
                 Attendees.datagridUpdate.attendeeFormConfigs.formData = response.data[0];
                 $('h3.page-title').text('Details of ' + Attendees.datagridUpdate.attendeeFormConfigs.formData.full_name);
                 window.top.document.title = Attendees.datagridUpdate.attendeeFormConfigs.formData.full_name;
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
      Attendees.utilities.toggleDxFormGroups();
    },
    colCount: 24,
    formData: null, // will be fetched
    items: [
      {
        colSpan: 4,
        itemType: "group",
        caption: "Photo",
        items: [

          {
            dataField: 'photo',
            label: {
              location: 'top',
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
        colSpan: 20,
        colCount: 20,
        itemType: "group",
        caption: "Basic info",
        items: [
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
                validationRules: [
                  {
                    type: "required",
                    message: "gender is required"
                  },
                ],
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
        ],
      },
      {
        colSpan: 24,
        colCount: 24,
        caption: "Families or Relations",
        itemType: "group",
        items: [
          {
            colSpan: 24,
            dataField: "familyattendee_set",
            name: "familyAttrs",
            label: {
              text: 'families',
            },
            template: (data, itemElement) => {
              $("<button>", {
                text: "Join new family+",
                disabled: !Attendees.utilities.editingEnabled,
                title: "+ Add the attendee to a new family",
                type: 'button',
                class: "family-button-new family-button btn-outline-primary btn button btn-sm ",
              }).appendTo(itemElement);
              if (data.editorOptions && data.editorOptions.value){
                data.editorOptions.value.forEach(familyAttendee => {
                  if (familyAttendee && typeof familyAttendee === 'object') {
                    $("<button>", {
                      text: familyAttendee.family.display_name,
                      type: 'button',
                      class: "btn-outline-success family-button btn button btn-sm ",
                      value: familyAttendee.family.id,
                    }).appendTo(itemElement);
                  }
                });
              }
            },
          },
          {
            colSpan: 24,
            dataField: "familyattendee_set",
            name: "familyAttendeeDatagrid",
            label: {
              location: 'top',
              text: ' ',  // empty space required for removing label
              showColon: false,
            },
            template: (data, itemElement) => Attendees.datagridUpdate.initFamilyAttendeeDatagrid(data, itemElement),
          }
        ],
      },
      {
        colSpan: 24,
        colCount: 24,
        caption: "Contacts",
        itemType: "group",
        items: [
          {
            colSpan: 7,
            dataField: "infos.contacts.phone1",
            label: {
              text: 'phone',
            },
          },
          {
            colSpan: 5,
            dataField: "infos.contacts.phone2",
            label: {
              visible: false,
            },
          },
          {
            colSpan: 7,
            dataField: "infos.contacts.email1",
            label: {
              text: 'email',
            },
          },
          {
            colSpan: 5,
            dataField: "infos.contacts.email2",
            label: {
              visible: false,
            },
          },
          {
            colSpan: 24,
            dataField: "places",
            label: {
              text: 'address',
            },
            template: (data, itemElement) => {
              $("<button>", {
                text: "Add new address+",
                disabled: !Attendees.utilities.editingEnabled,
                title: "+ Add the attendee to a new address",
                type: 'button',
                class: "place-button-new place-button btn-outline-primary btn button btn-sm ",
              }).appendTo(itemElement);
              if (data.editorOptions && data.editorOptions.value){
                data.editorOptions.value.forEach(place => {
                  if (place.id && typeof place === 'object'){
                    const $button = $('<button>', {
                      type: 'button',
                      class: "btn-outline-success place-button btn button btn-sm attendee-place-button", // or use btn-block class
                      value: place.id,
                      text: (place.display_name ? place.display_name + ': ' : '' ) + (place.street || '').replace(', USA', ''),
                    });
                    itemElement.append($button);
                  }
                });
              }
            },
          },
        ],
      },
      {
        colSpan: 24,
        colCount: 24,
        caption: "Groups",
        itemType: "group",
        items: [

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
                  if (attending && attending.attendingmeet_id) {
                    const buttonClass = Date.now() < Date.parse(attending.attending_finish) ? 'btn-outline-success' : 'btn-outline-secondary';
                    $("<button>", {
                      text: attending.meet_name,
                      title: "since " + attending.attending_start,
                      type: 'button', class: buttonClass + " attendingmeet-button btn button btn-sm ",
                      value: attending.attendingmeet_id
                    }).appendTo(itemElement);
                  }
                });
              }
            }, // try this next https://supportcenter.devexpress.com/ticket/details/t717702
          },
        ],
      },
      { // https://supportcenter.devexpress.com/ticket/details/t681806
        itemType: "button",
        name: "mainAttendeeFormSubmit",
        horizontalAlignment: "left",
        buttonOptions: {
          elementAttr: {
            class: 'attendee-form-submits',  // for toggling editing mode
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


  ///////////////////////  Attending Meet Popup and DxForm  ///////////////////////


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
                   Attendees.datagridUpdate.attendingmeetPopupDxForm.option('onFieldDataChanged', (e) => {e.component.validate()});
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
                    },
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
                    },
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
                    },
                  }),
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
              buttonOptions: {
                elementAttr: {
                  class: 'attendee-form-submits',    // for toggling editing mode
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


  ///////////////////////  Place (Address) Popup and DxForm  ///////////////////////


  initPlacePopupDxForm: (event) => {
    const placeButton = event.target;
    Attendees.datagridUpdate.placePopup = $('div.popup-place-update').dxPopup(Attendees.datagridUpdate.locatePopupDxFormConfig(placeButton)).dxPopup('instance');
    Attendees.datagridUpdate.fetchLocateFormData(placeButton);
  },

  locatePopupDxFormConfig: (placeButton) => {
    const ajaxUrl=$('form#place-update-popup-form').attr('action') + placeButton.value + '/';
    return {
      visible: true,
      title: placeButton.value ? 'Viewing Address' : 'Creating Address',
      minwidth: "20%",
      minheight: "30%",
      position: {
        my: 'center',
        at: 'center',
        of: window,
      },
      onHiding: () => {
        const $existingAddressSelector = $('div.address-lookup-search').dxLookup('instance');
        if ($existingAddressSelector) $existingAddressSelector.close();
        const $existingStateSelector = $('div.state-lookup-search').dxLookup('instance');
        if ($existingStateSelector) $existingStateSelector.close();
      },
      dragEnabled: true,
      contentTemplate: (e) => {
        const formContainer = $('<div class="locate-form">');
        Attendees.datagridUpdate.placePopupDxForm = formContainer.dxForm({
          // repaintChangesOnly: true,  // https://github.com/DevExpress/DevExtreme/issues/7295
          readOnly: !Attendees.utilities.editingEnabled,
          formData: Attendees.datagridUpdate.placeDefaults,
          colCount: 12,
          scrollingEnabled: true,
          showColonAfterLabel: false,
          requiredMark: "*",
          labelLocation: "top",
          minColWidth: "20%",
          showValidationSummary: true,
          items: [
            {
              colSpan: 3,
              dataField: "display_name",
              label: {
                text: 'Type',
              },
              helpText: 'what kind of address is this?',
              isRequired: true,
              editorOptions: {
                placeholder: "Main/parent/past, etc",
              },
            },
            {
              colSpan: 3,
              dataField: "display_order",
              label: {
                text: 'Importance',
              },
              helpText: '0 is shown before 1,2...',
              isRequired: true,
              editorOptions: {
                placeholder: "0/1/2/3, etc",
              },
              validationRules: [
                {
                  type: "range",
                  max: 32767,
                  min: 0,
                  message: "display_order should be between 0 and 32767"
                },
                {
                  type: "required",
                  message: "display_order is required"
                },
              ],
            },
            {
              colSpan: 3,
              dataField: "start",
              editorType: "dxDateBox",
              label: {
                text: 'stay from',
              },
              helpText: 'When moved in?',
              editorOptions: {
                type: "date",
                showClearButton: true,
                dateSerializationFormat: "yyyy-MM-dd",
                onFocusIn: (e) => {
                  if(!e.component.option("value")) {e.component.option("value", new Date())};
                },
                placeholder: "click calendar",
              },
            },
            {
              colSpan: 3,
              dataField: "finish",
              editorType: "dxDateBox",
              label: {
                text: 'stay until',
              },
              helpText: 'When moved out?',
              editorOptions: {
                type: "date",
                showClearButton: true,
                onFocusIn: (e) => {
                  if(!e.component.option("value")) {e.component.option("value", new Date())};
                },
                placeholder: "click calendar",
              },
            },
            {
              colSpan: 12,
              dataField: "address.id",
              name: "existingAddressSelector",
              label: {
                text: 'Address',
              },
              editorType: "dxLookup",
              editorOptions: {
                elementAttr: {
                  class: 'address-lookup-search',  // calling closing by the parent
                },
                valueExpr: "id",
                displayExpr: "raw",  // 'formatted' does not exist
                placeholder: "Select a value...",
                searchExpr: ['street_number', 'raw'],
//                searchMode: 'startswith',
                searchPlaceholder: 'Search addresses',
                minSearchLength: 3,  // cause values disappeared in drop down
                searchTimeout: 200,  // cause values disappeared in drop down
                dropDownOptions: {
                  showTitle: false,
                  closeOnOutsideClick: true,
                },
                dataSource: Attendees.datagridUpdate.addressSource,
                onValueChanged: (e) => {
                  if (e.previousValue && e.previousValue !== e.value){
                    const selectedAddress = $('div.address-lookup-search').dxLookup('instance')._dataSource._items.find(x => x.id === e.value);
//                    Attendees.datagridUpdate.placePopupDxForm.option('formData.address', selectedAddress);
                    Attendees.datagridUpdate.placePopupDxForm.updateData('address', selectedAddress); // https://supportcenter.devexpress.com/ticket/details/t443361
//                    console.log("hi 847 here is Attendees.datagridUpdate.placePopupDxFormData", Attendees.datagridUpdate.placePopupDxFormData);
//                    console.log("hi 848 here is selectedAddress: ", selectedAddress);
                    // Attendees.datagridUpdate.placePopupDxForm.getEditor("address_extra").option('value', null);
                    // Attendees.datagridUpdate.placePopupDxForm.getEditor("address.street_number").option('value', selectedAddress.street_number);
                    // Attendees.datagridUpdate.placePopupDxForm.getEditor("address.route").option('value', selectedAddress.route);
                  }
                },
              },
            },
            {
              itemType: "group",
              visible: false,
              name: 'NewAddressItems',
              colSpan: 12,
              colCount: 12,
              items: [
                {
                  colSpan: 4,
                  dataField: "address.street_number",
                  helpText: 'no road name please',
                  label: {
                    text: 'Door number',
                  },
                  editorOptions: {
                    placeholder: "example: '22416'",
                  },
                },
                {
                  colSpan: 4,
                  dataField: "address.route",
                  helpText: 'no door number please',
                  label: {
                    text: 'Road',
                  },
                  editorOptions: {
                    placeholder: "example: 'A street'",
                  },
                },
                {
                  colSpan: 4,
                  dataField: "address_extra",
                  helpText: 'suite/floor number, etc',
                  label: {
                    text: 'Extra: unit/apt',
                  },
                  editorOptions: {
                    placeholder: "example: Apt 2G",
                  },
                },
                {
                  colSpan: 4,
                  dataField: "address.city",
                  name: "locality",
                  helpText: 'Village/Town name',
                  label: {
                    text: 'City',
                  },
                  editorOptions: {
                    placeholder: "example: 'San Francisco'",
                  },
                },
                {
                  colSpan: 4,
                  dataField: "address.postal_code",
                  helpText: 'ZIP code',
                  editorOptions: {
                    placeholder: "example: '94106'",
                  },
                },
                {
                  colSpan: 4,
                  dataField: "address.state_id",
    //              name: "existingAddressSelector",
                  label: {
                    text: 'State',
                  },
                  editorType: "dxLookup",
                  editorOptions: {
                    elementAttr: {
                      class: 'state-lookup-search',  // calling closing by the parent
                    },
                    valueExpr: "id",
                    displayExpr: (item) => {
                      return item ? item.name + ", " + item.country_name : null;
                    },
                    placeholder: "Example: 'CA'",
                    searchExpr: ['name'],
    //                searchMode: 'startswith',
                    searchPlaceholder: 'Search states',
                    minSearchLength: 2,  // cause values disappeared in drop down
                    searchTimeout: 200,  // cause values disappeared in drop down
                    dropDownOptions: {
                      showTitle: false,
                      closeOnOutsideClick: true,
                    },
                    dataSource: Attendees.datagridUpdate.stateSource,
                    onValueChanged: (e) => {
                      if (e.previousValue && e.previousValue !== e.value){
                        const selectedState = $('div.state-lookup-search').dxLookup('instance')._dataSource._items.find(x => x.id === e.value);
                        console.log("hi 946 here is selectedState: ", selectedState);
                      }
                    },
                  },
                },
              ],
            },
            {
              colSpan: 3,
              itemType: "button",
              horizontalAlignment: "left",
              buttonOptions: {
                elementAttr: {
                  class: 'attendee-form-submits',    // for toggling editing mode
                },
                disabled: !Attendees.utilities.editingEnabled,
                text: "Save Place",
                icon: "save",
                hint: "save Place data in the popup",
                type: "default",
                useSubmitBehavior: false,
                onClick: (clickEvent) => {
                  if(confirm('are you sure to submit the popup Place Form?')){
                    const userData = Attendees.datagridUpdate.placePopupDxForm.option('formData');
                    if(!Attendees.datagridUpdate.addressId){  // no address id means user creating new address
                      const newStreetNumber = Attendees.datagridUpdate.placePopupDxForm.getEditor("address.street_number").option('value');
                      const newRoute = Attendees.datagridUpdate.placePopupDxForm.getEditor("address.route").option('value');
                      const newAddressExtra = Attendees.datagridUpdate.placePopupDxForm.getEditor("address_extra").option('value');
                      const newCity = Attendees.datagridUpdate.placePopupDxForm.getEditor("address.city").option('value');
                      const newZIP = Attendees.datagridUpdate.placePopupDxForm.getEditor("address.postal_code").option('value');
                      const newStateAttrs = Attendees.datagridUpdate.placePopupDxForm.getEditor("address.state_id")._options;

                      userData.address = {
                        raw: 'new',
                        new_address: {  // special object for creating new django-address instance
                          raw: newStreetNumber + ' ' + newRoute + (newAddressExtra ? ', ' + newAddressExtra : '') + ', ' + newCity + ', ' + newStateAttrs.text + ' ' + newZIP,
                          street_number: newStreetNumber,
                          route: newRoute,
                          locality: newCity,
                          post_code: newZIP,
                          state: newStateAttrs.selectedItem.name,
                          state_code: newStateAttrs.selectedItem.code,
                          country: newStateAttrs.selectedItem.country_name,
                          country_code: newStateAttrs.selectedItem.country_code,
                        },
                      }
                    }
                    userData._method = userData.id ? 'PUT' : 'POST';

                    $.ajax({
                      url    : ajaxUrl,
                      data   : JSON.stringify(userData),
                      dataType:'json',
                      contentType: "application/json; charset=utf-8",
                      method : 'POST',
                      success: (savedPlace) => {
                                 const clickedButton = $('button.attendee-place-button[value="' + savedPlace.id + '"]');
                                 if (clickedButton.length) { clickedButton.text(savedPlace.display_name + ': ' + savedPlace.address.raw)}
                                 Attendees.datagridUpdate.placePopup.hide();
                                 DevExpress.ui.notify(
                                   {
                                     message: 'saving place success',
                                     width: 500,
                                     position: {
                                      my: 'center',
                                      at: 'center',
                                      of: window,
                                     }
                                    }, "success", 2500);
                      },
                      error  : (response) => {
                                 console.log('1017 Failed to save data for place Form in Popup, error: ', response);
                                 console.log('formData: ', userData);
                                 DevExpress.ui.notify(
                                   {
                                     message: 'saving locate error',
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
                },
              },
            },
            {
              colSpan: 3,
              itemType: "button",
              name: "editAddressButton",
              visible: true,
              horizontalAlignment: "left",
              buttonOptions: {
                elementAttr: {
                  class: 'attendee-form-submits',    // for toggling editing mode
                },
                disabled: !Attendees.utilities.editingEnabled,
                text: "Edit the address",
                icon: "edit",
                hint: "Modifying the current address, without creating one",
                type: "success",
                useSubmitBehavior: false,
                onClick: (clickEvent) => {
                  if(confirm("Are you sure to edit the current address?")){
                    Attendees.datagridUpdate.placePopupDxForm.itemOption('NewAddressItems', 'visible', true);
                    Attendees.datagridUpdate.placePopupDxForm.getEditor("address.id").option('visible', false);
                    Attendees.datagridUpdate.placePopupDxForm.getEditor("address.id").option('disable', true);
                    Attendees.datagridUpdate.placePopupDxForm.getEditor("editAddressButton").option('visible', false);
                    Attendees.datagridUpdate.placePopupDxForm.getEditor("newAddressButton").option('visible', false);
                  }
                },
              },
            },
            {
              colSpan: 3,
              itemType: "button",
              name: "newAddressButton",
              visible: true,
              horizontalAlignment: "left",
              buttonOptions: {
                elementAttr: {
                  class: 'attendee-form-submits',    // for toggling editing mode
                },
                disabled: !Attendees.utilities.editingEnabled,
                text: "Add new address",
                icon: "home",
                hint: "Can't find exiting address, add a new one here",
                type: "normal",
                useSubmitBehavior: false,
                onClick: (clickEvent) => {
                  if(confirm("Are you sure to add new address?")){
                    Attendees.datagridUpdate.placePopupDxForm.itemOption('NewAddressItems', 'visible', true);
                    Attendees.datagridUpdate.placePopupDxForm.getEditor("address.id").option('visible', false);
                    Attendees.datagridUpdate.placePopupDxForm.getEditor("address.id").option('disable', true);
                    Attendees.datagridUpdate.placePopupDxForm.getEditor("newAddressButton").option('visible', false);
                    Attendees.datagridUpdate.placePopupDxForm.getEditor("editAddressButton").option('visible', false);
                    Attendees.datagridUpdate.placePopup.option('title', 'Creating Address');
                    Attendees.datagridUpdate.addressId = null;
                  }
                },
              },
            },
            {
              colSpan: 3,
              itemType: "button",
              name: "setFamilyAddressButton",
              visible: true,
              horizontalAlignment: "left",
              buttonOptions: {
                elementAttr: {
                  class: 'attendee-form-submits',    // for toggling editing mode
                },
                disabled: !Attendees.utilities.editingEnabled,
                text: "Address to Family",
                icon: "group",
                hint: "Assign the address to attendee's first family",
                type: "danger",
                useSubmitBehavior: false,
                onClick: (clickEvent) => {
                  if(confirm("Are you sure to set the current address to the attendee's first family?")){
                    console.log("Hi 1135 Todo 20210515: Please implement this function")
                  }
                },
              },
            },
          ],
        }).dxForm("instance");
        e.append(formContainer);
      },
    };
  },

  fetchLocateFormData: (locateButton) => {
    if (locateButton.value){
      const fetchedPlace = Attendees.datagridUpdate.attendeeFormConfigs.formData.places.find(x => x.id == locateButton.value); // button value is string
      if (!Attendees.utilities.editingEnabled && fetchedPlace) {
        Attendees.datagridUpdate.placePopupDxFormData = fetchedPlace;
        Attendees.datagridUpdate.placePopupDxForm.option('formData', fetchedPlace);
        Attendees.datagridUpdate.addressId = fetchedPlace.address.id;
      }else{
        $.ajax({
          url    : $('form#place-update-popup-form').attr('action') + locateButton.value + '/',
          success: (response) => {
                     Attendees.datagridUpdate.placePopupDxFormData = response.data[0];
                     Attendees.datagridUpdate.placePopupDxForm.option('formData', response.data[0]);
                     Attendees.datagridUpdate.placePopupDxForm.option('onFieldDataChanged', (e) => {e.component.validate()});
                     Attendees.datagridUpdate.addressId = Attendees.datagridUpdate.placePopupDxFormData.address.id;
                   },
          error  : (response) => console.log('Failed to fetch data for Locate Form in Popup, error: ', response),
        });
      }
    }
  },

  addressSource: new DevExpress.data.CustomStore({
    key: 'id',
    load: (loadOptions) => {
      if (!Attendees.utilities.editingEnabled) return [Attendees.datagridUpdate.placePopupDxFormData.address];

      const deferred = $.Deferred();
      const args = {};

      [
          "skip",
          "take",
          "sort",
          "filter",
          "searchExpr",
          "searchOperation",
          "searchValue",
          "group",
      ].forEach((i) => {
          if (i in loadOptions && Attendees.utilities.isNotEmpty(loadOptions[i]))
              args[i] = loadOptions[i];
      });

      $.ajax({
        url: $('div.datagrid-attendee-update').data('addresses-endpoint'),
        dataType: "json",
        data: args,
        success: (result) => {
          deferred.resolve(result.data.concat([Attendees.datagridUpdate.placePopupDxFormData.place]), {
            totalCount: result.totalCount,
            summary:    result.summary,
            groupCount: result.groupCount
          });
        },
        error: (response) => {
          console.log('hi 1126 ajax error here is response: ', response);
          deferred.reject("Data Loading Error, probably time out?");
        },
        timeout: 7000,
      });

      return deferred.promise();
    },
    byKey: (key) => {
      if (!Attendees.utilities.editingEnabled && Attendees.datagridUpdate.placePopupDxFormData){
        return [Attendees.datagridUpdate.placePopupDxFormData.address];
      }else{
        const d = new $.Deferred();
        $.get($('div.datagrid-attendee-update').data('addresses-endpoint'), {id: key})
            .done(function(result) {
                d.resolve(result.data);
            });
        return d.promise();
      }
    },
  }),

  stateSource: new DevExpress.data.CustomStore({
    key: 'id',
    load: (loadOptions) => {
//      if (!Attendees.utilities.editingEnabled) return [Attendees.datagridUpdate.placePopupDxFormData.address];

      const deferred = $.Deferred();
      const args = {};

      [
          "skip",
          "take",
          "sort",
          "filter",
          "searchExpr",
          "searchOperation",
          "searchValue",
          "group",
      ].forEach((i) => {
          if (i in loadOptions && Attendees.utilities.isNotEmpty(loadOptions[i]))
              args[i] = loadOptions[i];
      });

      $.ajax({
        url: $('div.datagrid-attendee-update').data('states-endpoint'),
        dataType: "json",
        data: args,
        success: (result) => {
          deferred.resolve(result.data, {
            totalCount: result.totalCount,
            summary:    result.summary,
            groupCount: result.groupCount
          });
        },
        error: (response) => {
          console.log('hi 1182 ajax error here is response: ', response);
          deferred.reject("Data Loading Error, probably time out?");
        },
        timeout: 7000,
      });

      return deferred.promise();
    },
    byKey: (key) => {
//      if (!Attendees.utilities.editingEnabled && Attendees.datagridUpdate.placePopupDxFormData){
//        return [Attendees.datagridUpdate.placePopupDxFormData.address];
//      }else{
        const d = new $.Deferred();
//        console.log("hi 1195 here is state key: ", key);
        $.get($('div.datagrid-attendee-update').data('states-endpoint'), {id: key})
            .done(function(result) {
                d.resolve(result.data);
            });
        return d.promise();
//      }
    },
  }),


  ///////////////////////  Family Attendees Datagrid in main DxForm  ///////////////////////


  initFamilyAttendeeDatagrid: (data, itemElement) => {
    console.log("hi 1299 here is data.editorOptions.value: ", data.editorOptions.value);
    // Attendees.datagridUpdate.familyAttendeeDatagridConfig['dataSource'] = Attendees.datagridUpdate.familyAttendeeDatagridDataSource;
    const $myDatagrid = $("<div id='family-attendee-datagrid-container'>").dxDataGrid(Attendees.datagridUpdate.familyAttendeeDatagridConfig);
    itemElement.append($myDatagrid);
    const mydatagrid = $myDatagrid.dxDataGrid("instance");
    mydatagrid.beginUpdate();
    mydatagrid.option("dataSource", document.querySelector('div.datagrid-attendee-update').dataset.familyAttendeesEndpoint);
    mydatagrid.endUpdate();
  },

  familyAttendeeDatagridConfig: {
    dataSource: null,
    allowColumnReordering: true,
    columnAutoWidth: true,
    allowColumnResizing: true,
    columnResizingMode: 'nextColumn',
    rowAlternationEnabled: true,
    hoverStateEnabled: true,
    loadPanel: {
      message: 'Fetching...',
      enabled: true,
    },
    wordWrapEnabled: false,
    grouping: {
      autoExpandAll: true,
    },
    // groupPanel: {
    //   visible: "auto",
    // },
    // columnChooser: {
    //   enabled: true,
    //   mode: "select",
    // },
    // remoteOperations: true,
    columns:[

      // {
      //   dataField: "gathering",
      //   groupIndex: 0,
      //   lookup: {
      //     valueExpr: "id",
      //     displayExpr: "gathering_label",
      //     dataSource: {
      //       store: new DevExpress.data.CustomStore({
      //         key: "id",
      //         load: () => {
      //           const $selectedMeets = $('select.filter-meets').val();
      //           if ($selectedMeets.length > 0) {
      //             return $.getJSON($('div.attendances').data('gatherings-endpoint'), {meets: $selectedMeets});
      //           }
      //         },
      //       }),
      //     },
      //   }
      // },

//
      {
        dataField: "family.id",
        caption: 'Family',
        groupIndex: 0,
        lookup: {
          valueExpr: "id",
          displayExpr: "display_name",
          dataSource: {
            store: new DevExpress.data.CustomStore({
              key: "id",
              load: () => {
                return $.getJSON($('div.datagrid-attendee-update').data('attendee-families-endpoint'));
              },
            }),
          },
        },
      },
      {
        dataField: "role",
        caption: 'Role',
        lookup: {
          valueExpr: "id",
          displayExpr: "title",
          dataSource: {
            store: new DevExpress.data.CustomStore({
              key: "id",
              load: () => {
                return $.getJSON($('div.datagrid-attendee-update').data('relations-endpoint'));
              },
            }),
          },
        },
      },
      {
        dataField: "attendee.gender",
        caption: 'Gender',
        lookup: {
          valueExpr: "name",
          displayExpr: "name",
          dataSource: Attendees.utilities.genderEnums(),
        }
      },
      {
        caption: 'First name',
        dataField: "attendee.first_name",
      },
      {
        caption: 'Last name',
        dataField: "attendee.last_name",
      },
      {
        caption: 'Last name2',
        dataField: "attendee.last_name2",
      },
      {
        caption: 'First name2',
        dataField: "attendee.first_name2",
      },
      {
        dataField: "attendee.division",
        caption: 'Division',
        lookup: {
          valueExpr: "id",
          displayExpr: "display_name",
          dataSource: {
            store: new DevExpress.data.CustomStore({
              key: "id",
              load: () => {
                return $.getJSON($('div.datagrid-attendee-update').data('divisions-endpoint'));
              },
            }),
          },
        }
      },
      {
        dataField: "start",
      },
      {
        dataField: "finish",
      },
    ],
  },

  // familyAttendeeDatagridDataSource: new DevExpress.data.CustomStore({
  //   key: "id",
  //   load: (loadOptions) => {
  //     const deferred = $.Deferred();
  //     const args = {};
  //
  //     [
  //       "skip",
  //       "take",
  //       "requireTotalCount",
  //       "requireGroupCount",
  //       "sort",
  //       "filter",
  //       "totalSummary",
  //       "group",
  //       "groupSummary"
  //     ].forEach((i) => {
  //       if (i in loadOptions && Attendees.utilities.isNotEmpty(loadOptions[i]))
  //         args[i] = JSON.stringify(loadOptions[i]);
  //     });
  //
  //     $.ajax({
  //       url: document.querySelector('div.datagrid-attendee-update').dataset.familyAttendeesEndpoint,
  //       dataType: "json",
  //       data: args,
  //       success: (result) => {
  //         deferred.resolve(result.data, {
  //           totalCount: result.totalCount,
  //           summary:    result.summary,
  //           groupCount: result.groupCount
  //         });
  //       },
  //       error: () => {
  //         deferred.reject("Data Loading Error, probably time out?");
  //       },
  //       timeout: 30000,
  //     });
  //
  //     return deferred.promise();
  //   }
  // }),


  ///////////////////////  Family Attributes Popup and DxForm  ///////////////////////

  initFamilyAttrPopupDxForm: (event) => {
    const familyAttrButton = event.target;
    Attendees.datagridUpdate.familyAttrPopup = $('div.popup-family-attr-update').dxPopup(Attendees.datagridUpdate.familyAttrPopupDxFormConfig(familyAttrButton)).dxPopup('instance');
    Attendees.datagridUpdate.fetchFamilyAttrFormData(familyAttrButton);
  },

  familyAttrPopupDxFormConfig: (familyAttrButton) => {
    const ajaxUrl=$('form#family-attr-update-popup-form').attr('action') + familyAttrButton.value + '/';
    console.log("hi 1327 here is ajaxUrl: ", ajaxUrl);
    return {
      visible: true,
      title: familyAttrButton.value ? 'Viewing Family' : 'Creating Family',
      minwidth: "20%",
      minheight: "30%",
      position: {
        my: 'center',
        at: 'center',
        of: window,
      },
      // onHiding: () => {
      // },
      dragEnabled: true,
      // contentTemplate: (e) => {
      // },
    };
  },

  fetchFamilyAttrFormData: (familyAttrButton) => {
    console.log("hi 1347 here is familyAttrButton: ", familyAttrButton);
  },
};

$(document).ready(() => {
  Attendees.datagridUpdate.init();
});
