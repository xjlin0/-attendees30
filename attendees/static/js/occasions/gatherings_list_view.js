Attendees.gatherings = {
  filtersForm: null,
  meetTagbox: null,
  init: () => {
    console.log('static/js/occasions/gatherings_list_view.js');
    Attendees.gatherings.initFiltersForm();
    Attendees.gatherings.initFilteredGatheringsDatagrid();
    Attendees.gatherings.initListeners();
  },
  initListeners: () => {},
  initFiltersForm: () => {
    console.log('11 initFiltersForm');
    Attendees.gatherings.filtersForm = $('div.filters-dxform').dxForm(Attendees.gatherings.filterFormConfigs).dxForm('instance');
  },
  filterFormConfigs: {
    dataSource: null,
    colCount: 12,
    itemType: 'group',
    items: [
      {
        // name: 'filter-from',
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
          // dateSerializationFormat: 'yyyy-MM-ddTHH:mm:ss',
        },
      },
      {
        // name: 'filter-till',
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
          // dateSerializationFormat: 'yyyy-MM-ddTHH:mm:ss',
        },
      },
      {
        dataField: 'meets',
        colSpan: 6,
        validationRules: [{type: 'required'}],
        label: {
          location: 'top',
          text: 'Select activities(meets)',
        },
        editorType: 'dxTagBox',
        editorOptions: {
          valueExpr: 'id',
          displayExpr: 'display_name',
          showClearButton: true,
          grouped: true,
          dataSource: new DevExpress.data.DataSource({
            store: new DevExpress.data.CustomStore({
              key: 'id',
              load: (loadOptions) => {
                console.log("hi 70 here is loadOptions: ", loadOptions);
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
            key: 'id',
          }),
        },

        // editorOptions: {
        //   valueExpr: 'id',
        //   displayExpr: 'display_name',
        //   // grouped: true,
        //   dataSource: new DevExpress.data.DataSource({
        //     store: new DevExpress.data.CustomStore({
        //       key: 'id',
        //       load: () => $.getJSON($('div.filters-dxform').data('meets-endpoint')),
        //     }),
        //     key: 'id',
        //     group: 'assembly_name',
        //   }),
        // },
      },
    ],
  },
  initFilteredGatheringsDatagrid: () => {},
};

$(document).ready(() => {
  Attendees.gatherings.init();
});
