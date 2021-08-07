Attendees.gatherings = {
  filtersForm: null,
  meetTagbox: null,
  init: () => {
    console.log('static/js/occasions/gatherings_list_view.js');
    Attendees.gatherings.initFiltersForm();
    Attendees.gatherings.initListeners();
  },
  initListeners: () => {},
  initFiltersForm: () => {
    Attendees.gatherings.filtersForm = $('div.filters-dxform').dxForm(Attendees.gatherings.filterFormConfigs).dxForm('instance');
  },
  filterFormConfigs: {
    dataSource: null,
    colCount: 12,
    itemType: 'group',
    items: [
      {
        colSpan: 3,
        cssClass: 'filter-from',
        validationRules: [{type: 'required'}],
        label: {
          location: 'top',
          text: 'Filter from',
        },
        editorType: 'dxDateBox',
        editorOptions: {
          value: new Date(new Date().setHours(new Date().getHours() - 1)),
          type: 'datetime',
          onValueChanged: (e)=>{
            Attendees.gatherings.gatheringsDatagrid.refresh();
          },
        },
      },
      {
        colSpan: 3,
        cssClass: 'filter-till',
        validationRules: [{type: 'required'}],
        label: {
          location: 'top',
          text: 'Filter till(exclude)',
        },
        editorType: 'dxDateBox',
        editorOptions: {
          value: new Date(new Date().setMonth(new Date().getMonth() + 1)),
          type: 'datetime',
          onValueChanged: (e)=>{
            Attendees.gatherings.gatheringsDatagrid.refresh();
          },
        },
      },
      {
        dataField: 'meets',
        colSpan: 6,
        cssClass: 'selected-meets',
        validationRules: [{type: 'required'}],
        label: {
          location: 'top',
          text: 'Select activities(meets)',
        },
        editorType: 'dxTagBox',
        editorOptions: {
          valueExpr: 'slug',
          displayExpr: 'display_name',
          showClearButton: true,
          searchEnabled: false,
          grouped: true,
          onValueChanged: (e)=>{
            Attendees.gatherings.gatheringsDatagrid.refresh();
          },
          dataSource: new DevExpress.data.DataSource({
            store: new DevExpress.data.CustomStore({
              key: 'slug',
              load: (loadOptions) => {
                const d = new $.Deferred();
                $.get($('div.filters-dxform').data('meets-endpoint'), {
                  start: new Date($('div.filter-from input')[1].value).toISOString(),
                  finish: new Date($('div.filter-till input')[1].value).toISOString(),
                })
                  .done((result) => {
                    const answer={};
                    if (result.data[0] && result.data[0].assembly_name){
                      result.data.forEach(meet=>{
                        if (meet.assembly_name){
                          answer[meet.assembly_name] = answer[meet.assembly_name] || {key: meet.assembly_name, items:[]};
                          answer[meet.assembly_name].items.push(meet);
                        }
                      })
                    }
                    d.resolve(Object.values(answer));
                  });
                return d.promise();
              },
            }),  // specify group didn't work, so regroup manually :(
            key: 'slug',
          }),
        },
      },
      {
        colSpan: 12,
        dataField: "filtered_gathering_set",
        label: {
          location: 'top',
          text: ' ',  // empty space required for removing label
          showColon: false,
        },
        template: (data, itemElement) => {
          Attendees.gatherings.gatheringsDatagrid = Attendees.gatherings.initFilteredGatheringsDatagrid(data, itemElement);
        },
      },
    ],
  },

  initFilteredGatheringsDatagrid: (data, itemElement) => {
    const $gatheringDatagrid = $("<div id='gatherings-datagrid-container'>").dxDataGrid(Attendees.gatherings.gatheringDatagridConfig);
    itemElement.append($gatheringDatagrid);
    return $gatheringDatagrid.dxDataGrid('instance');
  },

  gatheringDatagridConfig: {
    dataSource: {
      store: new DevExpress.data.CustomStore({
        key: 'id',
        load: () => {
          const meets = $('div.selected-meets select').val();
          if (meets.length) {
            return $.getJSON($('div.filters-dxform').data('gatherings-endpoint'), {
              meets: meets,
              start: new Date($('div.filter-from input')[1].value).toISOString(),
              finish: new Date($('div.filter-till input')[1].value).toISOString(),
            });
          }
        },
        // byKey: (key) => {
          // const d = new $.Deferred();
          // $.get(Attendees.datagridUpdate.attendeeAttrs.dataset.pastsEndpoint + key + '/')
          //   .done((result) => {
          //     d.resolve(result.data);
          //   });
          // return d.promise();
        // },
        // update: (key, values) => {
          // return $.ajax({
          //   url: Attendees.datagridUpdate.attendeeAttrs.dataset.pastsEndpoint + key + '/?' + $.param({category__type: args.type}),
          //   method: 'PATCH',
          //   dataType: 'json',
          //   contentType: 'application/json; charset=utf-8',
          //   data: JSON.stringify(values),
          //   success: (result) => {
          //     DevExpress.ui.notify(
          //       {
          //         message: 'update ' + args.type + ' success',
          //         width: 500,
          //         position: {
          //           my: 'center',
          //           at: 'center',
          //           of: window,
          //         },
          //       }, 'success', 2000);
          //   },
          // });
        // },
        // insert: function (values) {
          // const subject = {
          //   content_type: Attendees.datagridUpdate.attendeeAttrs.dataset.attendeeContenttypeId,
          //   object_id: Attendees.datagridUpdate.attendeeId,
          // };
          // return $.ajax({
          //   url: Attendees.datagridUpdate.attendeeAttrs.dataset.pastsEndpoint,
          //   method: 'POST',
          //   dataType: 'json',
          //   contentType: 'application/json; charset=utf-8',
          //   data: JSON.stringify({...values, ...subject}),
          //   success: (result) => {
          //     DevExpress.ui.notify(
          //       {
          //         message: 'Create ' + args.type + ' success',
          //         width: 500,
          //         position: {
          //           my: 'center',
          //           at: 'center',
          //           of: window,
          //         },
          //       }, 'success', 2000);
          //   },
          // });
        // },
        // remove: (key) => {
          // return $.ajax({
          //   url: Attendees.datagridUpdate.attendeeAttrs.dataset.pastsEndpoint + key + '/?' + $.param({category__type: args.type}),
          //   method: 'DELETE',
          //   success: (result) => {
          //     DevExpress.ui.notify(
          //       {
          //         message: 'removed '+ args.type +' success',
          //         width: 500,
          //         position: {
          //           my: 'center',
          //           at: 'center',
          //           of: window,
          //         },
          //       }, 'info', 2000);
          //   },
          // });
        // },
      }),
    },
    // onRowInserting: (rowData) => {
    // },
    // onInitNewRow: (e) => {
    // },
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
    // onRowUpdating: (rowData) => {
    // },
    columns: [
      {
        dataField: 'meet',
      },
      {
        dataField: 'gathering_label',
      },
      {
        dataField: 'site',
        caption: 'Location',
      },
      {
        dataField: 'start',
        caption: 'Start (12hr@your timezone)',
        validationRules: [{type: 'required'}],
        dataType: 'datetime',
        format: 'longDateLongTime',
        editorOptions: {
          type: 'datetime',
          dateSerializationFormat: 'yyyy-MM-ddTHH:mm:ss',
        },
      },
    ],
  },
};

$(document).ready(() => {
  Attendees.gatherings.init();
});
