Attendees.utilities = {
  editingEnabled: false,
  userAuthGroups: {},
  userAttendeeId: '',

  init: () => {
    console.log("attendees/static/js/shared/utilities.js");
    Attendees.utilities.userAuthGroups = $('body').data('user-auth-groups');
    Attendees.utilities.userAttendeeId = $('body').data('user-attendee-id');
  },

  toggleEditingAndReturnStatus: (event) => {
    if (confirm('Are you sure to toggle editing mode?')){
      Attendees.utilities.editingEnabled = event.currentTarget.checked;
    } else {
      event.preventDefault();  // stop checkbox from being changed.
    }
    return Attendees.utilities.editingEnabled;
  },  // if button clicking bug can't be fixed, considering DevExtreme DxSwitch

  isNotEmpty: (value) => {
      return value !== undefined && value !== null && value !== "";
  },

  toggleDxFormGroups: (animationSpeed="fast") => {
    $(".dx-form-group-caption")
      .each(function () {
        $(this)
          .prepend(
            $('<div />')
                .css({
                    "margin-right": "1rem",
                })
                .dxButton({
                    "icon": "collapse",
                    "onClick": (e) => {
                        const hidden = e.component.option('icon') === 'expand';
                        const $caption = e.element.closest('.dx-form-group-caption');
                        const $content = $caption.siblings(".dx-form-group-content");
                        $content.toggle(animationSpeed);
                        e.component.option(
                            'icon',
                            hidden ? 'collapse' : 'expand'
                        );
                    }
                })
          );
      });
  },  // jQuery toggle() from https://supportcenter.devexpress.com/ticket/details/t525231

  trimBothKeyAndValueButKeepBasicContacts: (obj, keepEmpties=false) => {
    return Object.entries(obj).reduce((acc, curr) => {
      const [key, value] = curr;
      const trimmedValue = value ? value.trim() : null;

      if(keepEmpties || trimmedValue || trimmedValue in Attendees.utilities.basicContacts) {  // Will retain a single empty string as the only one empty key
        acc[key.trim()] = trimmedValue;  // acc[key.trim()] = typeof obj[key] == 'string'? obj[key].trim() : trimObj(obj[key]);
      }
      return acc;
    }, {});
  },  // https://stackoverflow.com/a/33511005/4257237

  convertObjectToFormData: object => Object.keys(object).reduce((formData, key) => {
            formData.append(key, object[key]);
            return formData;   // https://stackoverflow.com/a/62936649/4257237
        }, new FormData()),

  setAjaxLoaderOnDevExtreme: () => {
    $(document).ajaxStop(function(){
      $('div.dx-loadpanel').dxLoadPanel('hide');
    });

    $(document).ajaxStart(function(){
      $('div.dx-loadpanel').dxLoadPanel('show');
    });

  },

  debounce : (delay, fn) => {
    let timer = null;
    return (...arguments) => {
      const context = this,
            args = arguments;

      clearTimeout(timer);
      timer = setTimeout(() => {
        fn.apply(context, args);
      }, delay);
    };
  },

  toggleSelect2All: (event, inputSelector) => {
     const $select2Input = $(event.delegateTarget).find(inputSelector);
     const $checkAllBox = $(event.currentTarget);
     const allOptions = $select2Input.children('option').map((i,e) => e.value).get();
     const options = $checkAllBox.is(':checked') ? allOptions : [];
     $select2Input.val(options).trigger('change');
  },

  testArraysEqualAfterSort : (a, b) => {
    a = Array.isArray(a) ? a.sort() : [];
    b = Array.isArray(b) ? b.sort() : [];
    return a.length > 0 && a.length === b.length && a.every((el, ix) => el === b[ix]);
  }, // https://stackoverflow.com/a/39967517/4257237

  alterCheckBoxAndValidations: (currentTarget, inputSelector) => {
    const $currentTarget = $(currentTarget);

    if ($currentTarget.is('select')) {
      const $checkAllBox = $currentTarget.siblings('div.input-group-append').find(inputSelector);
      const allOptions = $currentTarget.children('option').map((i,e) => e.value).get();
      const chosenOptions = $currentTarget.val() || [];

        if (chosenOptions.length) {
          $currentTarget.removeClass('is-invalid');
        } else {
          $currentTarget.addClass('is-invalid');
        }
      $checkAllBox.prop('checked', Attendees.utilities.testArraysEqualAfterSort(chosenOptions, allOptions));
    }
  },

  genderEnums: () => {
    return [
      {name: 'MALE'},
      {name: 'FEMALE'},
      {name: 'UNSPECIFIED'},
    ];
  },

  basicContacts: {
    phone1: null,
    phone2: null,
    email1: null,
    email2: null,
  },
};

$(document).ready(() => {
  Attendees.utilities.init();
});
