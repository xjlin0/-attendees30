Attendees.dataAttendees = {
  init: () => {
    console.log("attendees/static/js/persons/datagrid_assembly_data_attendees.js");
    Attendees.utilities.setAjaxLoaderOnDevExtreme();
    Attendees.dataAttendees.setDataAttrs();
    Attendees.dataAttendees.setMeetsColumns([]);
    Attendees.dataAttendees.startDataGrid();
  },

  attendeeUrn: null,
  familyAttendancesUrn: null,

  setDataAttrs: () => {
    const $AttendeeAttrs = document.querySelector('div.dataAttendees').dataset;
    Attendees.dataAttendees.familyAttendancesUrn = $AttendeeAttrs.familyAttendancesUrn;
    Attendees.dataAttendees.attendeeUrn = $AttendeeAttrs.attendeeUrn;
  },

  startDataGrid: () => {
    Attendees.dataAttendees.dataGridOpts['dataSource'] = Attendees.dataAttendees.customStore;
    $("div.dataAttendees").dxDataGrid(Attendees.dataAttendees.dataGridOpts);//.dxDataGrid("instance");
  },

  customStore: new DevExpress.data.CustomStore({
    key: "id",
    load: (loadOptions) => {
      const deferred = $.Deferred();
      const args = {assemblies: JSON.stringify([$('div.dataAttendees').data('assembly')])};

      [
        "skip",
        "take",
        "requireTotalCount",
        "requireGroupCount",
        "sort",
        "filter",
        "totalSummary",
        "group",
        "groupSummary"
      ].forEach((i) => {
          if (i in loadOptions && Attendees.utilities.isNotEmpty(loadOptions[i]))
              args[i] = JSON.stringify(loadOptions[i]);
      });

      $.ajax({
        url: "/persons/api/datagrid_data_attendees/",
        dataType: "json",
        data: args,
        success: (result) => {
          deferred.resolve(result.data, {
            totalCount: result.totalCount,
            summary:    result.summary,
            groupCount: result.groupCount
          });
        },
        error: () => {
          deferred.reject("Data Loading Error, probably time out?");
        },
        timeout: 30000,
      });

      return deferred.promise();
    }
  }),

  dataGridOpts: {
    dataSource: null, // set later in startDataGrid()
    sorting: {
      mode: "multiple",
    },
    filterRow: { visible: true },  //filter doesn't work with fields with calculateDisplayValue yet
    searchPanel: { visible: true },   //search doesn't work with fields with calculateDisplayValue yet
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
//    groupPanel: {
//      visible: "auto",
//    },
    columnChooser: {
      enabled: true,
      mode: "select",
    },
    columnFixing: {
      enabled: true
    },
    onCellPrepared: e => e.rowType === "header" && e.column.dataHtmlTitle && e.cellElement.attr("title", e.column.dataHtmlTitle),

    headerFilter: {
      visible: true
    },
    showBorders: false,
    remoteOperations: true,
    paging: {
        pageSize:10
    },
    pager: {
        showPageSizeSelector: true,
        allowedPageSizes: [10, 30, 5000]
    },
    columns: null,  // will be initialized later.
    },

  initialAttendeesColumns: [
//    {
//      caption: "attendee_id",
//      dataField: "id",
//      dataType: "string",
//    },
    {
      caption: "Full name",
      allowSorting: false,
      dataField: "infos.names",
      name: 'infos.names.original',
      dataType: "string",
      allowHeaderFiltering: false,
      cellTemplate: (container, rowData) => {
        const attrs = {
          "class": "text-info",
          "text": rowData.data.infos.names.original,
          "href": Attendees.dataAttendees.attendeeUrn + rowData.data.id,
        };
        $($('<a>', attrs)).appendTo(container);
      },
    },
    {
      dataHtmlTitle: "showing only divisions of current user organization",
      caption: "division",
      dataField: "division",
      lookup: {
        valueExpr: "id",   // valueExpr has to be string, not function
        displayExpr: "display_name",
        dataSource: {
          store: new DevExpress.data.CustomStore({
            key: "id",
            load: () => {
              return $.getJSON($('div.dataAttendees').data('divisions-endpoint'));
            },
          }),
        },
      },
    },
  ],

  otherAttendeesColumns: [
    {
      caption: "Attendance",
      allowSorting: false,
      allowHeaderFiltering: false,
      cellTemplate: (container, rowData) => {
        const attrs = {
          "class": "text-info",
          "text": "Attendances",
          "href": Attendees.dataAttendees.familyAttendancesUrn + rowData.data.id,
        };
        $($('<a>', attrs)).appendTo(container);
      },
    },

    {
      caption: "Phone",
      dataField: "infos.contacts",
      name: 'infos.contacts.phones',
      allowSorting: false,
      dataType: "string",
      allowHeaderFiltering: false,
      cellTemplate: (container, rowData) => {
        const phones = [];
        if (rowData.data.infos.contacts.phone1) phones.push(rowData.data.infos.contacts.phone1);
        if (rowData.data.infos.contacts.phone2) phones.push(rowData.data.infos.contacts.phone2);
        const attrs = {
          "class": "text-info",
          "text": phones.join(', '),
        };
        $($('<span>', attrs)).appendTo(container);
      },
    },
    {
      caption: 'Email',
      dataField: 'infos.contacts',
      name: 'infos.contacts.emails',
      allowSorting: false,
      dataType: 'string',
      allowHeaderFiltering: false,
      cellTemplate: (container, rowData) => {
        const emails = [];
        if (rowData.data.infos.contacts.email1) emails.push(rowData.data.infos.contacts.email1);
        if (rowData.data.infos.contacts.email2) emails.push(rowData.data.infos.contacts.email2);
        const attrs = {
          class: 'text-info',
          text: emails.join(', '),
        };
        $($('<span>', attrs)).appendTo(container);
      },
    },
  ],

  setMeetsColumns: (availableMeets = JSON.parse(document.querySelector('div.dataAttendees').dataset.availableMeets)) => {
    const meetColumns=[];
    // const availableMeets = JSON.parse(document.querySelector('div.dataAttendees').dataset.availableMeets); // $('div.attendings').data('available-meets');

    availableMeets.forEach(meet => {
      meetColumns.push({
        visible: meet.id > 0,
        caption: meet.display_name,
        dataField: meet.slug,
        allowHeaderFiltering: false,
        calculateCellValue: (rowData) => {
          if (rowData.attendingmeets && rowData.attendingmeets.includes(meet.slug)) {
            return meet.display_name;
          }else{
            return '-';
          }
        }
      })
    });

    Attendees.dataAttendees.dataGridOpts['columns']=[...Attendees.dataAttendees.initialAttendeesColumns, ...meetColumns, ...Attendees.dataAttendees.otherAttendeesColumns]
  },
};

$(document).ready(() => {
  Attendees.dataAttendees.init();
});
