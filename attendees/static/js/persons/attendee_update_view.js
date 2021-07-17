Attendees.datagridUpdate = {
  attendeeMainDxForm: null,  // will be assigned later, may not needed if use native form.submit()?
  attendeeMainDxFormDefault: {
    infos: {
      names: {},
      contacts: {}
    }
  },
  attendeeAttrs: null,  // will be assigned later
  attendeeId: '',  // the attendee is being edited, since it maybe admin/parent editing another attendee
  attendeeAjaxUrl: null,
  attendeePhotoFileUploader: null,
  relationshipDatagrid: null,
  attendingMeetDatagrid: null,
  attendingPopupDxForm: null,  // for getting formData
  attendingPopupDxFormData: {},  // for storing formData
  // attendingPopupDxFormCharacterSelect: null,
  attendingPopup: null,  // for show/hide popup
  attendingsData: {},
  attendingDefaults: {
    category: 'primary',
  },
  attendingmeetDefaults: {
    // assembly: parseInt(document.querySelector('div.datagrid-attendee-update').dataset.currentAssemblyId),
    category: 'primary',
    start: new Date().toISOString(),
    finish: new Date(new Date().setFullYear(new Date().getFullYear() + 1)).toISOString(), // 1 years from now
  },
  // addressId: '', // for sending address data by AJAX
  placePopup: null, // for show/hide popup
  placePopupDxForm: null,  // for getting formData
  placePopupDxFormData: {},  // for storing formData
  placeDefaults: {
    address: {
      type: 'street',
    },
    display_order: 0,
    display_name: 'main',
    // content_type: parseInt(document.querySelector('div.datagrid-attendee-update').dataset.attendeeContenttypeId),
  },
  familyAttendeeDatagrid: null,
  familyAttrPopupDxForm: null,
  familyAttrPopupDxFormData: {},
  familyAttrPopup: null,
  familyAttrDefaults: {
    display_order: 0,
    attendees: [document.querySelector('input[name="attendee-id"]').value],
    division: 0,       // will be assigned later
    display_name: '',  // will be assigned later
  },

  init: () => {
    console.log('/static/js/persons/attendee_update_view.js');
    Attendees.datagridUpdate.displayNotifierFromSearchParam('success');
    Attendees.datagridUpdate.initAttendeeForm();
  },

  initListeners: () => {
    $("div.nav-buttons").on('click', 'input#custom-control-edit-checkbox', e => Attendees.datagridUpdate.toggleEditing(Attendees.utilities.toggleEditingAndReturnStatus(e)));
    $("div.form-container").on('click', 'button.attending-button', e => Attendees.datagridUpdate.initAttendingPopupDxForm(e));
    $("div.form-container").on('click', 'button.place-button', e => Attendees.datagridUpdate.initPlacePopupDxForm(e));
    $("div.form-container").on('click', 'button.family-button', e => Attendees.datagridUpdate.initFamilyAttrPopupDxForm(e));
    Attendees.datagridUpdate.attachContactAddButton();
    // add listeners for Family, counselling, etc.
  },

  toggleEditing: (enabled) => {
    $('div.attendee-form-submits').dxButton('instance').option('disabled', !enabled);
    $('div.attendee-form-delete').dxButton('instance').option('disabled', !enabled);
    $('span.attendee-form-submits').dxButton('instance').option('disabled', !enabled);
    $('button.attending-button-new, button.family-button-new, button.place-button-new, input.form-check-input').prop('disabled', !enabled);
    Attendees.datagridUpdate.attendeeMainDxForm.option('readOnly', !enabled);
    Attendees.datagridUpdate.attendeePhotoFileUploader.option('disabled', !enabled);

    if (enabled) {
      Attendees.datagridUpdate.familyAttendeeDatagrid.clearGrouping();
      Attendees.datagridUpdate.familyAttendeeDatagrid.columnOption('attendee.infos.names.original', 'visible', false);
      Attendees.datagridUpdate.familyAttendeeDatagrid.columnOption('attendee.first_name', 'visible', true);
      Attendees.datagridUpdate.familyAttendeeDatagrid.columnOption('attendee.last_name', 'visible', true);
      Attendees.datagridUpdate.familyAttendeeDatagrid.columnOption('attendee.last_name2', 'visible', true);
      Attendees.datagridUpdate.familyAttendeeDatagrid.columnOption('attendee.first_name2', 'visible', true);

      Attendees.datagridUpdate.relationshipDatagrid && Attendees.datagridUpdate.relationshipDatagrid.clearGrouping();
    } else {
      Attendees.datagridUpdate.familyAttendeeDatagrid.columnOption('attendee.first_name', 'visible', false);
      Attendees.datagridUpdate.familyAttendeeDatagrid.columnOption('attendee.last_name', 'visible', false);
      Attendees.datagridUpdate.familyAttendeeDatagrid.columnOption('attendee.last_name2', 'visible', false);
      Attendees.datagridUpdate.familyAttendeeDatagrid.columnOption('attendee.first_name2', 'visible', false);
      Attendees.datagridUpdate.familyAttendeeDatagrid.columnOption('attendee.infos.names.original', 'visible', true);
      Attendees.datagridUpdate.familyAttendeeDatagrid.columnOption('family.id', 'groupIndex', 0);

      Attendees.datagridUpdate.relationshipDatagrid && Attendees.datagridUpdate.relationshipDatagrid.columnOption("in_family", "groupIndex", 0);
    }

    const cellEditingArgs = {
      mode: 'cell',
      allowUpdating: enabled,
      allowAdding: enabled,
      allowDeleting: enabled,
      texts: {
        confirmDeleteMessage: 'Are you sure to delete it? Instead, setting the "finish" date is usually enough!',
      },
    };
    Attendees.datagridUpdate.familyAttendeeDatagrid.option('editing', cellEditingArgs);
    Attendees.datagridUpdate.relationshipDatagrid && Attendees.datagridUpdate.relationshipDatagrid.option('editing', cellEditingArgs);
    Attendees.datagridUpdate.educationDatagrid && Attendees.datagridUpdate.educationDatagrid.option('editing', cellEditingArgs);
    Attendees.datagridUpdate.statusDatagrid && Attendees.datagridUpdate.statusDatagrid.option('editing', cellEditingArgs);
    Attendees.datagridUpdate.noteDatagrid && Attendees.datagridUpdate.noteDatagrid.option('editing', {...cellEditingArgs, ...Attendees.datagridUpdate.noteEditingArgs});
    Attendees.datagridUpdate.attendingMeetDatagrid && Attendees.datagridUpdate.attendingMeetDatagrid.option('editing', {...cellEditingArgs, ...Attendees.datagridUpdate.attendingMeetEditingArgs});
  },

  displayNotifierFromSearchParam: (successParamName) => {
    const successParamValue = Attendees.utilities.extractParamAndReplaceHistory(successParamName);
    if (successParamValue) {
      DevExpress.ui.notify(
        {
          message: successParamValue,
          width: 500,
          position: {
            my: 'center',
            at: 'center',
            of: window,
          },
        }, 'success', 2500);
    }
  },


  ///////////////////////  Main Attendee DxForm and Submit ///////////////////////


  initAttendeeForm: () => {
    Attendees.datagridUpdate.attendeeAttrs = document.querySelector('div.datagrid-attendee-update');
    Attendees.datagridUpdate.attendeeUrn = Attendees.datagridUpdate.attendeeAttrs.attendeeUrn;
    Attendees.datagridUpdate.attendeeId = document.querySelector('input[name="attendee-id"]').value;
    // Attendees.datagridUpdate.placeDefaults.object_id = Attendees.datagridUpdate.attendeeId;
    $.ajaxSetup({
      headers: {
        'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value,
        'X-Target-Attendee-Id': Attendees.datagridUpdate.attendeeId,
      }
    });

    if (Attendees.datagridUpdate.attendeeId === 'new') {
      Attendees.datagridUpdate.attendeeAjaxUrl = Attendees.datagridUpdate.attendeeAttrs.dataset.attendeeEndpoint;
      $('h3.page-title').text('New Attendee: more data can be entered after save');
      window.top.document.title = 'New Attendee';
      Attendees.utilities.editingEnabled = true;
      Attendees.datagridUpdate.attendeeFormConfigs = Attendees.datagridUpdate.getAttendeeFormConfigs();
      Attendees.datagridUpdate.attendeeMainDxForm = $("div.datagrid-attendee-update").dxForm(Attendees.datagridUpdate.attendeeFormConfigs).dxForm('instance');
      Attendees.datagridUpdate.attendeeFormConfigs.formData = Attendees.datagridUpdate.attendeeMainDxFormDefault;
      Attendees.datagridUpdate.populateBasicInfoBlock({});
    } else {
      Attendees.datagridUpdate.attendeeAjaxUrl = Attendees.datagridUpdate.attendeeAttrs.dataset.attendeeEndpoint + Attendees.datagridUpdate.attendeeId + '/';
      $.ajax({
        url: Attendees.datagridUpdate.attendeeAjaxUrl,
        success: (response) => {
          Attendees.datagridUpdate.attendeeFormConfigs = Attendees.datagridUpdate.getAttendeeFormConfigs();
          Attendees.datagridUpdate.attendeeFormConfigs.formData = response ? response : Attendees.datagridUpdate.attendeeMainDxFormDefault;
          $('h3.page-title').text('Details of ' + Attendees.datagridUpdate.attendeeFormConfigs.formData.infos.names.original);
          window.top.document.title = Attendees.datagridUpdate.attendeeFormConfigs.formData.infos.names.original;
          Attendees.datagridUpdate.attendeeMainDxForm = $("div.datagrid-attendee-update").dxForm(Attendees.datagridUpdate.attendeeFormConfigs).dxForm('instance');
          Attendees.datagridUpdate.populateBasicInfoBlock();
          Attendees.datagridUpdate.initListeners();
          Attendees.datagridUpdate.familyAttrDefaults.division = response.division;
          Attendees.datagridUpdate.familyAttrDefaults.display_name = response.infos.names.original + ' family';
        },
        error: (response) => {
          console.log('Failed to fetch data in Attendees.datagridUpdate.initAttendeeForm(), error: ', response);
        },
      });
    }
  },

  attachContactAddButton: () => {
    $('<span>', {class: 'extra-contacts float-right'})
      .dxButton({
        disabled: !Attendees.utilities.editingEnabled,
        elementAttr: {
          class: 'attendee-form-submits',  // for toggling editing mode
        },
        text: 'Add more contact',
        icon: 'email',  // or 'fas fa-comment-dots'
        stylingMode: 'outlined',
        type: 'success',
        height: '1.4rem',
        hint: 'add more different contacts such as more phones/emails',
        onClick: () => {
          Attendees.datagridUpdate.contactPopup = $('div.popup-more-contacts').dxPopup(Attendees.datagridUpdate.contactPopupDxFormConfig).dxPopup('instance');
        },
      }).appendTo($('span.dx-form-group-caption')[1]);  // basic info block is at index 1
  },

  getAttendeeFormConfigs: () => {  // this is the place to control blocks of AttendeeForm
    const basicItems = [
      {
        colSpan: 4,
        itemType: 'group',
        cssClass: 'h6',
        caption: 'Photo',
        items: [

          {
            dataField: 'photo',
            label: {
              location: 'top',
              text: ' ',  // empty space required for removing label
              showColon: false,
            },
            template: (data, itemElement) => {
              if (data.editorOptions && data.editorOptions.value) {
                const $img = $('<img>', {src: data.editorOptions.value, class: 'attendee-photo-img'});
                const $imgLink = $('<a>', {href: data.editorOptions.value, target: '_blank'});
                itemElement.append($imgLink.append($img));
                // Todo: add check/uncheck photo-clear feature, store img link in data attributes when marking deleted
                const $inputDiv = $('<div>', {
                  class: 'form-check',
                  title: "If checked, it'll be deleted when you save"
                });
                const $clearInput = $('<input>', {
                  id: 'photo-clear',
                  disabled: !Attendees.utilities.editingEnabled,
                  type: 'checkbox',
                  name: 'photo-clear',
                  class: 'form-check-input',
                  onclick: "return confirm('Are you sure?')"
                });
                const $clearInputLabel = $('<label>', {
                  for: 'photo-clear',
                  text: 'delete photo',
                  class: 'form-check-label'
                });
                $inputDiv.append($clearInput);
                $inputDiv.append($clearInputLabel);
                itemElement.append($inputDiv);
              } else {
                $('<img>', {
                  src: Attendees.datagridUpdate.attendeeAttrs.dataset.emptyImageLink,
                  class: 'attendee-photo-img'
                }).appendTo(itemElement);
              }
            },
          },
          {
            template: (data, itemElement) => {
              photoFileUploader = $("<div>").attr('id', 'dxfu1').dxFileUploader(
                {
                  name: 'photo',
                  disabled: !Attendees.utilities.editingEnabled,
                  selectButtonText: 'Select photo',
                  accept: 'image/*',
                  multiple: false,
                  uploadMode: 'useForm',
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
        colCount: 21,
        itemType: "group",
        name: 'basic-info-container',
        cssClass: 'h6',
        caption: 'Basic info. Fields after nick name can be removed by clearing & save.',  // adding element in caption by $("<span>", {text:"hi 5"}).appendTo($("span.dx-form-group-caption")[1])
        items: [],  // will populate later for dynamic contacts
      },
    ];

    const moreItems = [
      {
        colSpan: 24,
        colCount: 24,
        caption: 'Addresses',
        cssClass: 'h6',
        itemType: "group",
        items: [
          {
            colSpan: 24,
            name: 'places',
            label: {
              location: 'top',
              text: ' ',  // empty space required for removing label
              showColon: false,
            },
            template: (data, itemElement) => {
              const familyContentTypeId = document.querySelector('div.datagrid-attendee-update').dataset.familyContenttypeId;
              const $placeUl = $('<ul>', {class: 'list-group'});
              const newButtonAttrs = {
                text: 'Add new address+',
                disabled: !Attendees.utilities.editingEnabled,
                title: '+ Add the attendee to a new address',
                // type: 'button',
                class: 'place-button-new place-button btn-outline-primary btn button btn-sm ',
              };

              const $personalNewButton = Attendees.datagridUpdate.familyButtonFactory({
                ...newButtonAttrs,
                'data-desc': 'attendee address (' + Attendees.datagridUpdate.attendeeFormConfigs.formData.infos.names.original + ')',
                'data-content-type': parseInt(document.querySelector('div.datagrid-attendee-update').dataset.attendeeContenttypeId),
                'data-object-id': Attendees.datagridUpdate.attendeeId,
                'data-object-name': Attendees.datagridUpdate.attendeeFormConfigs.formData.infos.names.original,
              });
              const personalPlaces = Attendees.datagridUpdate.attendeeFormConfigs.formData.places || [];
              const familyattendees = Attendees.datagridUpdate.attendeeFormConfigs.formData.familyattendee_set || [];
              let $personalLi = $('<li>', {class: 'list-group-item', text: 'Personal'}).append($personalNewButton);

              personalPlaces.forEach(place => {
                const addressName = (place.street || '').replace(', USA', '');
                const $button = Attendees.datagridUpdate.familyButtonFactory({
                  // type: 'button',
                  'data-desc': 'attendee address (' + place.street + ')',
                  class: 'btn-outline-success place-button btn button btn-sm',
                  value: place.id,
                  text: (place.display_name && !addressName.includes(place.display_name) ? place.display_name + ': ' : '') + addressName,
                  'data-object-id': Attendees.datagridUpdate.attendeeId,
                  'data-object-name': Attendees.datagridUpdate.attendeeFormConfigs.formData.infos.names.original,
                });
                $personalLi = $personalLi.append($button);
              });
              let $places = $placeUl.append($personalLi);

              familyattendees.forEach(familyattendee => {
                const family = familyattendee.family;
                const $familyNewButton = Attendees.datagridUpdate.familyButtonFactory({
                  ...newButtonAttrs,
                  'data-desc': 'family address (' + family.display_name + ')',
                  'data-content-type': familyContentTypeId,
                  'data-object-id': family.id,
                  'data-object-name': family.display_name,
                });

                let $familyLi = $('<li>', {
                  class: 'list-group-item ' + family.id,
                  text: family.display_name,
                }).append($familyNewButton);

                familyattendee.family.places.forEach(place => {
                  const addressName = (place.street || '').replace(', USA', '');
                  const $button = Attendees.datagridUpdate.familyButtonFactory({
                    // type: 'button',
                    'data-desc': family.display_name + ' family address (' + place.street + ')',
                    class: 'btn-outline-success place-button btn button btn-sm',
                    value: place.id,
                    text: (place.display_name && !addressName.includes(place.display_name) ? place.display_name + ': ' : '') + addressName,
                    'data-object-id': family.id,
                    'data-object-name': family.display_name,
                  });
                  $familyLi = $familyLi.append($button);
                });
                $places = $places.append($familyLi);
              });
              itemElement.append($places);
            },
          },
        ],
      },
      {
        colSpan: 24,
        colCount: 24,
        caption: 'Families: Except current attendee, double click table cells to edit if editing mode is on. Click away or hit Enter to save',
        cssClass: 'h6',
        itemType: 'group',
        items: [
          {
            colSpan: 24,
            dataField: 'familyattendee_set',
            name: 'familyAttrs',
            label: {
              text: 'families',
            },
            template: (data, itemElement) => {
              Attendees.datagridUpdate.familyButtonFactory({
                text: 'New family for attendee+',
                disabled: !Attendees.utilities.editingEnabled,
                title: '+ Add the attendee to a new family',
                type: 'button',
                class: 'family-button-new family-button btn-outline-primary btn button btn-sm ',
              }).appendTo(itemElement);
              if (data.editorOptions && data.editorOptions.value) {
                data.editorOptions.value.forEach(familyAttendee => {
                  if (familyAttendee && typeof familyAttendee === 'object') {
                    Attendees.datagridUpdate.familyButtonFactory({value: familyAttendee.family.id, text: familyAttendee.family.display_name}).appendTo(itemElement);
                  }
                });
              }
            },
          },
          {
            colSpan: 24,
            dataField: 'familyattendee_set',
            name: 'familyAttendeeDatagrid',
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
        apiUrlName: 'api_attendee_relationships_view_set',
        colSpan: 24,
        colCount: 24,
        caption: 'Relationships & Access: double click table cells to edit if editing mode is on. Click away or hit Enter to save',
        cssClass: 'h6',
        itemType: "group",
        items: [
          {
            colSpan: 24,
            dataField: 'relationship_set',
            label: {
              location: 'top',
              text: ' ',  // empty space required for removing label
              showColon: false,
            },
            template: (data, itemElement) => Attendees.datagridUpdate.initRelationshipDatagrid(data, itemElement),
          }
        ],
      },
      {
        apiUrlName: 'api_categorized_pasts_view_set_education',
        colSpan: 24,
        colCount: 24,
        caption: "Education: double click table cells to edit if editing mode is on. Click away or hit Enter to save",
        cssClass: 'h6',
        itemType: 'group',
        items: [
          {
            colSpan: 24,
            dataField: "past_education_set",
            label: {
              location: 'top',
              text: ' ',  // empty space required for removing label
              showColon: false,
            },
            template: (data, itemElement) => {
              Attendees.datagridUpdate.educationDatagrid = Attendees.datagridUpdate.initPastDatagrid(data, itemElement, {
                type: 'education',
                dataFieldAndOpts: {
                  category: {},
                  display_name: {},
                  'infos.show_secret': {},
                  'infos.comment': {},
                  when: {caption: 'Start'},
                  finish: {},
                },
              });
            },
          }
        ],
      },
      {
        apiUrlName: 'api_categorized_pasts_view_set_status',
        colSpan: 24,
        colCount: 24,
        caption: 'Status: double click table cells to edit if editing mode is on. Click away or hit Enter to save',
        cssClass: 'h6',
        itemType: 'group',
        items: [
          {
            colSpan: 24,
            dataField: 'past_status_set',
            label: {
              location: 'top',
              text: ' ',  // empty space required for removing label
              showColon: false,
            },
            template: (data, itemElement) => {
              Attendees.datagridUpdate.statusDatagrid = Attendees.datagridUpdate.initPastDatagrid(data, itemElement, {
                type: 'status',
                dataFieldAndOpts: {
                  category: {},
                  display_name: {},
                  'infos.show_secret': {},
                  'infos.comment': {},
                  when: {},
                },
              });
            },
          }
        ],
      },
      {
        apiUrlName: 'api_categorized_pasts_view_set_note',
        colSpan: 24,
        colCount: 24,
        caption: 'Other notes',
        cssClass: 'h6',
        itemType: 'group',
        items: [
          {
            colSpan: 24,
            dataField: 'past_note_set',
            label: {
              location: 'top',
              text: ' ',  // empty space required for removing label
              showColon: false,
            },
            template: (data, itemElement) => {
              Attendees.datagridUpdate.noteDatagrid = Attendees.datagridUpdate.initPastDatagrid(data, itemElement, {
                type: 'note',
                dataFieldAndOpts: {
                  category: {},
                  display_name: {caption: 'Title'},
                  'infos.show_secret': {},
                  'infos.comment': {},
                  when: {},
                },
              });
            },
          }
        ],
      },
      {
        colSpan: 24,
        colCount: 24,
        caption: 'Usually joins: register groups by buttons, or click \'edit\' to join activities',
        cssClass: 'h6',
        itemType: 'group',
        items: [
          {
            colSpan: 24,
            dataField: 'attendingmeets',
            cssClass: 'attendings-buttons',
            label: {
              text: 'registrant/group',
            },
            template: (data, itemElement) => {
                  const attendings = data.editorOptions && data.editorOptions.value || [];
                  Attendees.datagridUpdate.attendingsData = attendings.reduce((sum, now) => {
                    if (now.attending_is_removed) {
                      return {...sum}
                    }else {
                      return {
                        ...sum,
                        [now.attending_id]: now,
                      };
                    }
                  }, {});
                  Attendees.datagridUpdate.populateAttendingButtons(Object.values(Attendees.datagridUpdate.attendingsData), itemElement);
            },
          },
          {
            colSpan: 24,
            dataField: 'attendingmeets_set',
            label: {
              location: 'top',
              text: ' ',  // empty space required for removing label
              showColon: false,
            },
            template: (data, itemElement) => Attendees.datagridUpdate.initAttendingMeetsDatagrid(data, itemElement),
          },
        ],
      },
    ];

    const buttonItems = [
      {
        itemType: 'button',
        name: 'mainAttendeeFormSubmit',
        horizontalAlignment: 'left',
        buttonOptions: {
          elementAttr: {
            class: 'attendee-form-submits',  // for toggling editing mode
          },
          disabled: !Attendees.utilities.editingEnabled,
          text: 'Save Attendee details and photo',
          icon: 'save',
          hint: 'save attendee data in the page',
          type: 'default',
          useSubmitBehavior: true,
          onClick: (e) => {
            if (Attendees.datagridUpdate.attendeeMainDxForm.validate().isValid && confirm('Are you sure?')) {

              const userData = new FormData($('form#attendee-update-form')[0]);
              if (!$('input[name="photo"]')[0].value) {
                userData.delete('photo')
              }
              const userInfos = Attendees.datagridUpdate.attendeeFormConfigs.formData.infos;
              userInfos['contacts'] = Attendees.utilities.trimBothKeyAndValueButKeepBasicContacts(userInfos.contacts);  // remove emptied contacts
              userData.set('infos', JSON.stringify(userInfos));

              $.ajax({
                url: Attendees.datagridUpdate.attendeeAjaxUrl,
                contentType: false,
                processData: false,
                dataType: 'json',
                data: userData,
                method: Attendees.datagridUpdate.attendeeId && Attendees.datagridUpdate.attendeeId !== 'new' ? 'PUT' : 'POST',
                success: (response) => {  // Todo: update photo link, temporarily reload to bypass the requirement
                  const parser = new URL(window.location);
                  parser.searchParams.set('success', 'Saving attendee success');

                  if (parser.href.split('/').pop().startsWith('new')){
                    const newAttendeeIdUrl = '/' + response.id;
                    window.location = parser.href.replace('/new', newAttendeeIdUrl);
                  }else {
                    window.location = parser.href;
                  }
                },
                error: (response) => {
                  console.log('Failed to save data for main AttendeeForm, error: ', response);
                  console.log('formData: ', [...userData]);
                  DevExpress.ui.notify(
                    {
                      message: 'saving attendee error',
                      width: 500,
                      position: {
                        my: 'center',
                        at: 'center',
                        of: window,
                      },
                    }, 'error', 5000);
                },
              });
            }
          }
        },
      },
      {
        itemType: 'button',
        name: 'mainAttendeeFormDelete',
        horizontalAlignment: 'left',
        buttonOptions: {
          elementAttr: {
            class: 'attendee-form-delete',  // for toggling editing mode
          },
          disabled: !Attendees.utilities.editingEnabled,
          text: "Delete all of Attendee's data",
          icon: 'trash',
          hint: "delete attendee's all data in the page",
          type: 'danger',
          onClick: (e) => {
            if (confirm('Are you sure to delete all data of the attendee? Everything of the attendee will be removed.  Instead, seetting finish/deathday is usually enough!')) {
              window.scrollTo(0,0);
              $('div.spinner-border').show();
              $.ajax({
                url: Attendees.datagridUpdate.attendeeAjaxUrl,
                method: 'DELETE',
                success: (response) => {
                  $('div.spinner-border').hide();
                  DevExpress.ui.notify(
                    {
                      message: 'delete attendee success',
                      width: 500,
                      position: {
                        my: 'center',
                        at: 'center',
                        of: window,
                      },
                    }, 'info', 2500);
                  window.location = new URL(window.location.origin);
                },
                error: (response) => {
                  console.log('Failed to delete data for main AttendeeForm, error: ', response);
                  DevExpress.ui.notify(
                    {
                      message: 'saving attendee error',
                      width: 500,
                      position: {
                        my: 'center',
                        at: 'center',
                        of: window,
                      },
                    }, 'error', 5000);
                },
              });
            }
          }
        },
      },
    ];

    const originalItems = [...basicItems, ...(Attendees.datagridUpdate.attendeeId === 'new' ? [] : moreItems ), ...buttonItems];

    return {
      showValidationSummary: true,
      readOnly: !Attendees.utilities.editingEnabled,
      onContentReady: () => {
        $('div.spinner-border').hide();
        Attendees.utilities.toggleDxFormGroups();
      },
      onFieldDataChanged: (e) => {
        Attendees.datagridUpdate.attendeeMainDxForm.validate();
      },
      colCount: 24,
      formData: null, // will be fetched
      items: originalItems.filter(item => {
        return item.apiUrlName ? item.apiUrlName in Attendees.utilities.userApiAllowedUrlNames : true;
      }),
    };
  },

  attendeeNameValidator: () => {
    const attendeeFromData = Attendees.datagridUpdate.attendeeMainDxForm.option('formData');
    return attendeeFromData.first_name || attendeeFromData.last_name || attendeeFromData.first_name2 || attendeeFromData.last_name2;
  },

  familyButtonFactory: (attrs) => {
    return $('<button>', {
      type: 'button',
      class: 'btn-outline-success family-button btn button btn-sm ',
      ...attrs
    });
  },

  populateAttendingButtons: (attendings, itemElement) => {
    itemElement.empty();

    $('<button>').attr({
      disabled: !Attendees.utilities.editingEnabled,
      title: '+ Add a new attending',
      type: 'button',
      class: 'attending-button-new attending-button btn-outline-primary btn button btn-sm'
    }).text('+ Register group').appendTo(itemElement);

    attendings.forEach(attending => {
      if (attending && attending.attending_id) {
        let label, title;
        if (attending.attending_label){
          const originalLabel = (attending.attending_label).match(/\(([^)]+)\)/).pop();  // get substring between parentheses
          label = originalLabel.replace(Attendees.datagridUpdate.attendeeFormConfigs.formData.infos.names.original, 'Self');
          title = label;
        } else {
          const registrant_name = attending.registrant.replace(Attendees.datagridUpdate.attendeeFormConfigs.formData.infos.names.original, 'Self');
          label = attending.registration_assembly ? registrant_name + ' ' + attending.registration_assembly : registrant_name + ' Generic';
          title = attending.registrant;
        }
        $('<button>', {
          text: label,
          type: 'button',
          title: title,
          class: 'attending-button btn button btn-sm btn-outline-success',
          value: attending.attending_id,
        }).appendTo(itemElement);
      }
    });
  },

  populateBasicInfoBlock: (allContacts = Attendees.datagridUpdate.attendeeMainDxForm.option('formData').infos.contacts) => {
    const basicInfoItems = [
      {
        colSpan: 7,
        dataField: 'first_name',
        editorOptions: {
          placeholder: 'English',
        },
        validationRules: [
          {
            type: 'custom',
            reevaluate: true,
            validationCallback: Attendees.datagridUpdate.attendeeNameValidator,
            message: 'first or last name is required'
          },
          {
            type: 'stringLength',
            reevaluate: true,
            max: 25,
            message: 'No more than 25 characters'
          },
        ],
      },
      {
        colSpan: 7,
        dataField: 'last_name',
        editorOptions: {
          placeholder: 'English',
        },
        validationRules: [
          {
            type: 'custom',
            validationCallback: Attendees.datagridUpdate.attendeeNameValidator,
            message: 'first or last name is required'
          },
          {
            type: 'stringLength',
            max: 25,
            message: 'No more than 25 characters'
          },
        ],
      },
      {
        colSpan: 7,
        dataField: 'division',
        editorType: 'dxSelectBox',
        isRequired: true,
        label: {
          text: 'Major Division',
        },
        editorOptions: {
          valueExpr: 'id',
          displayExpr: 'display_name',
          placeholder: 'Select a value...',
          dataSource: new DevExpress.data.DataSource({
            store: new DevExpress.data.CustomStore({
              key: 'id',
              loadMode: 'raw',
              load: () => {
                const d = $.Deferred();
                $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.divisionsEndpoint).done((response) => {
                  d.resolve(response.data);
                });
                return d.promise();
              }
            })
          }),
        },
      },
      {
        colSpan: 7,
        dataField: 'last_name2',
        validationRules: [
          {
            type: 'custom',
            validationCallback: Attendees.datagridUpdate.attendeeNameValidator,
            message: 'first or last name is required'
          },
          {
            type: 'stringLength',
            max: 8,
            message: "No more than 8 characters"
          }
        ],
      },
      {
        colSpan: 7,
        dataField: 'first_name2',
        validationRules: [
          {
            type: 'custom',
            validationCallback: Attendees.datagridUpdate.attendeeNameValidator,
            message: 'first or last name is required'
          },
          {
            type: 'stringLength',
            max: 12,
            message: "No more than 12 characters"
          }
        ],
      },
      {
        colSpan: 7,
        dataField: 'gender',
        editorType: 'dxSelectBox',
        isRequired: true,
        editorOptions: {
          dataSource: Attendees.utilities.genderEnums(),
          valueExpr: 'name',
          displayExpr: 'name',
        },
        validationRules: [
          {
            type: 'required',
            message: 'gender is required'
          },
        ],
      },
      {
        colSpan: 7,
        dataField: 'actual_birthday',
        editorType: 'dxDateBox',
        label: {
          text: 'Real birthday',
        },
        editorOptions: {
          placeholder: 'click calendar',
          elementAttr: {
            title: 'month, day and year are all required',
          },
        },
      },
      {
        colSpan: 7,
        dataField: 'estimated_birthday',
        label: {
          text: 'Guess birthday',
        },
        editorType: 'dxDateBox',
        editorOptions: {
          placeholder: 'click calendar',
          elementAttr: {
            title: 'pick any day of your best guess year for the age estimation',
          },
        },
      },
      {
        colSpan: 7,
        dataField: 'deathday',
        editorType: 'dxDateBox',
        editorOptions: {
          placeholder: 'click calendar',
        },
      },
      {
        colSpan: 7,
        dataField: 'infos.contacts.phone1',
        label: {
          text: 'phone1',
        },
      },
      {
        colSpan: 7,
        dataField: 'infos.contacts.phone2',
        label: {
          text: 'phone2',
        },
      },
      {
        colSpan: 7,
        dataField: 'infos.names.nick',
        label: {
          text: 'nick name',
        },
      },
      {
        colSpan: 7,
        dataField: 'infos.contacts.email1',
        label: {
          text: 'email1',
        },
      },
      {
        colSpan: 7,
        dataField: 'infos.contacts.email2',
        label: {
          text: 'email2',
        },
      },
      {
        colSpan: 7,
        dataField: 'infos.fixed.food_pref',
        label: {
          text: 'Food pref',
        },
      },
    ];

    for (const contactKey in allContacts) {
      if (allContacts.hasOwnProperty(contactKey) && !(contactKey in Attendees.utilities.basicContacts)) {
        basicInfoItems.push({
          colSpan: 7,
          dataField: 'infos.contacts.' + contactKey,
          label: {
            text: contactKey,
          },
        });
      }
    }
    Attendees.datagridUpdate.attendeeMainDxForm.itemOption('basic-info-container', 'items', basicInfoItems);
  },

  contactPopupDxFormConfig: {
    maxWidth: '50%',
    maxHeight: '50%',
    visible: true,
    title: 'Add Contact',
    position: {
      my: 'center',
      at: 'center',
      of: window,
    },
    dragEnabled: true,
    contentTemplate: (e) => {
      const formContainer = $('<div class="contact-form">');
      Attendees.datagridUpdate.contactPopupDxForm = formContainer.dxForm({
        scrollingEnabled: true,
        showColonAfterLabel: false,
        requiredMark: '*',
        showValidationSummary: true,
        items: [
          {
            dataField: 'contactKey',
            editorOptions: {
              placeholder: 'for example: WeChat1',
            },
            helpText: 'Any contact such as email3/phone3/fax1, etc',
            label: {
              text: 'Contact method',
            },
            isRequired: true,
            validationRules: [
              {
                type: 'required',
                message: 'Contact method is required'
              },
              {
                type: 'stringLength',
                min: 2,
                message: 'Contact method can\'t be less than 2 characters'
              },
              {
                type: 'custom',
                message: 'That contact method exists already',
                validationCallback: (e) => {
                  const currentContacts = Attendees.datagridUpdate.attendeeMainDxForm.option('formData').infos.contacts;
                  return !Object.keys(currentContacts).includes(e.value.trim());
                }
              }
            ],
          },
          {
            dataField: 'contactValue',
            editorOptions: {
              placeholder: 'for example: WeiXin',
            },
            helpText: 'Contact such as name@email.com/+15101234567 etc',
            label: {
              text: 'Contact content',
            },
            isRequired: true,
            validationRules: [
              {
                type: 'required',
                message: 'Contact content is required'
              },
              {
                type: 'stringLength',
                min: 2,
                message: "Contact content can't be less than 2 characters"
              },
            ],
          },
          {
            itemType: 'button',
            horizontalAlignment: 'left',
            buttonOptions: {
              elementAttr: {
                class: 'attendee-form-submits',    // for toggling editing mode
              },
              disabled: !Attendees.utilities.editingEnabled,
              text: 'Save Custom Contact',
              icon: 'save',
              hint: 'save Custom Contact in the popup',
              type: 'default',
              useSubmitBehavior: false,
              onClick: (e) => {
                if (Attendees.datagridUpdate.contactPopupDxForm.validate().isValid) {
                  const currentInfos = Attendees.datagridUpdate.attendeeMainDxForm.option('formData').infos;
                  const newContact = Attendees.datagridUpdate.contactPopupDxForm.option('formData');
                  const trimmedNewContact = Attendees.utilities.trimBothKeyAndValueButKeepBasicContacts(newContact);
                  currentInfos.contacts = Attendees.utilities.trimBothKeyAndValueButKeepBasicContacts(currentInfos.contacts);  // remove emptied contacts
                  currentInfos.contacts[trimmedNewContact.contactKey] = trimmedNewContact.contactValue;

                  $.ajax({
                    url: Attendees.datagridUpdate.attendeeAjaxUrl,
                    data: JSON.stringify({infos: currentInfos}),
                    dataType: 'json',
                    contentType: 'application/json; charset=utf-8',
                    method: 'PATCH',
                    success: (response) => {
                      Attendees.datagridUpdate.contactPopupDxForm.resetValues();
                      Attendees.datagridUpdate.populateBasicInfoBlock(response.infos.contacts);
                      Attendees.datagridUpdate.contactPopup.hide();
                      DevExpress.ui.notify(
                        {
                          message: "saving custom contact success",
                          width: 500,
                          position: {
                            my: 'center',
                            at: 'center',
                            of: window,
                          },
                        }, 'success', 2500);
                    },
                    error: (response) => {
                      console.log('Failed to save data for custom contact in Popup, response and infos data: ', response, Attendees.datagridUpdate.attendeeMainDxForm.option('formData').infos);
                      Attendees.datagridUpdate.contactPopup.hide();
                      DevExpress.ui.notify(
                        {
                          message: 'saving custom contact error',
                          width: 500,
                          position: {
                            my: 'center',
                            at: 'center',
                            of: window,
                          },
                        }, 'error', 5000);
                    },
                  });
                }
              },
            },
          },
        ],
      }).dxForm('instance');
      e.append(formContainer);
    },
  },


  ///////////////////////  Attending Popup and DxForm  ///////////////////////


  initAttendingPopupDxForm: (event) => {
    const attendingButton = event.target;
    Attendees.datagridUpdate.attendingPopup = $("div.popup-attending-update").dxPopup(Attendees.datagridUpdate.attendingPopupDxFormConfig(attendingButton)).dxPopup('instance');
    Attendees.datagridUpdate.fetchAttendingFormData(attendingButton);
  },

  fetchAttendingFormData: (attendingButton) => {
    if (attendingButton.value) {
      $.ajax({
        url: $('form#attending-update-popup-form').attr('action') + attendingButton.value + '/',
        success: (response) => {
          Attendees.datagridUpdate.attendingPopupDxFormData = response;
          Attendees.datagridUpdate.attendingPopupDxForm.option('formData', response);
          // Attendees.datagridUpdate.attendingPopupDxForm.option('onFieldDataChanged', (e) => e.component.validate());
        },
        error: (response) => console.log('Failed to fetch data for AttendingForm in Popup, error: ', response),
      });
    }
  },

  attendingPopupDxFormConfig: (attendingButton) => {
    const ajaxUrl = $('form#attending-update-popup-form').attr('action') + (attendingButton.value ? attendingButton.value + '/' : '');
    return {
      visible: true,
      title: attendingButton.value ? 'Viewing attending' : 'Creating attending',
      minwidth: '20%',
      minheight: '30%',
      position: {
        my: 'center',
        at: 'center',
        of: window,
      },
      onHiding: () => {
        const $existingAttendeeSelector = $('div.attendee-lookup-search').dxLookup('instance');
        if ($existingAttendeeSelector) $existingAttendeeSelector.close();
      },
      dragEnabled: true,
      contentTemplate: (e) => {
        const formContainer = $('<div class="attendingForm">');
        Attendees.datagridUpdate.attendingPopupDxForm = formContainer.dxForm({
          readOnly: !Attendees.utilities.editingEnabled,
          formData: Attendees.datagridUpdate.attendingDefaults,
          colCount: 3,
          scrollingEnabled: true,
          showColonAfterLabel: false,
          requiredMark: '*',
          labelLocation: 'top',
          minColWidth: '20%',
          showValidationSummary: true,
          items: [
            {
              dataField: 'registration.assembly',
              editorType: 'dxSelectBox',
              validationRules: [
                {
                  type: 'async',
                  message: 'Same Group/Registrant exists, please select other assembly or close the popup to find that registration',
                  validationCallback: (params) =>  Attendees.datagridUpdate.validateRegistration(params.value),
                },
              ],
              helpText: 'Same Group/Registrant can only register once',
              label: {
                text: 'Belonging Group (Assembly)',
                showColon: true,
              },
              editorOptions: {
                valueExpr: 'id',
                displayExpr: 'division_assembly_name',
                placeholder: 'Select a value...',
                showClearButton: true,
                dataSource: new DevExpress.data.DataSource({
                  store: new DevExpress.data.CustomStore({
                    key: 'id',
                    loadMode: 'raw',
                    load: () => {
                      const d = $.Deferred();
                      $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.assembliesEndpoint).done((response) => {
                        d.resolve(response.data);
                      });
                      return d.promise();
                    },
                  })
                }),
              },
            },
            {
              dataField: 'registration.registrant',
              validationRules: [
                {
                  type: 'async',
                  message: 'Same Group/Registrant exists, please select other registrant or close the popup to find that registration',
                  validationCallback: (params) =>  Attendees.datagridUpdate.validateRegistration(params.value),
                },
              ],
              helpText: 'Same Group/Registrant can only register once',
              label: {
                text: 'Registrant',
              },
              editorType: 'dxLookup',
              editorOptions: {
                showClearButton: true,
                elementAttr: {
                  class: 'attendee-lookup-search',  // calling closing by the parent
                },
                valueExpr: 'id',
                displayExpr: 'infos.names.original',
                placeholder: 'Select a value...',
                // searchExpr: ['first_name', 'last_name'],
                searchPlaceholder: 'Search attendee',
                minSearchLength: 3,  // cause values disappeared in drop down
                searchTimeout: 200,  // cause values disappeared in drop down
                dropDownOptions: {
                  showTitle: false,
                  closeOnOutsideClick: true,
                },
                dataSource: Attendees.datagridUpdate.attendeeSource,
              },
            },
            {
              dataField: 'category',
              helpText: 'help text can be changed in /static/js /persons /datagrid_attendee_update_view.js',
              isRequired: true,
            },
            {
              itemType: 'button',
              horizontalAlignment: 'left',
              buttonOptions: {
                elementAttr: {
                  class: 'attendee-form-submits',    // for toggling editing mode
                },
                disabled: !Attendees.utilities.editingEnabled,
                text: 'Save Attending',
                icon: 'save',
                hint: 'save attending data in the popup',
                type: 'default',
                useSubmitBehavior: false,
                onClick: (clickEvent) => {
                  const validationResult = clickEvent.validationGroup.validate();
                  validationResult.status === 'pending' && validationResult.complete.then((validation) => {
                    if (validation.status === 'valid' && confirm('are you sure to submit the popup attendingForm?')) {
                      const userData = Attendees.datagridUpdate.attendingPopupDxForm.option('formData');

                      $.ajax({
                        url: ajaxUrl,
                        data: JSON.stringify(userData),
                        dataType: 'json',
                        contentType: 'application/json; charset=utf-8',
                        method: userData.id ? 'PUT' : 'POST',
                        success: (response) => {
                          Attendees.datagridUpdate.attendingPopup.hide();
                          DevExpress.ui.notify(
                            {
                              message: 'saving attending success',
                              width: 500,
                              position: {
                                my: 'center',
                                at: 'center',
                                of: window,
                              },
                            }, 'success', 2500);
                          response.attending_id = response.id;
                          Attendees.datagridUpdate.attendingsData[response.id] = response;
                          Attendees.datagridUpdate.populateAttendingButtons(Object.values(Attendees.datagridUpdate.attendingsData), $('div.attendings-buttons > div.dx-field-item-content'));
                        },
                        error: (response) => {
                          console.log('Failed to save data for AttendingForm in Popup, error: ', response);
                          console.log('formData: ', userData);
                          DevExpress.ui.notify(
                            {
                              message: 'saving attending error',
                              width: 500,
                              position: {
                                my: 'center',
                                at: 'center',
                                of: window,
                              },
                            }, 'error', 5000);
                        },
                      });
                    }
                  });
                }
              },
            },
            {
              itemType: 'button',
              horizontalAlignment: 'left',
              name: 'deleteAttendingButton',
              buttonOptions: {
                elementAttr: {
                  class: 'attendee-form-submits',    // for toggling editing mode
                },
                disabled: !Attendees.utilities.editingEnabled,
                text: 'Delete Attending',
                icon: 'trash',
                hint: 'delete the current Attending in the popup',
                type: 'danger',
                useSubmitBehavior: false,
                onClick: (clickEvent) => {
                  if (confirm('Are you sure to delete the attending and all its registrations&activities? Instead, setting "finish" dates in all its activities in the table is usually enough!')) {
                    $.ajax({
                      url: ajaxUrl,
                      method: 'DELETE',
                      success: (response) => {
                        Attendees.datagridUpdate.attendingPopup.hide();
                        DevExpress.ui.notify(
                          {
                            message: 'attending deleted',
                            width: 500,
                            position: {
                              my: 'center',
                              at: 'center',
                              of: window,
                            },
                          }, 'info', 2500);
                        attendingButton.remove();
                        Attendees.datagridUpdate.attendingMeetDatagrid.refresh();
                      },
                      error: (response) => {
                        console.log('Failed to delete attending in Popup, error: ', response);
                        DevExpress.ui.notify(
                          {
                            message: 'delete attending error',
                            width: 500,
                            position: {
                              my: 'center',
                              at: 'center',
                              of: window,
                            },
                          }, 'error', 5000);
                      },
                    });
                  }
                },
              },
            },
          ]
        }).dxForm('instance');
        e.append(formContainer);
      }
    };
  },

  validateRegistration: (value) => {
    const registration = Attendees.datagridUpdate.attendingPopupDxForm.option('formData') && Attendees.datagridUpdate.attendingPopupDxForm.option('formData').registration || {};
    var d = $.Deferred();
    if (!Attendees.utilities.editingEnabled) {
      d.resolve();
    }else {
      $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.registrationsEndpoint, {
        assembly: registration.assembly,
        registrant: registration.registrant,
      }).done((response) => {
        const registrations = response && response.data || [];
        if (registrations.length < 1){
          d.resolve();
        } else if(registrations.length < 2){
          registrations[0].id === registration.id ? d.resolve() : d.reject();
        }
        d.reject();
      });
    }
    return d.promise();
  },

  attendeeSource: new DevExpress.data.CustomStore({
    key: 'id',
    load: (loadOptions) => {
      // if (!Attendees.utilities.editingEnabled) return [Attendees.datagridUpdate.attendingPopupDxFormData.registration.registrant];

      const deferred = $.Deferred();
      const args = {};

      [
        'skip',
        'take',
        'sort',
        'filter',
        'searchExpr',
        'searchOperation',
        'searchValue',
        'group',
      ].forEach((i) => {
        if (i in loadOptions && Attendees.utilities.isNotEmpty(loadOptions[i]))
          args[i] = loadOptions[i];
      });

      $.ajax({
        url: Attendees.datagridUpdate.attendeeAttrs.dataset.attendeeEndpoint,
        dataType: 'json',
        data: args,
        success: (result) => {
          const registrant = Attendees.datagridUpdate.attendingPopupDxFormData.registration && Attendees.datagridUpdate.attendingPopupDxFormData.registration.registrant || null;
          const resulting_attendees = registrant ? result.data.concat([registrant]) : result.data;
          deferred.resolve(resulting_attendees, {
            totalCount: result.totalCount,
            summary: result.summary,
            groupCount: result.groupCount
          });
        },
        error: (response) => {
          console.log('ajax error here is response: ', response);
          deferred.reject('Data Loading Error, probably time out?');
        },
        timeout: 7000,
      });

      return deferred.promise();
    },
    byKey: (key) => {
      // if (!Attendees.utilities.editingEnabled && Attendees.datagridUpdate.placePopupDxFormData) {
      //   const mainAttendee = Attendees.datagridUpdate.attendingPopupDxFormData.registration && Attendees.datagridUpdate.attendingPopupDxFormData.registration.registrant || null;
      //   return mainAttendee ? [mainAttendee] : [];
      // } else {
        const d = new $.Deferred();
        $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.attendeeEndpoint + key + '/')
          .done((result) => {
            d.resolve(result);
          });
        return d.promise();
      // }
    },
  }),


  ///////////////////////  Place (Address) Popup and DxForm  ///////////////////////


  initPlacePopupDxForm: (event) => {
    const placeButton = event.target;
    Attendees.datagridUpdate.placePopup = $('div.popup-place-update').dxPopup(Attendees.datagridUpdate.placePopupDxFormConfig(placeButton)).dxPopup('instance');
    Attendees.datagridUpdate.fetchPlaceFormData(placeButton);
  },

  placePopupDxFormConfig: (placeButton) => {
    const ajaxUrl = $('form#place-update-popup-form').attr('action') + (placeButton.value ? placeButton.value + '/' : '');
    return {
      visible: true,
      title: (placeButton.value ? 'Viewing ' : 'Creating ') + placeButton.dataset.desc,
      minwidth: '20%',
      minheight: '30%',
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
          readOnly: !Attendees.utilities.editingEnabled,
          formData: {
            ...Attendees.datagridUpdate.placeDefaults,
            content_type: parseInt(placeButton.dataset.contentType),
            object_id: placeButton.dataset.objectId,
          },
          colCount: 12,
          scrollingEnabled: true,
          showColonAfterLabel: false,
          requiredMark: '*',
          labelLocation: 'top',
          minColWidth: '20%',
          showValidationSummary: true,
          items: [
            {
              colSpan: 3,
              dataField: 'display_name',
              // label: {
              //   text: 'Dwelling Reason',
              // },
              helpText: 'Why attendee occupy here',
              isRequired: true,
              editorOptions: {
                placeholder: 'Main/parent/past, etc',
              },
            },
            {
              colSpan: 3,
              dataField: 'display_order',
              helpText: '0 is shown before 1,2...',
              isRequired: true,
              editorOptions: {
                placeholder: '0/1/2/3, etc',
              },
              validationRules: [
                {
                  type: 'range',
                  max: 32767,
                  min: 0,
                  message: 'display_order should be between 0 and 32767'
                },
                {
                  type: 'required',
                  message: 'display_order is required'
                },
              ],
            },
            {
              colSpan: 3,
              dataField: 'start',
              editorType: 'dxDateBox',
              label: {
                text: 'stay from',
              },
              helpText: 'When moved in?',
              editorOptions: {
                type: 'date',
                showClearButton: true,
                dateSerializationFormat: 'yyyy-MM-dd',
                placeholder: 'click calendar',
              },
            },
            {
              colSpan: 3,
              dataField: 'finish',
              editorType: 'dxDateBox',
              label: {
                text: 'stay until',
              },
              helpText: 'When moved out?',
              editorOptions: {
                type: 'date',
                showClearButton: true,
                dateSerializationFormat: 'yyyy-MM-dd',
                placeholder: 'click calendar',
              },
            },
            {
              colSpan: 12,
              dataField: 'address.id',
              name: 'existingAddressSelector',
              label: {
                text: 'Address',
              },
              editorType: 'dxLookup',
              editorOptions: {
                showClearButton: true,
                elementAttr: {
                  class: 'address-lookup-search',  // calling closing by the parent
                },
                valueExpr: 'id',
                displayExpr: 'formatted',
                placeholder: 'Select a value...',
                searchExpr: ['street_number', 'formatted'],
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
                  if (e.previousValue !== e.value) {
                    const selectedAddress = $('div.address-lookup-search').dxLookup('instance')._dataSource._items.find(x => x.id === e.value);
                    if (selectedAddress){
                      Attendees.datagridUpdate.placePopupDxForm.updateData('address', selectedAddress);
                    }
                  }
                },
              },
            },
            {
              itemType: 'group',
              visible: false,
              name: 'NewAddressItems',
              colSpan: 12,
              colCount: 12,
              items: [
                {
                  colSpan: 4,
                  dataField: 'address.street_number',
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
                  dataField: 'address.route',
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
                  dataField: 'address.extra',
                  helpText: 'suite/floor number, etc',
                  label: {
                    text: 'Extra: unit/apt',
                  },
                  editorOptions: {
                    placeholder: 'example: Apt 2G',
                  },
                },
                {
                  colSpan: 4,
                  dataField: 'address.city',
                  name: 'locality',
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
                  dataField: 'address.postal_code',
                  helpText: 'ZIP code',
                  editorOptions: {
                    placeholder: "example: '94106'",
                  },
                },
                {
                  colSpan: 4,
                  dataField: 'address.state_id',
                  label: {
                    text: 'State',
                  },
                  editorType: 'dxLookup',
                  editorOptions: {
                    elementAttr: {
                      class: 'state-lookup-search',  // calling closing by the parent
                    },
                    valueExpr: 'id',
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
                    // onValueChanged: (e) => {
                    //   if (e.previousValue && e.previousValue !== e.value) {
                    //     const selectedState = $('div.state-lookup-search').dxLookup('instance')._dataSource._items.find(x => x.id === e.value);
                    //     console.log("hi 1401 here is selectedState: ", selectedState);
                    //   }
                    // },
                  },
                },
              ],
            },
            {
              colSpan: 3,
              itemType: 'button',
              horizontalAlignment: 'left',
              buttonOptions: {
                elementAttr: {
                  class: 'attendee-form-submits',    // for toggling editing mode
                },
                disabled: !Attendees.utilities.editingEnabled,
                text: 'Save Place',
                icon: 'save',
                hint: 'save Place data in the popup',
                type: 'default',
                useSubmitBehavior: true,
                onClick: (clickEvent) => {
                  if (confirm('Are you sure to submit the popup Place Form?')) {
                    const userData = Attendees.datagridUpdate.placePopupDxForm.option('formData');
                    const addressMaybeEdited = Attendees.datagridUpdate.placePopupDxForm.itemOption('NewAddressItems').visible;

                    if (addressMaybeEdited) {  // no address id means user creating new address
                      const newAddressExtra = Attendees.datagridUpdate.placePopupDxForm.getEditor("address.extra").option('value');
                      const newStreetNumber = Attendees.datagridUpdate.placePopupDxForm.getEditor("address.street_number").option('value');
                      const newRoute = Attendees.datagridUpdate.placePopupDxForm.getEditor("address.route").option('value');
                      const newCity = Attendees.datagridUpdate.placePopupDxForm.getEditor("address.city").option('value');
                      const newZIP = Attendees.datagridUpdate.placePopupDxForm.getEditor("address.postal_code").option('value');
                      const newStateAttrs = Attendees.datagridUpdate.placePopupDxForm.getEditor("address.state_id")._options;
                      const newAddressText = newStreetNumber + ' ' + newRoute + (newAddressExtra ? ', ' + newAddressExtra : '') + ', ' + newCity + ', ' + newStateAttrs.selectedItem.code + ' ' + newZIP + ', ' + newStateAttrs.selectedItem.country_name;

                      if (!(userData.address && userData.address.id)) {
                        userData.address = {
                          raw: 'new',     // for bypassing DRF validations from Django-Address model
                          new_address: {  // for creating new django-address instance bypassing DRF model validations
                            raw: userData.object_id,
                            type: 'street',   // use Django-admin to change if needed
                            extra: newAddressExtra,
                            formatted: placeButton.dataset.objectName + ': ' + newAddressText,
                            street_number: newStreetNumber,
                            route: newRoute,
                            locality: newCity,
                            post_code: newZIP,
                            state: newStateAttrs.selectedItem.name,
                            state_code: newStateAttrs.selectedItem.code,
                            country: newStateAttrs.selectedItem.country_name,
                            country_code: newStateAttrs.selectedItem.country_code,
                          },
                        };
                      }else{
                        userData.address.formatted = placeButton.dataset.objectName + ': ' + newAddressText;
                      }
                    }

                    $.ajax({
                      url: ajaxUrl,
                      data: JSON.stringify(userData),
                      dataType: 'json',
                      contentType: 'application/json; charset=utf-8',
                      method: userData.id ? 'PUT' : 'POST',
                      success: (savedPlace) => {
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
                          }, 'success', 2500);

                        const clickedButtonDescPrefix = placeButton.dataset.desc.split(' (')[0];
                        const newDesc = clickedButtonDescPrefix + ' (' + savedPlace.address.formatted + ')';
                        const newText = savedPlace.display_name + ': ' + savedPlace.address.formatted;
                        if (placeButton.value) {
                          placeButton.dataset.desc = newDesc;
                          placeButton.textContent = newText;
                        } else {
                          Attendees.datagridUpdate.familyButtonFactory({
                            class: placeButton.className.replace('place-button-new', '').replace('btn-outline-primary', 'btn-outline-success'),
                            value: savedPlace.id,
                            text: newText,
                            title: newDesc,
                            'data-desc': newDesc,
                            'data-object-id': placeButton.dataset.objectId,
                            'data-object-name': placeButton.dataset.objectName,
                            'data-content-type': placeButton.dataset.contentType,
                          }).insertAfter(placeButton);
                        }
                      },
                      error: (response) => {
                        console.log('Failed to save data for place Form in Popup, error: ', response);
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
                          }, 'error', 5000);
                      },
                    });
                  }
                },
              },
            },
            {
              colSpan: 3,
              itemType: 'button',
              horizontalAlignment: 'left',
              name: 'editAddressButton',
              visible: true,
              buttonOptions: {
                elementAttr: {
                  class: 'attendee-form-submits',    // for toggling editing mode
                },
                disabled: !Attendees.utilities.editingEnabled,
                text: 'Edit the address',
                icon: 'edit',
                hint: 'Modifying the current address, without creating one',
                type: 'success',
                useSubmitBehavior: false,
                onClick: (clickEvent) => {
                  if (confirm('Are you sure to edit the current address?')) {
                    Attendees.datagridUpdate.placePopupDxForm.itemOption('NewAddressItems', 'visible', true);
                    Attendees.datagridUpdate.placePopupDxForm.getEditor('address.id').option('visible', false);
                    Attendees.datagridUpdate.placePopupDxForm.getEditor('address.id').option('disable', true);
                    Attendees.datagridUpdate.placePopupDxForm.getEditor('editAddressButton').option('visible', false);
                    Attendees.datagridUpdate.placePopupDxForm.getEditor('newAddressButton').option('visible', false);
                  }
                },
              },
            },
            {
              colSpan: 3,
              itemType: 'button',
              horizontalAlignment: 'left',
              name: 'newAddressButton',
              visible: true,
              buttonOptions: {
                elementAttr: {
                  class: 'attendee-form-submits',    // for toggling editing mode
                },
                disabled: !Attendees.utilities.editingEnabled,
                text: 'Add new address',
                icon: 'home',
                hint: "Can't find exiting address, add a new address here",
                type: 'normal',
                useSubmitBehavior: false,
                onClick: (clickEvent) => {
                  if (confirm('Are you sure to add new address?')) {
                    Attendees.datagridUpdate.placePopupDxForm.itemOption('NewAddressItems', 'visible', true);
                    Attendees.datagridUpdate.placePopupDxForm.getEditor('address.id').option('visible', false);
                    Attendees.datagridUpdate.placePopupDxForm.getEditor('address.id').option('disable', true);
                    Attendees.datagridUpdate.placePopupDxForm.getEditor('newAddressButton').option('visible', false);
                    Attendees.datagridUpdate.placePopupDxForm.getEditor('editAddressButton').option('visible', false);
                    Attendees.datagridUpdate.placePopup.option('title', 'Creating Address');
                    Attendees.datagridUpdate.placePopupDxForm.option('formData').address.id = null;
                  }
                },
              },
            },
            {
              colSpan: 3,
              itemType: 'button',
              horizontalAlignment: 'left',
              name: 'deletePlaceButton',
              buttonOptions: {
                elementAttr: {
                  class: 'attendee-form-submits',    // for toggling editing mode
                },
                disabled: !Attendees.utilities.editingEnabled,
                text: 'Delete Place',
                icon: 'trash',
                hint: 'delete the current place in the popup',
                type: 'danger',
                useSubmitBehavior: false,
                onClick: (clickEvent) => {
                  if (confirm('Are you sure to delete the place? Instead, setting "move out" date is usually enough!')) {
                    $.ajax({
                      url: ajaxUrl,
                      method: 'DELETE',
                      success: (response) => {
                        Attendees.datagridUpdate.placePopup.hide();
                        DevExpress.ui.notify(
                          {
                            message: 'Place deleted',
                            width: 500,
                            position: {
                              my: 'center',
                              at: 'center',
                              of: window,
                            },
                          }, 'info', 2500);
                        placeButton.remove();
                      },
                      error: (response) => {
                        console.log('Failed to delete Place in Popup, error: ', response);
                        DevExpress.ui.notify(
                          {
                            message: 'delete place error',
                            width: 500,
                            position: {
                              my: 'center',
                              at: 'center',
                              of: window,
                            },
                          }, 'error', 5000);
                      },
                    });
                  }
                },
              },
            },
          ],
        }).dxForm('instance');
        e.append(formContainer);
      },
    };
  },

  fetchPlaceFormData: (placeButton) => {
    if (placeButton.value) {
      const allPlaces = Attendees.datagridUpdate.attendeeFormConfigs.formData.places.concat(Attendees.datagridUpdate.attendeeFormConfigs.formData.familyattendee_set.flatMap(familyattendee => familyattendee.family.places));
      const fetchedPlace = allPlaces.find(x => x.id === placeButton.value);
      if (!Attendees.utilities.editingEnabled && fetchedPlace) {
        Attendees.datagridUpdate.placePopupDxFormData = fetchedPlace;
        Attendees.datagridUpdate.placePopupDxForm.option('formData', fetchedPlace);
        // Attendees.datagridUpdate.addressId = fetchedPlace.address && fetchedPlace.address.id;
      } else {
        $.ajax({
          url: $('form#place-update-popup-form').attr('action') + placeButton.value + '/',
          success: (response) => {
            Attendees.datagridUpdate.placePopupDxFormData = response;
            Attendees.datagridUpdate.placePopupDxForm.option('formData', response);
            Attendees.datagridUpdate.placePopupDxForm.option('onFieldDataChanged', (e) => {
              e.component.validate()
            });
            // Attendees.datagridUpdate.addressId = Attendees.datagridUpdate.placePopupDxFormData.address && Attendees.datagridUpdate.placePopupDxFormData.address.id;
          },
          error: (response) => console.log('Failed to fetch data for Locate Form in Popup, error: ', response),
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
        'skip',
        'take',
        'sort',
        'filter',
        'searchExpr',
        'searchOperation',
        'searchValue',
        'group',
      ].forEach((i) => {
        if (i in loadOptions && Attendees.utilities.isNotEmpty(loadOptions[i]))
          args[i] = loadOptions[i];
      });

      $.ajax({
        url: $('div.datagrid-attendee-update').data('addresses-endpoint'),
        dataType: 'json',
        data: args,
        success: (result) => {
          deferred.resolve(result.data.concat([Attendees.datagridUpdate.placePopupDxFormData.place]), {
            totalCount: result.totalCount,
            summary: result.summary,
            groupCount: result.groupCount
          });
        },
        error: (response) => {
          console.log('ajax error here is response: ', response);
          deferred.reject('Data Loading Error, probably time out?');
        },
        timeout: 7000,
      });

      return deferred.promise();
    },
    byKey: (key) => {
      if (!Attendees.utilities.editingEnabled && Attendees.datagridUpdate.placePopupDxFormData) {
        return [Attendees.datagridUpdate.placePopupDxFormData.address];
      } else {
        const d = new $.Deferred();
        $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.addressesEndpoint, {id: key})
          .done((result) => {
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
        'skip',
        'take',
        'sort',
        'filter',
        'searchExpr',
        'searchOperation',
        'searchValue',
        'group',
      ].forEach((i) => {
        if (i in loadOptions && Attendees.utilities.isNotEmpty(loadOptions[i]))
          args[i] = loadOptions[i];
      });

      $.ajax({
        url: Attendees.datagridUpdate.attendeeAttrs.dataset.statesEndpoint,
        dataType: 'json',
        data: args,
        success: (result) => {
          deferred.resolve(result.data, {
            totalCount: result.totalCount,
            summary: result.summary,
            groupCount: result.groupCount
          });
        },
        error: (response) => {
          console.log('ajax error here is response: ', response);
          deferred.reject('Data Loading Error, probably time out?');
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
//        console.log("hi 1647 here is state key: ", key);
      $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.statesEndpoint, {id: key})
        .done((result) => {
          d.resolve(result.data);
        });
      return d.promise();
//      }
    },
  }),


  ///////////////////////  Family Attendees Datagrid in main DxForm  ///////////////////////


  initFamilyAttendeeDatagrid: (data, itemElement) => {
    const $myDatagrid = $("<div id='family-attendee-datagrid-container'>").dxDataGrid(Attendees.datagridUpdate.familyAttendeeDatagridConfig);
    itemElement.append($myDatagrid);
    Attendees.datagridUpdate.familyAttendeeDatagrid = $myDatagrid.dxDataGrid('instance');
  },

  familyAttendeeDatagridConfig: {
    dataSource: {
      store: new DevExpress.data.CustomStore({
        key: 'id',
        load: () => {
          return $.getJSON(Attendees.datagridUpdate.attendeeAttrs.dataset.familyAttendeesEndpoint);
        },
        byKey: (key) => {
          const d = new $.Deferred();
          $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.familyAttendeesEndpoint, {familyattendee_id: key})
            .done((result) => {
              d.resolve(result.data);
            });
          return d.promise();
        },
        update: (key, values) => {
          return $.ajax({
            url: Attendees.datagridUpdate.attendeeAttrs.dataset.familyAttendeesEndpoint + key + '/',
            method: 'PATCH',
            dataType: 'json',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify(values),
            success: (result) => {
              DevExpress.ui.notify(
                {
                  message: 'update success, please reload page if changing family',
                  width: 500,
                  position: {
                    my: 'center',
                    at: 'center',
                    of: window,
                  },
                }, 'success', 2000);
            },
          });
        },
        insert: function (values) {
          return $.ajax({
            url: Attendees.datagridUpdate.attendeeAttrs.dataset.familyAttendeesEndpoint,
            method: 'POST',
            dataType: 'json',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify(values),
            success: (result) => {
              DevExpress.ui.notify(
                {
                  message: 'Create success, please find the new attendee in the table',
                  width: 500,
                  position: {
                    my: 'center',
                    at: 'center',
                    of: window,
                  },
                }, "success", 2000);
            },
          });
        },
        remove: (key) => {
          return $.ajax({
            url: Attendees.datagridUpdate.attendeeAttrs.dataset.familyAttendeesEndpoint + key + '/',
            method: 'DELETE',
            success: (result) => {
              DevExpress.ui.notify(
                {
                  message: 'family member removed',
                  width: 500,
                  position: {
                    my: 'center',
                    at: 'center',
                    of: window,
                  },
                }, 'info', 2000);
            },
          });
        },
      }),
    },
    onInitNewRow: (e) => {
      DevExpress.ui.notify(
        {
          message: "Let's create a new family member, click away or hit Enter to save. Hit Esc to quit without save",
          width: 500,
          position: {
            my: 'center',
            at: 'center',
            of: window,
          },
        }, 'info', 3000);
    },
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
    editing: {
      mode: 'cell',
      allowUpdating: Attendees.utilities.editingEnabled,
      allowAdding: Attendees.utilities.editingEnabled,
      allowDeleting: false,
    },
    onEditingStart: (info) => {  // forbid editing names or names on top of page will be inconsistent.
      if (info.data.attendee && info.data.attendee.id === Attendees.datagridUpdate.attendeeId && ['attendee.first_name', 'attendee.last_name', 'attendee.first_name2', 'attendee.last_name2'].includes(info.column.dataField)) {
        info.cancel = true;
      }
    },
    onRowPrepared: (e) => {
      if (e.rowType === 'data' && e.data.attendee && e.data.attendee.id === Attendees.datagridUpdate.attendeeId) {
        e.rowElement.css('color', 'SeaGreen');
        e.rowElement.attr('title', 'Please scroll up and change main attendee data there!');
      }
    },
    columns: [
      {
        dataField: 'family.id',
        validationRules: [{type: 'required'}],
        caption: 'Family',
        groupIndex: 0,
        lookup: {
          valueExpr: 'id',
          displayExpr: 'display_name',
          dataSource: {
            store: new DevExpress.data.CustomStore({
              key: 'id',
              load: () => $.getJSON(Attendees.datagridUpdate.attendeeAttrs.dataset.attendeeFamiliesEndpoint),
              byKey: (key) => $.getJSON(Attendees.datagridUpdate.attendeeAttrs.dataset.attendeeFamiliesEndpoint + key + '/'),
            }),
          },
        },
      },
      {
        dataField: 'role',
        validationRules: [{type: 'required'}],
        caption: 'Role',
        lookup: {
          valueExpr: 'id',
          displayExpr: 'title',
          dataSource: {
            store: new DevExpress.data.CustomStore({
              key: 'id',
              load: () => {
                return $.getJSON(Attendees.datagridUpdate.attendeeAttrs.dataset.relationsEndpoint);
              },
              byKey: (key) => {
                const d = new $.Deferred();
                $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.relationsEndpoint, {relation_id: key})
                  .done((result) => {
                    d.resolve(result.data);
                  });
                return d.promise();
              },
            }),
          },
        },
      },
      {
        dataField: 'attendee.gender',
        validationRules: [{type: 'required'}],
        caption: 'Gender',
        lookup: {
          valueExpr: 'name',
          displayExpr: 'name',
          dataSource: Attendees.utilities.genderEnums(),
        }
      },
      {
        caption: 'Full name',
        dataField: 'attendee.infos.names.original',
        allowEditing: false,
        cellTemplate: (container, rowData) => {
          if (rowData.data.attendee.id === Attendees.datagridUpdate.attendeeId) {
            $('<span>', {text: rowData.data.attendee.infos.names.original}).appendTo(container);
          } else {
            const attrs = {
              class: 'text-info',
              text: rowData.data.attendee.infos.names.original,
              href: Attendees.datagridUpdate.attendeeAttrs.dataset.attendeeUrn + rowData.data.attendee.id,
            };
            $('<a>', attrs).appendTo(container);
          }
        },
      },
      {
        caption: 'First name',
        dataField: 'attendee.first_name',
        visible: false,
        validationRules: [
          {
            type: 'stringLength',
            max: 25,
            message: 'first name cannot exceed 25 characters'
          },
        ],
      },
      {
        caption: 'Last name',
        dataField: 'attendee.last_name',
        visible: false,
        validationRules: [
          {
            type: 'stringLength',
            max: 25,
            message: 'last name cannot exceed 25 characters'
          },
        ],
      },
      {
        caption: 'Last name2',
        dataField: 'attendee.last_name2',
        visible: false,
        validationRules: [
          {
            type: 'stringLength',
            max: 8,
            message: 'last name 2 cannot exceed 8 characters'
          },
        ],
      },
      {
        caption: 'First name2',
        dataField: 'attendee.first_name2',
        visible: false,
        validationRules: [
          {
            type: 'stringLength',
            max: 12,
            message: 'last name 2 cannot exceed 12 characters'
          },
        ],
      },
      {
        dataField: 'attendee.division',
        validationRules: [{type: 'required'}],
        caption: 'Attendee Division',
        lookup: {
          valueExpr: 'id',
          displayExpr: 'display_name',
          dataSource: {
            store: new DevExpress.data.CustomStore({
              key: 'id',
              load: () => {
                return $.getJSON(Attendees.datagridUpdate.attendeeAttrs.dataset.divisionsEndpoint);
              },
              byKey: (key) => {
                const d = new $.Deferred();
                $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.divisionsEndpoint, {division_id: key})
                  .done((result) => {
                    d.resolve(result.data);
                  });
                return d.promise();
              },
            }),
          },
        }
      },
      {
        dataField: 'start',
        dataType: 'date',
        editorOptions: {
          dateSerializationFormat: 'yyyy-MM-dd',
        },
      },
      {
        dataField: 'finish',
        dataType: 'date',
        editorOptions: {
          dateSerializationFormat: 'yyyy-MM-dd',
        },
      },
    ],
  },


  ///////////////////////  Family Attributes Popup and DxForm  ///////////////////////

  initFamilyAttrPopupDxForm: (event) => {
    const familyAttrButton = event.target;
    Attendees.datagridUpdate.familyAttrPopup = $('div.popup-family-attr-update').dxPopup(Attendees.datagridUpdate.familyAttrPopupDxFormConfig(familyAttrButton)).dxPopup('instance');
    Attendees.datagridUpdate.fetchFamilyAttrFormData(familyAttrButton);
  },

  familyAttrPopupDxFormConfig: (familyAttrButton) => {
    const ajaxUrl = $('form#family-attr-update-popup-form').attr('action') + (familyAttrButton.value ? familyAttrButton.value + '/': '');
    return {
      visible: true,
      title: familyAttrButton.value ? 'Viewing Family' : 'Creating Family',
      minwidth: '20%',
      minheight: '30%',
      position: {
        my: 'center',
        at: 'center',
        of: window,
      },
      dragEnabled: true,
      contentTemplate: (e) => {
        const formContainer = $('<div class="familyAttrForm">');
        Attendees.datagridUpdate.familyAttrPopupDxForm = formContainer.dxForm({
          readOnly: !Attendees.utilities.editingEnabled,
          formData: Attendees.datagridUpdate.familyAttrDefaults,
          colCount: 3,
          scrollingEnabled: true,
          showColonAfterLabel: false,
          requiredMark: '*',
          labelLocation: 'top',
          minColWidth: '20%',
          showValidationSummary: true,
          items: [
            {
              colSpan: 1,
              dataField: "display_name",
              label: {
                text: 'Name',
              },
              helpText: 'what family is this?',
              isRequired: true,
              editorOptions: {
                placeholder: 'Main/parent/past, etc',
              },
            },
            {
              colSpan: 1,
              dataField: 'display_order',
              helpText: '0 is shown before 1,2...',
              isRequired: true,
              editorOptions: {
                placeholder: '0/1/2/3, etc',
              },
              validationRules: [
                {
                  type: 'range',
                  max: 32767,
                  min: 0,
                  message: 'display_order should be between 0 and 32767'
                },
                {
                  type: 'required',
                  message: 'display_order is required'
                },
              ],
            },
            {
              colSpan: 1,
              dataField: 'division',
              editorType: 'dxSelectBox',
              isRequired: true,
              label: {
                text: 'Family major Division',
              },
              editorOptions: {
                valueExpr: 'id',
                displayExpr: 'display_name',
                placeholder: 'Select a value...',
                dataSource: new DevExpress.data.DataSource({
                  store: new DevExpress.data.CustomStore({
                    key: 'id',
                    loadMode: 'raw',
                    load: () => {
                      const d = $.Deferred();
                      $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.divisionsEndpoint).done((response) => {
                        d.resolve(response.data);
                      });
                      return d.promise();
                    },
                  })
                }),
              },
            },
            {
              colSpan: 1,
              itemType: 'button',
              horizontalAlignment: 'left',
              buttonOptions: {
                elementAttr: {
                  class: 'attendee-form-submits',    // for toggling editing mode
                },
                disabled: !Attendees.utilities.editingEnabled,
                text: 'Save Family',
                icon: 'save',
                hint: 'save Family attr data in the popup',
                type: 'default',
                useSubmitBehavior: true,
                onClick: (clickEvent) => {
                  if (Attendees.datagridUpdate.familyAttrPopupDxForm.validate().isValid && confirm('are you sure to submit the popup Family attr Form?')) {
                    const userData = Attendees.datagridUpdate.familyAttrPopupDxForm.option('formData');

                    $.ajax({
                      url: ajaxUrl,
                      data: JSON.stringify(userData),
                      dataType: 'json',
                      contentType: 'application/json; charset=utf-8',
                      method: userData.id ? 'PUT' : 'POST',
                      success: (savedFamily) => {
                        Attendees.datagridUpdate.familyAttrPopup.hide();
                        DevExpress.ui.notify(
                          {
                            message: 'saving Family attr success',
                            width: 500,
                            position: {
                              my: 'center',
                              at: 'center',
                              of: window,
                            },
                          }, 'success', 2500);

                        if (familyAttrButton.value) {
                          familyAttrButton.textContent(savedFamily.display_name)
                        } else {
                          Attendees.datagridUpdate.familyButtonFactory({value: savedFamily.id, text: savedFamily.display_name}).insertAfter(familyAttrButton);
                        }
                        Attendees.datagridUpdate.familyAttendeeDatagrid.refresh();
                      },
                      error: (response) => {
                        console.log('Failed to save data for Family attr Form in Popup, error: ', response);
                        console.log('formData: ', userData);
                        DevExpress.ui.notify(
                          {
                            message: 'saving Family error',
                            width: 500,
                            position: {
                              my: 'center',
                              at: 'center',
                              of: window,
                            },
                          }, 'error', 5000);
                      },
                    });
                  }
                },
              },
            },
            {
              colSpan: 1,
              itemType: 'button',
              horizontalAlignment: 'left',
              buttonOptions: {
                elementAttr: {
                  class: 'attendee-form-submits family-delete-button',    // for toggling editing mode
                },
                disabled: !Attendees.utilities.editingEnabled,
                hide: !familyAttrButton.value,
                text: 'Delete Family, Places, Relationships',
                icon: 'trash',
                hint: 'delete the Family with their places & marital relationships.',
                type: 'danger',
                useSubmitBehavior: false,
                onClick: (clickEvent) => {
                  if (confirm('Are you sure to delete the family and all its places and marital relationships in the popup?  Instead, editing the "finish" date or members is usually enough!')) {
                    $.ajax({
                      url: $('form#family-attr-update-popup-form').attr('action') + Attendees.datagridUpdate.familyAttrPopupDxFormData.id,
                      method: 'DELETE',
                      success: (response) => {
                        Attendees.datagridUpdate.familyAttrPopup.hide();
                        DevExpress.ui.notify(
                          {
                            message: 'Family deleted',
                            width: 500,
                            position: {
                              my: 'center',
                              at: 'center',
                              of: window,
                            },
                          }, 'info', 2500);

                        Attendees.datagridUpdate.familyAttendeeDatagrid.refresh();
                        Attendees.datagridUpdate.relationshipDatagrid.refresh();
                        $('li.' + familyAttrButton.value).remove();
                        familyAttrButton.remove();
                      },
                      error: (response) => {
                        console.log('Failed to delete Family in Popup, error: ', response);
                        DevExpress.ui.notify(
                          {
                            message: 'delete Family error',
                            width: 500,
                            position: {
                              my: 'center',
                              at: 'center',
                              of: window,
                            },
                          }, 'error', 5000);
                      },
                    });
                  }
                },
              },
            },
            {
              colSpan: 1,
              name: 'familyMemberCount',
              helpText: 'Close the popup to see family members in the table',
              label: {
                text: 'family member count',
              },
              template: (data, itemElement) => {
                $('<p>', {class: 'family-member-count', text: 0}).appendTo(itemElement);
              },
            },
          ],
        }).dxForm('instance');
        e.append(formContainer);
      }
    };
  },

  fetchFamilyAttrFormData: (familyAttrButton) => {
    if (familyAttrButton.value) {
      const families = Attendees.datagridUpdate.attendeeFormConfigs.formData.familyattendee_set.map(familyattendee => familyattendee.family);
      const fetchedFamily = families.find(x => x.id === familyAttrButton.value);
      if (!Attendees.utilities.editingEnabled && fetchedFamily) {
        $('p.family-member-count')[0].textContent = fetchedFamily.attendees.length;
        if (fetchedFamily.attendees.length > 1) {$('.family-delete-button').text('Remove attendee from Family')}
        Attendees.datagridUpdate.familyAttrPopupDxFormData = fetchedFamily;
        Attendees.datagridUpdate.familyAttrPopupDxForm.option('formData', fetchedFamily);
      } else {
        $.ajax({
          url: $('form#family-attr-update-popup-form').attr('action') + familyAttrButton.value + '/',
          success: (response) => {
            $('p.family-member-count')[0].textContent = response.attendees.length;
            if (response.attendees.length > 1) {$('.family-delete-button').text('Remove attendee from Family')}
            Attendees.datagridUpdate.familyAttrPopupDxFormData = response;
            Attendees.datagridUpdate.familyAttrPopupDxForm.option('formData', response);
          },
          error: (response) => console.log('Failed to fetch data for Family Attr Form in Popup, error: ', response),
        });
      }
    }
  },


  ///////////////////////  Relationship Datagrid in main DxForm  ///////////////////////


  initRelationshipDatagrid: (data, itemElement) => {
    const $relationshipDatagrid = $("<div id='relationship-datagrid-container'>").dxDataGrid(Attendees.datagridUpdate.relationshipDatagridConfig);
    itemElement.append($relationshipDatagrid);
    Attendees.datagridUpdate.relationshipDatagrid = $relationshipDatagrid.dxDataGrid("instance");
  },

  relationshipDatagridConfig: {
    dataSource: {
      store: new DevExpress.data.CustomStore({
        key: 'id',
        load: () => {
          return $.getJSON(Attendees.datagridUpdate.attendeeAttrs.dataset.relationshipsEndpoint);
        },
        byKey: (key) => {
          const d = new $.Deferred();
          $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.relationshipsEndpoint + key + '/')
            .done((result) => {
              d.resolve(result.data);
            });
          return d.promise();
        },
        update: (key, values) => {
          return $.ajax({
            url: Attendees.datagridUpdate.attendeeAttrs.dataset.relationshipsEndpoint + key + '/',
            method: 'PATCH',
            dataType: 'json',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify(values),
            success: (result) => {
              DevExpress.ui.notify(
                {
                  message: 'update success, please reload page if changing family',
                  width: 500,
                  position: {
                    my: 'center',
                    at: 'center',
                    of: window,
                  },
                }, 'success', 2000);
            },
          });
        },
        insert: (values) => {
          return $.ajax({
            url: Attendees.datagridUpdate.attendeeAttrs.dataset.relationshipsEndpoint,
            method: 'POST',
            dataType: 'json',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify(values),
            success: (result) => {
              DevExpress.ui.notify(
                {
                  message: "Create success, please find the new relationship in the table",
                  width: 500,
                  position: {
                    my: 'center',
                    at: 'center',
                    of: window,
                  },
                }, 'success', 2000);
            },
          });
        },
        remove: (key) => {
          return $.ajax({
            url: Attendees.datagridUpdate.attendeeAttrs.dataset.relationshipsEndpoint + key + '/',
            method: 'DELETE',
            success: (result) => {
              DevExpress.ui.notify(
                {
                  message: 'removed relationship success',
                  width: 500,
                  position: {
                    my: 'center',
                    at: 'center',
                    of: window,
                  },
                }, 'info', 2000);
            },
          });
        },
      }),
    },
    onRowInserted: (e) => {
      Attendees.datagridUpdate.relationshipDatagrid.refresh();  // or the new inserted to_attendee dxlookup won't show
    },
    onInitNewRow: (e) => {
      e.data.from_attendee = Attendees.datagridUpdate.attendeeId;
      DevExpress.ui.notify(
        {
          message: "Let's create a relationship, click away or hit Enter to save. Hit Esc to quit without save",
          width: 500,
          position: {
            my: 'center',
            at: 'center',
            of: window,
          },
        }, "info", 3000);
    },
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
    wordWrapEnabled: true,
    grouping: {
      autoExpandAll: true,
    },
    editing: {
      mode: 'cell',
      allowUpdating: Attendees.utilities.editingEnabled,
      allowAdding: Attendees.utilities.editingEnabled,
      allowDeleting: false,
    },
    onRowInserting: (rowData) => {
      const infos = {show_secret: {}};
      if (rowData.data.infos && rowData.data.infos.show_secret) {
        infos.show_secret[Attendees.utilities.userAttendeeId] = true;
      }
      rowData.data.infos = infos;
    },
    onRowUpdating: (rowData) => {
      if (rowData.newData.infos && 'show_secret' in rowData.newData.infos) { // value could be intentionally false to prevent someone seeing it
        const showSecret = rowData.oldData.infos.show_secret;
        const isItSecretWithCurrentUser = rowData.newData.infos.show_secret;
        if (isItSecretWithCurrentUser) {
          showSecret[Attendees.utilities.userAttendeeId] = true;
        } else {
          delete showSecret[Attendees.utilities.userAttendeeId];
        }
        rowData.newData.infos.show_secret = showSecret;
      }
    },
    columns: [
      {
        dataField: 'relation',
        validationRules: [{type: 'required'}],
        caption: 'Role',
        lookup: {
          valueExpr: 'id',
          displayExpr: 'title',
          dataSource: {
            store: new DevExpress.data.CustomStore({
              key: 'id',
              load: () => {
                return $.getJSON(Attendees.datagridUpdate.attendeeAttrs.dataset.relationsEndpoint, {take: 100});
              },
              byKey: (key) => {
                const d = new $.Deferred();
                $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.relationsEndpoint, {relation_id: key})
                  .done((result) => {
                    d.resolve(result.data);
                  });
                return d.promise();
              },
            }),
          },
        },
      },
      {
        dataField: 'to_attendee',
        validationRules: [{type: 'required'}],
        caption: 'Attendee',
        lookup: {
          valueExpr: 'id',
          displayExpr: (item) => {
            return item ? '(' + item.gender[0] + ") " + item.infos.names.original : null;
          },
          dataSource: {
            store: new DevExpress.data.CustomStore({
              key: 'id',
              load: (searchOpts) => {
                const params = {};
                if (searchOpts.searchValue) {
                  const searchCondition = ['infos__names', searchOpts.searchOperation, searchOpts.searchValue];
                  params.filter = JSON.stringify(searchCondition);
                }
                return $.getJSON(Attendees.datagridUpdate.attendeeAttrs.dataset.relatedAttendeesEndpoint, params);
              },
              byKey: (key) => {
                const d = new $.Deferred();
                $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.relatedAttendeesEndpoint + key + '/')
                  .done((result) => {
                    d.resolve(result.data);
                  });
                return d.promise();
              },
            }),
          },
        },
      },
      {
        dataField: 'in_family',
        editorOptions: {
          showClearButton: true,
        },
        caption: 'Family',
        groupIndex: 0,
        lookup: {
          valueExpr: 'id',
          displayExpr: "display_name",
          dataSource: {
            store: new DevExpress.data.CustomStore({
              key: 'id',
              load: () => $.getJSON(Attendees.datagridUpdate.attendeeAttrs.dataset.attendeeFamiliesEndpoint),
              byKey: (key) => {
                if (key) {
                  $.getJSON(Attendees.datagridUpdate.attendeeAttrs.dataset.attendeeFamiliesEndpoint + key + '/');
                }
              },
            }),
          },
        },
      },
      {
        dataField: "scheduler",
        caption: "Can change main attendee's schedule",
        dataType: "boolean",
        calculateCellValue: (rowData) => {
          return rowData.scheduler ? rowData.scheduler : false;
        },
      },
      {
        dataField: "emergency_contact",
        caption: 'Contact when Main attendee in emergency',
        dataType: "boolean",
        calculateCellValue: (rowData) => {
          return rowData.scheduler ? rowData.scheduler : false;
        },
      },
      {
        caption: 'Secret shared with you',
        dataField: 'infos.show_secret',
        calculateCellValue: (rowData) => {
          if (rowData.infos) {
            const showSecret = rowData.infos.show_secret;
            const result = !!(showSecret && showSecret[Attendees.utilities.userAttendeeId]);
            return result;
          } else {
            return false;
          }
        },
        dataType: 'boolean',
      },
      {
        dataField: 'start',
        dataType: 'datetime',
        format: 'MM/dd/yyyy',
      },
      {
        dataField: 'finish',
        dataType: 'datetime',
        format: 'MM/dd/yyyy',
      },
    ],
  },


  ///////////////////////  Past Datagrids (dynamic) in main DxForm  ///////////////////////

  initPastDatagrid: (data, itemElement, args) => {
    const $pastDatagrid = $("<div id='" + args.type + "-past-datagrid-container'>").dxDataGrid(Attendees.datagridUpdate.pastDatagridConfig(args));
    itemElement.append($pastDatagrid);
    return $pastDatagrid.dxDataGrid("instance");
  },

  pastDatagridConfig: (args) => { // {type: 'education', dataFields: {display_name: 'display_name', start: 'start'}, extraDatagridOpts:{editing:{mode:'popup'}}}
    const columns = [
      {
        dataField: 'category',
        validationRules: [{type: 'required'}],
        lookup: {
          valueExpr: 'id',
          displayExpr: 'display_name',
          dataSource: {
            store: new DevExpress.data.CustomStore({
              key: 'id',
              load: () => {
                return $.getJSON(Attendees.datagridUpdate.attendeeAttrs.dataset.categoriesEndpoint, {
                  take: 100,
                  type: args.type,
                });
              },
              byKey: (key) => {
                const d = new $.Deferred();
                $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.categoriesEndpoint + key + '/')
                  .done((result) => {
                    d.resolve(result);
                  });
                return d.promise();
              },
            }),
          },
        },
      },
      {
        dataField: 'display_name',
      },
      {
        caption: 'Secret shared with you',
        dataField: 'infos.show_secret',
        width: '18%',
        calculateCellValue: (rowData) => {
          if (rowData.infos) {
            const showSecret = rowData.infos.show_secret;
            return !!(showSecret && showSecret[Attendees.utilities.userAttendeeId]);
          } else {
            return false;
          }
        },
        dataType: 'boolean',
      },
      {
        dataField: 'infos.comment',
        caption: 'Comment',
        dataType: 'string',
        width: '32%',
      },
      {
        dataField: 'when',
        dataType: 'date',
      },
      {
        dataField: 'finish',
        dataType: 'date',
      },
    ];

    return {
      dataSource: {
        store: new DevExpress.data.CustomStore({
          key: 'id',
          load: () => {
            return $.getJSON(Attendees.datagridUpdate.attendeeAttrs.dataset.pastsEndpoint, {category__type: args.type});
          },
          byKey: (key) => {
            const d = new $.Deferred();
            $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.pastsEndpoint + key + '/')
              .done((result) => {
                d.resolve(result.data);
              });
            return d.promise();
          },
          update: (key, values) => {
            return $.ajax({
              url: Attendees.datagridUpdate.attendeeAttrs.dataset.pastsEndpoint + key + '/?' + $.param({category__type: args.type}),
              method: 'PATCH',
              dataType: 'json',
              contentType: 'application/json; charset=utf-8',
              data: JSON.stringify(values),
              success: (result) => {
                DevExpress.ui.notify(
                  {
                    message: 'update ' + args.type + ' success',
                    width: 500,
                    position: {
                      my: 'center',
                      at: 'center',
                      of: window,
                    },
                  }, 'success', 2000);
              },
            });
          },
          insert: function (values) {
            const subject = {
              content_type: Attendees.datagridUpdate.attendeeAttrs.dataset.attendeeContenttypeId,
              object_id: Attendees.datagridUpdate.attendeeId,
            };
            return $.ajax({
              url: Attendees.datagridUpdate.attendeeAttrs.dataset.pastsEndpoint,
              method: 'POST',
              dataType: 'json',
              contentType: 'application/json; charset=utf-8',
              data: JSON.stringify({...values, ...subject}),
              success: (result) => {
                DevExpress.ui.notify(
                  {
                    message: 'Create ' + args.type + ' success',
                    width: 500,
                    position: {
                      my: 'center',
                      at: 'center',
                      of: window,
                    },
                  }, 'success', 2000);
              },
            });
          },
          remove: (key) => {
            return $.ajax({
              url: Attendees.datagridUpdate.attendeeAttrs.dataset.pastsEndpoint + key + '/?' + $.param({category__type: args.type}),
              method: 'DELETE',
              success: (result) => {
                DevExpress.ui.notify(
                  {
                    message: 'removed '+ args.type +' success',
                    width: 500,
                    position: {
                      my: 'center',
                      at: 'center',
                      of: window,
                    },
                  }, 'info', 2000);
              },
            });
          },
        }),
      },
      onRowInserting: (rowData) => {
        const infos = {show_secret: {}, comment: rowData.data.infos && rowData.data.infos.comment};
        if (rowData.data.infos && rowData.data.infos.show_secret) {
          infos.show_secret[Attendees.utilities.userAttendeeId] = true;
        }
        rowData.data.infos = infos;
      },
      onInitNewRow: (e) => {  // don't assign e.data or show_secret somehow messed up
        DevExpress.ui.notify(
          {
            message: "Let's create a " + args.type + ", click away or hit Enter to save. Hit Esc to quit without save",
            width: 500,
            position: {
              my: 'center',
              at: 'center',
              of: window,
            },
          }, 'info', 3000);
      },
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
      width: '100%',
      grouping: {
        autoExpandAll: true,
      },
      onRowUpdating: (rowData) => {
        if (rowData.newData.infos) { // could be comment or show_secret or both
          const updatingInfos = rowData.oldData.infos || {};
          if ('show_secret' in rowData.newData.infos) {  // infos.show_secret could be false or true
            let updatingShowSecret = typeof (updatingInfos.show_secret) === 'object' && updatingInfos.show_secret || {};  // could show_secret to others
            if (rowData.newData.infos.show_secret) {  // boolean from UI but db needs to store attendee
              updatingShowSecret[Attendees.utilities.userAttendeeId] = true;
            } else {
              delete updatingShowSecret[Attendees.utilities.userAttendeeId];
            }
            updatingInfos.show_secret = updatingShowSecret;
          }
          if ('comment' in rowData.newData.infos) {  // UI may send this or not
            updatingInfos.comment = rowData.newData.infos.comment;
          }
          rowData.newData.infos = updatingInfos;
        }
      },
      columns: columns.flatMap(column => {
        if (column.dataField in args.dataFieldAndOpts) {
          return [{...column, ...args.dataFieldAndOpts[column.dataField]}];
        } else {
          return [];
        }
      }),
    };
  },

  noteEditingArgs: {
    mode: 'popup',
    popup: {
      showTitle: true,
      title: 'Editing note of Attendee'
    },
    form: {
      items: [
        {
          dataField: 'category',
        },
        {
          dataField: 'display_name',
        },
        {
          dataField: 'infos.show_secret',
        },
        {
          dataField: 'when',
        },
        {
          dataField: 'infos.comment',
          editorType: 'dxTextArea',
          colSpan: 2,
          editorOptions: {
            autoResizeEnabled: true,
          }
        },
      ],
    },
  },


  ///////////////////////  AttendingMeet Datagrid in main DxForm  ///////////////////////

  initAttendingMeetsDatagrid: (data, itemElement) => {
    const $attendingMeetDatagrid = $("<div id='attendingmeet-datagrid-container'>").dxDataGrid(Attendees.datagridUpdate.attendingMeetDatagridConfig);
    itemElement.append($attendingMeetDatagrid);
    Attendees.datagridUpdate.attendingMeetDatagrid = $attendingMeetDatagrid.dxDataGrid('instance');
  },

  attendingMeetDatagridConfig: {
    dataSource: {
      store: new DevExpress.data.CustomStore({
        key: 'id',
        load: () => {
          return $.getJSON(Attendees.datagridUpdate.attendeeAttrs.dataset.attendingmeetsEndpoint);
        },
        byKey: (key) => {
          const d = new $.Deferred();
          $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.attendingmeetsEndpoint + key + '/')
            .done((result) => {
              d.resolve(result.data);
            });
          return d.promise();
        },
        update: (key, values) => {
          return $.ajax({
            url: Attendees.datagridUpdate.attendeeAttrs.dataset.attendingmeetsEndpoint + key + '/',
            method: 'PATCH',
            dataType: 'json',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify(values),
            success: (result) => {
              DevExpress.ui.notify(
                {
                  message: 'update success',
                  width: 500,
                  position: {
                    my: 'center',
                    at: 'center',
                    of: window,
                  }
                }, 'success', 2000);
            },
          });
        },
        insert: (values) => {
          return $.ajax({
            url: Attendees.datagridUpdate.attendeeAttrs.dataset.attendingmeetsEndpoint,
            method: 'POST',
            dataType: 'json',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify(values),
            success: (result) => {
              DevExpress.ui.notify(
                {
                  message: 'Create success, please find the new activity in the table',
                  width: 500,
                  position: {
                    my: 'center',
                    at: 'center',
                    of: window,
                  },
                }, 'success', 2000);
            },
          });
        },
        remove: (key) => {
          return $.ajax({
            url: Attendees.datagridUpdate.attendeeAttrs.dataset.attendingmeetsEndpoint + key + '/',
            method: 'DELETE',
            success: (result) => {
              DevExpress.ui.notify(
                {
                  message: 'removed AttendingMeet success',
                  width: 500,
                  position: {
                    my: 'center',
                    at: 'center',
                    of: window,
                  },
                }, 'info', 2000);
            },
          });
        },
      }),
    },
    onRowInserted: (e) => {
      Attendees.datagridUpdate.attendingMeetDatagrid.refresh();
    },
    onInitNewRow: (e) => {
      for (const [key, value] of Object.entries(Attendees.datagridUpdate.attendingmeetDefaults)) {
        e.data[key] = value;
      }
    },
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
    wordWrapEnabled: true,
    grouping: {
      autoExpandAll: true,
    },
    columns: [
      {
        dataField: 'attending',
        validationRules: [{type: 'required'}],
        visible: false,
        lookup: {
          valueExpr: 'id',
          displayExpr: 'attending_label',
          dataSource: {
            store: new DevExpress.data.CustomStore({
              key: 'id',
              load: (e) => {
                return $.getJSON(Attendees.datagridUpdate.attendeeAttrs.dataset.attendingsEndpoint);
              },
              byKey: (key) => {
                if (key) {
                  const d = $.Deferred();
                  $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.attendingsEndpoint + key + '/').done((response) => {
                    d.resolve(response);
                  });
                  return d.promise();
                }
              },
            }),
          },
        },
      },
      {
        dataField: 'assembly',
        groupIndex: 0,
        validationRules: [{type: 'required'}],
        caption: 'Group (Assembly)',
        setCellValue: (rowData, value) => {
          rowData.assembly = value;
          rowData.meet = null;
          rowData.character = null;
        },
        lookup: {
          valueExpr: 'id',
          displayExpr: 'display_name',
          dataSource: {
            store: new DevExpress.data.CustomStore({
              key: 'id',
              load: () => $.getJSON(Attendees.datagridUpdate.attendeeAttrs.dataset.assembliesEndpoint),
              byKey: (key) => {
                if (key) {
                  const d = $.Deferred();
                  $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.assembliesEndpoint + key + '/').done((response) => {
                    d.resolve(response);
                  });
                  return d.promise();
                }
              },
            }),
          },
        },
      },
      {
        dataField: 'meet',
        caption: 'Activity (Meet)',
        validationRules: [{type: 'required'}],
        lookup: {
          valueExpr: 'id',
          displayExpr: 'display_name',
          dataSource: (options) => {
            return {
              filter: options.data ? {'assemblies[]': options.data.assembly} : null,
              store: new DevExpress.data.CustomStore({
                key: 'id',
                load: (searchOpts) => {
                  return $.getJSON(Attendees.datagridUpdate.attendeeAttrs.dataset.meetsEndpoint, searchOpts.filter);
                },
                byKey: (key) => {
                  const d = new $.Deferred();
                  $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.meetsEndpoint + key + '/')
                    .done((result) => {
                      d.resolve(result);
                    });
                  return d.promise();
                },
              }),
            };
          },
        },
      },
      {
        dataField: 'character',
        validationRules: [{type: 'required'}],
        lookup: {
          valueExpr: 'id',
          displayExpr: 'display_name',
          dataSource: (options) => {
            return {
              filter: options.data ? {'assemblies[]': options.data.assembly} : null,
              store: new DevExpress.data.CustomStore({
                key: 'id',
                load: (searchOpts) => {
                  return $.getJSON(Attendees.datagridUpdate.attendeeAttrs.dataset.charactersEndpoint, searchOpts.filter);
                },
                byKey: (key) => {
                  const d = new $.Deferred();
                  $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.charactersEndpoint + key + '/')
                    .done((result) => {
                      d.resolve(result);
                    });
                  return d.promise();
                },
              }),
            };
          }
        },
      },
      {
        dataField: 'category',
        validationRules: [{type: 'required'}],
      },
      {
        dataField: 'start',
        validationRules: [{type: 'required'}],
        dataType: 'datetime',
        format: 'MM/dd/yyyy',
        editorOptions: {
          type: 'datetime',
          dateSerializationFormat: 'yyyy-MM-ddTHH:mm:ss',
        },
      },
      {
        dataField: 'finish',
        validationRules: [{type: 'required'}],
        dataType: 'datetime',
        format: 'MM/dd/yyyy',
        editorOptions: {
          type: 'datetime',
          dateSerializationFormat: 'yyyy-MM-ddTHH:mm:ss',
        },
      },
    ],
  },

  attendingMeetEditingArgs: {
    mode: 'popup',
    popup: {
      showTitle: true,
      title: 'Editing Attendee activities'
    },
    texts: {
      confirmDeleteMessage: 'Are you sure to delete it and all its attendances? Instead, setting the "finish" date is usually enough!',
    },
    form: {
      items: [
        {
          colSpan: 2,
          dataField: 'attending',
        },
        {
          dataField: 'assembly',
        },
        {
          dataField: 'meet',
        },
        {
          dataField: 'character',
          editorOptions: {
            showClearButton: true,
          }
        },
        {
          dataField: 'category',
        },
        {
          dataField: 'start',
        },
        {
          dataField: 'finish',
        },
      ],
    },
  },
};

$(document).ready(() => {
  Attendees.datagridUpdate.init();
});
