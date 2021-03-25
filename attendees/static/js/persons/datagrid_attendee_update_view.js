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
            $attendingInfos = $("<ul>").attr({class: "attending-infos"}); // .text('attended:')
            if (data.editorOptions && data.editorOptions.value){
              data.editorOptions.value.forEach(attending => {
                  $("<li>").attr({class: "joined-meet-"+attending.meet_slug}).text(attending.meet_name).appendTo($attendingInfos);
              });
            }
            $("<li>").attr({class: "joined-meet-new"}).text("+ Attend a new meet").appendTo($attendingInfos);
            $attendingInfos.appendTo(itemElement);
          }, // try this next https://supportcenter.devexpress.com/ticket/details/t717702
      },
      {
        template: $("<button>").attr({class: 'btn button btn-primary btn-sm'}).text('blah'),
      },
      {
        itemType: "button",
        buttonOptions: {
            text: "meet!",
            horizontalAlignment: "left", // doesn't align to left
            type: "primary",
            onClick: function () {
                console.log('blah');
            }
        }
      },
    ]

  },

  dxForm: null, // will be assigned later
  attendeeAttrs: null, // will be assigned later
  attendeeId: null, // will be assigned later

  initAttendeeForm: () => {
    Attendees.datagridUpdate.attendeeAttrs = document.querySelector('div.datagrid-update');
    Attendees.datagridUpdate.attendeeId = Attendees.datagridUpdate.attendeeAttrs.id.replace("attendee_", "");

    $.ajax
      ({
        url      : Attendees.datagridUpdate.attendeeAttrs.dataset.attendeeEndpoint + Attendees.datagridUpdate.attendeeId + '/',
        success  : (response) => {
                      Attendees.datagridUpdate.attendeeFormConfigs.formData = response.data[0];
                      Attendees.datagridUpdate.dxForm = $(".datagrid-update").dxForm(Attendees.datagridUpdate.attendeeFormConfigs).dxForm("instance");
                   },
//        error    : (response) => {
//                   },
      });

  },
}

$(document).ready(() => {
  Attendees.datagridUpdate.init();
});
