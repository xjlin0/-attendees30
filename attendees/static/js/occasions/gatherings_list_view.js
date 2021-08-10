Attendees.gatherings = {
  filtersForm: null,
  meetTagbox: null,
  editingSwitch: null,
  init: () => {
    console.log('static/js/occasions/gatherings_list_view.js');
    Attendees.gatherings.initEditingSwitch();
    Attendees.gatherings.initFiltersForm();
    // Attendees.gatherings.initListeners();
  },

  // initListeners: () => {},

  initEditingSwitch: () => {
    $('div#custom-control-edit-checkbox').dxSwitch({
      value: Attendees.utilities.editingEnabled,
      switchedOffText: 'Editing disabled',
      switchedOnText: 'Editing enabled',
      hint: 'Toggle Editing mode',
      width: '60%',
      height: '110%',
      onValueChanged: (e) => {  // not reconfirm, it's already after change
        Attendees.utilities.editingEnabled = e.value;
        Attendees.gatherings.toggleEditing(e.value);
      },
    })
  },

  toggleEditing: (enabled) => {
    Attendees.gatherings.gatheringsDatagrid && Attendees.gatherings.gatheringsDatagrid.option('editing', Attendees.gatherings.gatheringEditingArgs(enabled));
    // if(enabled){
    // }else{
    // }
  },

  initFiltersForm: () => {
    $.ajaxSetup({
      headers: {
        'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value,
      }
    });
    Attendees.gatherings.filtersForm = $('form.filters-dxform').dxForm(Attendees.gatherings.filterFormConfigs).dxForm('instance');
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
          text: 'Filter from (mm/dd/yyyy)',
        },
        editorType: 'dxDateBox',
        editorOptions: {
          value: new Date(new Date().setHours(new Date().getHours() - 1)),
          type: 'datetime',
          onValueChanged: (e)=>{
            const meets = $('div.selected-meets select').val();
            if (meets.length) {
              Attendees.gatherings.gatheringsDatagrid.refresh();
            }
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
            const meets = $('div.selected-meets select').val();
            if (meets.length) {
              Attendees.gatherings.gatheringsDatagrid.refresh();
            }
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
                $.get($('form.filters-dxform').data('meets-endpoint-by-slug'), {
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
            return $.getJSON($('form.filters-dxform').data('gatherings-endpoint'), {
              meets: meets,
              start: new Date($('div.filter-from input')[1].value).toISOString(),
              finish: new Date($('div.filter-till input')[1].value).toISOString(),
            });
          }
        },
        byKey: (key) => {
          console.log("hi 73 here is key: ", key);
          const d = new $.Deferred();
          $.get($('form.filters-dxform').data('gatherings-endpoint') + key + '/')
            .done((result) => {
              d.resolve(result.data);
            });
          return d.promise();
        },
        update: (key, values) => {
          console.log("hi 182 here is values: ", values);
          return $.ajax({
            url: $('form.filters-dxform').data('gatherings-endpoint') + key + '/',
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
                  },
                }, 'success', 2000);
            },
          });
        },
        insert: function (c) {
          // const subject = {
          //   content_type: Attendees.datagridUpdate.attendeeAttrs.dataset.attendeeContenttypeId,
          //   object_id: Attendees.datagridUpdate.attendeeId,
          // };
          return $.ajax({
            url: $('form.filters-dxform').data('gatherings-endpoint'),
            method: 'POST',
            dataType: 'json',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify(values),  // ...subject}),
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
            url: $('form.filters-dxform').data('gatherings-endpoint') + key ,
            method: 'DELETE',
            success: (result) => {
              DevExpress.ui.notify(
                {
                  message: 'removed success',
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
    groupPanel: {
      visible: 'auto',
    },
    columnChooser: {
      enabled: true,
      mode: 'select',
    },
    // onRowUpdating: (rowData) => {
    // },
    columns: [
      {
        dataField: 'meet',
        validationRules: [{type: 'required'}],
        lookup: {
          valueExpr: 'id',
          displayExpr: 'display_name',
          dataSource: {
            store: new DevExpress.data.CustomStore({
              key: 'id',
              load: () => $.getJSON($('form.filters-dxform').data('meets-endpoint-by-id')),
              byKey: (key) => {
                console.log("hi 281 here is key: ", key);
                return $.getJSON($('form.filters-dxform').data('meets-endpoint-by-id') + key + '/');},
            }),
          },
        },
      },
      {
        dataField: 'gathering_label',
        // helpText: 'label, not editable',
        readOnly: true,
      },
      {
        dataField: 'site',
        caption: 'Location',
      },
      {
        dataField: 'start',
        caption: 'Start (12hr@browser timezone)',
        validationRules: [{type: 'required'}],
        dataType: 'datetime',
        format: 'longDateLongTime',
        editorOptions: {
          type: 'datetime',
          dateSerializationFormat: 'yyyy-MM-ddTHH:mm:ss',
        },
      },
      {
        dataField: 'finish',
        visible: false,
        caption: 'End at',
        validationRules: [{type: 'required'}],
        dataType: 'datetime',
        format: 'longDateLongTime',
        editorOptions: {
          type: 'datetime',
          dateSerializationFormat: 'yyyy-MM-ddTHH:mm:ss',
        },
      },
      {
        dataField: 'display_name',
        // helpText: 'meet name + date',
        visible: false,
      },
      {
        dataField: 'site_type',
        visible: false,
      },
      {
        dataField: 'site_id',
        visible: false,
      },
    ],
  },

  gatheringEditingArgs: (enabled) => {
    return {
      allowUpdating: enabled,
      allowAdding: enabled,
      allowDeleting: enabled,
      texts: {
        confirmDeleteMessage: 'Are you sure to delete it and all its attendances? Instead, setting the "finish" date is usually enough!',
      },
      mode: 'popup',
      popup: {
        showTitle: true,
        title: 'Editing Gathering',
      },
      form: {
        items: [
          {
            dataField: 'display_name',
          },
          {
            // colSpan: 2,
            dataField: 'meet',
          },
          {
            dataField: 'gathering_label',
            disabled: true,
            helpText: 'not editable',
          },
          {
            dataField: 'start',
          },
          {
            dataField: 'finish',
          },
          {
            dataField: 'site',
            caption: 'Location',
            colSpan: 2,
          },
          // {
          //   dataField: 'site_type',
          // },
          // {
          //   dataField: 'site_id',
          // },
        ],
      },
    };
  },
};

$(document).ready(() => {
  Attendees.gatherings.init();
});
