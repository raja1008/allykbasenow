$(function()
{
    var dataGrid_Event, dataGrid_EventTemplate, dataGrid_Feedback, dataGrid_Goal, ds_templateeventlist, ds_eventlist, ds_event_objectiveslist, ds_event_categorylist, ds_feedbacknote, ds_feedbackgrid, ds_gallery, ds_goallist, ds_categorylist, ds_grid_categorylist, ds_objective, goal_RowKey=-1, daybegin_value, dayend_value, OnloadInitial=1, Redirect_Home = 0, Reload_Eventlist=0, Reload_Feedbackgrid = 0, Reload_EventTemplate=0, Reload_GoalCategorylist=0, Reload_Grid_Categorylist=0, Reload_Weekday=0 , OnEditRowId =0, OnEditEventTemplateRowId =0, OnEditNoteRowId =0, OnEditCategoryRowId=0, OnEditGoalRowId=0, OnEditObjectiveRowId = 0, global_eventlistidcollection = "", global_templatelistidcollection ="", uploadUrl, IsWeeklyEventTemplate=0;
    var user_TimeZone = moment.tz.guess();
    // var user_TimeZone = "America/Toronto";
    var ds_weekdaylist = [{
            "ID": 1,
            "DayName": "Monday"
        }, {
            "ID": 2,
            "DayName": "Tuesday"
        }, {
            "ID": 3,
            "DayName": "Wednesday"
        }, {
            "ID": 4,
            "DayName": "Thursday"
        }, {
            "ID": 5,
            "DayName": "Friday"
        }, {
            "ID": 6,
            "DayName": "Saturday"
        }, {
            "ID": 7,
            "DayName": "Sunday"
        }];

    var daybegin = $("#daybegin").dxDateBox({
        type: "datetime",
        pickerType: "rollers",
        showClearButton: true,
        value: moment().startOf('day'),
        onValueChanged: function (e)
        {
            dayend.option("min", e.value);
        }
    }).dxDateBox("instance");
    var dayend = $("#dayend").dxDateBox({
        type: "datetime",
        pickerType: "rollers",
        showClearButton: true,
        value: moment().endOf('day'),
        onValueChanged: function (e)
        {
            daybegin.option("max", e.value);
        }
    }).dxDateBox("instance");

    $("#btnLoadEvents").dxButton
    ({
        text: "Load Events",
        type: "default",
        onClick: LoadEvents
    });
    function LoadEvents()
    {
        if($("#grid-container-feedback").is(":visible"))
            $("#grid-container-feedback").toggle("slow");
        //*** Day Begin -- BEGIN ---
        let pre_daybegin =new Date($("#daybegin").dxDateBox("option", "value"));
        let pre_daybegin_formatted = moment(pre_daybegin).format("YYYY-MM-DD HH:mm:ss");
        let pre_daybegin_formatted_zone = moment.tz(pre_daybegin_formatted, user_TimeZone);
        let daybegin = moment.utc(pre_daybegin_formatted_zone.format()).format();
        //*** Day Begin -- END ---
        //*** Day End -- BEGIN ---
        let pre_dayend =new Date($("#dayend").dxDateBox("option", "value"));
        let pre_dayend_formatted = moment(pre_dayend).format("YYYY-MM-DD HH:mm:ss");
        let  pre_dayend_formatted_zone = moment.tz(pre_dayend_formatted, user_TimeZone);
        let dayend = moment.utc(pre_dayend_formatted_zone.format()).format();
        //*** Day End -- END ---
        let geteventlist_jsondata =
        {
            "daybegin" : daybegin,
            "dayend" : dayend,
        };
        $.ajax({
            url: "http://127.0.0.1:8001/geteventlist",
            type: "POST",
            data: JSON.stringify(geteventlist_jsondata),
            contentType: "application/json;charset=UTF-8",
            dataType: "json",
            success: function (data)
            {
                if (data.loginstatus == 0)
                    Redirect_Home =1;
                else
                {
                    ds_event_objectiveslist = data.event_objectiveslist;
                    ds_event_categorylist = data.event_categorylist;
                    ds_eventlist = data.eventlist;
                    Reload_Eventlist = 1;
                }
            },
            error: function (response)
            {
                return console.error(response);
            }
        });
    }

// --- setEventGrid --- BEGIN --
    function setEventGrid()
    {
        global_eventlistidcollection = ""; //used only when eventlist grid is loaded or about to load.
        $("#grid-container-events").dxDataGrid({
            dataSource: ds_eventlist,
            keyExpr: "eventlist_id",
            /*scrolling:
                {
                    mode: 'infinite'
                },*/
            paging:
                {pageSize: 7},
            pager:
                {
                    showInfo: true,
                    showNavigationButtons: true
                },
            editing:
                {
                    mode: "form",
                    allowUpdating: true,
                    allowAdding: true,
                    allowDeleting: true
                },
            loadPanel:
                {
                    enabled: true
                },
            selection:
                {
                    mode: "multiple",
                    deferred: true
                },
            wordWrapEnabled: true,
            filterRow:
                {visible: true},
            onInitialized: function (e) {
                dataGrid_Event = e.component;
            },
            columns:
                [
                    {
                        dataField: "eventlist_id",
                        visible: false,
                        allowEditing: false
                    },
                    {
                        dataField: "event_description",
                        caption: "Todo Event"
                    },
                    {
                        dataField: "starttime",
                        dataType: "datetime",
                        caption: "Start Time"
                    },
                    {
                        dataField: "expectfinishtime",
                        dataType: "datetime",
                        caption: "Expected Finish Time"
                    },
                    {
                        dataField: "objectiveid",
                        caption: "Goal-Objective",
                        lookup:
                            {
                                dataSource: ds_event_objectiveslist,
                                displayExpr: "event_objectivename",
                                valueExpr: "objectiveid"
                            }
                    },
                    {
                        dataField: "categoryid",
                        caption: "Category",
                        lookup:
                            {
                                dataSource: ds_event_categorylist,
                                displayExpr: "event_categoryname",
                                valueExpr: "categoryid"
                            }
                    },
                    {
                        dataField: "eventcompletedstatus",
                        dataType: "boolean",
                        caption: "Completed Status"
                    }
                ]
            , masterDetail:
                {
                    enabled: true,
                    template: function (container, info) {
                        let getfeedbacknote_jsondata =
                            {
                                "eventlist_id": info.data.eventlist_id.toString().trim(),
                            };
                        $.ajax({
                            url: "http://127.0.0.1:8001/getfeedbacknote",
                            type: "POST",
                            data: JSON.stringify(getfeedbacknote_jsondata),
                            contentType: "application/json;charset=UTF-8",
                            dataType: "json",
                            success: function (data)
                            {
                                    if (data.loginstatus == 0)
                                        Redirect_Home =1;
                                    else
                                        {
                                            ds_feedbacknote = data;
                                        }
                            },
                            error: function (response) {
                                return console.error(response);
                            },
                            complete: function (data) {
                                // console.log('ajax completed');
                                $("<div>")
                                    .addClass("master-detail-caption")
                                    .text("Add [only one] feedback note for " + info.data.event_description + ".")
                                    .appendTo(container);

                                $("<div>")
                                    .dxDataGrid({
                                        dataSource: ds_feedbacknote,
                                        keyExpr: "feedback_id",
                                        columnAutoWidth: true,
                                        showBorders: false,
                                        editing:
                                            {
                                                mode: "row",
                                                allowUpdating: true,
                                                allowAdding: true,
                                                allowDeleting: true
                                            },
                                        selection:
                                            {
                                                mode: "single"
                                            },
                                        wordWrapEnabled: true,
                                        filterRow:
                                            {visible: false},
                                        columns:
                                            [
                                                {
                                                    dataField: "feedback_id",
                                                    visible: false,
                                                    allowEditing: false
                                                },
                                                {
                                                    dataField: "eventlistid",
                                                    visible: false,
                                                    allowEditing: false
                                                },
                                                {
                                                    dataField: "feedbacknote",
                                                    caption: "Feedback Note"
                                                }
                                            ]
                                        , onInitNewRow: function (e) {
                                            if (ds_feedbacknote.length >= 1) window.location.reload();
                                        }
                                        , onRowInserting: function (e) {
                                            let insertnote_jsondata =
                                                {
                                                    "eventlistid": " " + info.data.eventlist_id.toString().trim() + " ",
                                                    "feedbacknote": " " + e.data.feedbacknote.toString().trim() + " ",
                                                };
                                            $.ajax({
                                                url: "http://127.0.0.1:8001/insertfeedbacknote",
                                                type: "POST",
                                                data: JSON.stringify(insertnote_jsondata),
                                                contentType: "application/json;charset=UTF-8",
                                                dataType: "json",
                                                success: function (data) {
                                                    //console.log(data);
                                                },
                                                error: function (response) {
                                                    return console.error(response);
                                                }
                                            });
                                        }
                                        , onEditingStart: function (e) {
                                            //alert("EditingStart");
                                            OnEditNoteRowId = e.data.feedback_id;
                                        }
                                        , onRowUpdating: function (e) {
                                            //alert("RowUpdating");
                                            let feedbacknote = "";
                                            if (e.newData.feedbacknote) feedbacknote = e.newData.feedbacknote.toString().trim();
                                            let updatenote_jsondata =
                                                {
                                                    "eventlistid": " " + info.data.eventlist_id.toString().trim() + " ",
                                                    "feedbacknote": " " + feedbacknote.toString().trim() + " ",
                                                };
                                            $.ajax({
                                                url: "http://127.0.0.1:8001/updatefeedbacknote",
                                                type: "POST",
                                                data: JSON.stringify(updatenote_jsondata),
                                                contentType: "application/json;charset=UTF-8",
                                                dataType: "json",
                                                success: function (data) {
                                                    //console.log(data);
                                                },
                                                error: function (response) {
                                                    return console.error(response);
                                                }
                                            });
                                            OnEditNoteRowId = 0;
                                        }
                                        , onRowRemoving: function (e) {
                                            //alert("RowRemoving");
                                            var removenote_jsondata =
                                                {
                                                    "eventlistid": " " + info.data.eventlist_id.toString().trim() + " "
                                                };
                                            $.ajax({
                                                url: "http://127.0.0.1:8001/removefeedbacknote",
                                                type: "POST",
                                                data: JSON.stringify(removenote_jsondata),
                                                contentType: "application/json;charset=UTF-8",
                                                dataType: "json",
                                                success: function (data) {
                                                    // console.log(data);
                                                },
                                                error: function (response) {
                                                    return console.error(response);
                                                }
                                            });
                                        }
                                    }).appendTo(container);
                            }
                        });

                    }
                }
            , onRowInserting: function (e) {
                // alert("RowInserting change");
                //*** Start time -- BEGIN ---
                let pre_starttime = new Date(e.data.starttime);
                let pre_starttime_formatted = moment(pre_starttime).format("YYYY-MM-DD HH:mm:ss");
                let  pre_starttime_formatted_zone = moment.tz(pre_starttime_formatted, user_TimeZone);
                let starttime = moment.utc(pre_starttime_formatted_zone.format()).format();
                //*** Start time -- END ---
                //*** End time -- BEGIN ---
                let pre_expectfinishtime = new Date(e.data.expectfinishtime);
                let pre_expectfinishtime_formatted = moment(pre_expectfinishtime).format("YYYY-MM-DD HH:mm:ss");
                let  pre_expectfinishtime_formatted_zone = moment.tz(pre_expectfinishtime_formatted, user_TimeZone);
                let expectfinishtime = moment.utc(pre_expectfinishtime_formatted_zone.format()).format();
                //*** End time -- END ---
                //*** Day Begin -- BEGIN ---
                let pre_daybegin =new Date($("#daybegin").dxDateBox("option", "value"));
                let pre_daybegin_formatted = moment(pre_daybegin).format("YYYY-MM-DD HH:mm:ss");
                let  pre_daybegin_formatted_zone = moment.tz(pre_daybegin_formatted, user_TimeZone);
                let daybegin = moment.utc(pre_daybegin_formatted_zone.format()).format();
                //*** Day Begin -- END ---
                //*** Day End -- BEGIN ---
                let pre_dayend =new Date($("#dayend").dxDateBox("option", "value"));
                let pre_dayend_formatted = moment(pre_dayend).format("YYYY-MM-DD HH:mm:ss");
                let  pre_dayend_formatted_zone = moment.tz(pre_dayend_formatted, user_TimeZone);
                let dayend = moment.utc(pre_dayend_formatted_zone.format()).format();
                //*** Day End -- END ---

                 // alert(e.data.event_description + starttime.toString() + expectfinishtime.toString() + e.data.objectiveid + e.data.categoryid);
                let insert_jsondata =
                    {
                        "event_description": " " + e.data.event_description.toString().trim() + " ",
                        "starttime": " " + starttime + " ",
                        "expectfinishtime": " " + expectfinishtime + " ",
                        "objectiveid": " " + e.data.objectiveid + " ",
                        "categoryid": " " + e.data.categoryid + " ",
                        "daybegin" : " " + daybegin + " ",
                        "dayend" : " " + dayend + " ",
                    };
                $.ajax({
                    url: "http://127.0.0.1:8001/inserteventslist",
                    type: "POST",
                    data: JSON.stringify(insert_jsondata),
                    contentType: "application/json;charset=UTF-8",
                    dataType: "json",
                    success: function (data) {
                        if (data.loginstatus == 0)
                            Redirect_Home =1;
                        else {
                            ds_eventlist = data;
                            Reload_Eventlist = 1;
                        }
                    },
                    error: function (response) {
                        return console.error(response);
                    }
                });
            }
            , onRowInserted: function (e) {
                //alert("RowInserted");
            }
            , onEditingStart: function (e) {
                // alert("EditingStart");
                OnEditRowId = e.data.eventlist_id;
            }
            , onRowUpdating: function (e) {
                // alert("RowUpdating");
                var event_description = "", starttime, expectfinishtime, eventcompletedstatus, objectiveid = "", categoryid = "";
                if (e.newData.event_description) event_description = e.newData.event_description;
                if (e.newData.starttime) {
                    //*** Start time -- BEGIN ---
                        let pre_starttime = new Date(e.newData.starttime);
                        let pre_starttime_formatted = moment(pre_starttime).format("YYYY-MM-DD HH:mm:ss");
                        let pre_starttime_formatted_zone = moment.tz(pre_starttime_formatted, user_TimeZone);
                        starttime = moment.utc(pre_starttime_formatted_zone.format()).format();
                    //*** Start time -- END ---
                } else {
                    starttime = "";
                }
                if (e.newData.expectfinishtime) {
                    //*** End time -- BEGIN ---
                        let pre_expectfinishtime = new Date(e.newData.expectfinishtime);
                        let pre_expectfinishtime_formatted = moment(pre_expectfinishtime).format("YYYY-MM-DD HH:mm:ss");
                        let  pre_expectfinishtime_formatted_zone = moment.tz(pre_expectfinishtime_formatted, user_TimeZone);
                        expectfinishtime = moment.utc(pre_expectfinishtime_formatted_zone.format()).format();
                    //*** End time -- END ---
                } else {
                    expectfinishtime = "";
                }
                if (e.newData.eventcompletedstatus === true || e.newData.eventcompletedstatus === false) {
                    eventcompletedstatus = Boolean(false);
                    eventcompletedstatus = e.newData.eventcompletedstatus;
                }
                else
                    eventcompletedstatus = "undefined";
                // alert(e.newData.eventcompletedstatus);
                if (e.newData.objectiveid) objectiveid = e.newData.objectiveid;
                if (e.newData.categoryid) categoryid = e.newData.categoryid;
                //*** Day Begin -- BEGIN ---
                let pre_daybegin =new Date($("#daybegin").dxDateBox("option", "value"));
                let pre_daybegin_formatted = moment(pre_daybegin).format("YYYY-MM-DD HH:mm:ss");
                let  pre_daybegin_formatted_zone = moment.tz(pre_daybegin_formatted, user_TimeZone);
                let daybegin = moment.utc(pre_daybegin_formatted_zone.format()).format();
                //*** Day Begin -- END ---
                //*** Day End -- BEGIN ---
                let pre_dayend =new Date($("#dayend").dxDateBox("option", "value"));
                let pre_dayend_formatted = moment(pre_dayend).format("YYYY-MM-DD HH:mm:ss");
                let  pre_dayend_formatted_zone = moment.tz(pre_dayend_formatted, user_TimeZone);
                let dayend = moment.utc(pre_dayend_formatted_zone.format()).format();
                //*** Day End -- END ---
                //alert(OnEditRowId.toString().trim() + event_description.toString().trim() + starttime + expectfinishtime + objectiveid.toString().trim());
                let update_jsondata =
                    {
                        "eventlist_id": " " + OnEditRowId.toString().trim() + " ",
                        "event_description": " " + event_description.toString().trim() + " ",
                        "starttime": " " + starttime + " ",
                        "expectfinishtime": " " + expectfinishtime + " ",
                        "eventcompletedstatus": " " + eventcompletedstatus + " ",
                        "objectiveid": " " + objectiveid.toString().trim() + " ",
                        "categoryid": " " + categoryid.toString().trim() + " ",
                        "daybegin" : daybegin,
                        "dayend" : dayend,
                    };
                $.ajax({
                    url: "http://127.0.0.1:8001/updateeventslist",
                    type: "PUT",
                    data: JSON.stringify(update_jsondata),
                    contentType: "application/json;charset=UTF-8",
                    dataType: "json",
                    success: function (data) {
                        if (data.loginstatus == 0)
                            Redirect_Home =1;
                        else {
                            ds_eventlist = data;
                            Reload_Eventlist = 1;
                        }
                    },
                    error: function (response) {
                        return console.error(response);
                    }
                });
                OnEditRowId = 0;
            }
            , onRowUpdated: function (e) {
                // alert("RowUpdated");
            }
            , onRowRemoving: function (e) {
                // alert("RowRemoving");
                //*** Day Begin -- BEGIN ---
                let pre_daybegin =new Date($("#daybegin").dxDateBox("option", "value"));
                let pre_daybegin_formatted = moment(pre_daybegin).format("YYYY-MM-DD HH:mm:ss");
                let  pre_daybegin_formatted_zone = moment.tz(pre_daybegin_formatted, user_TimeZone);
                let daybegin = moment.utc(pre_daybegin_formatted_zone.format()).format();
                //*** Day Begin -- END ---
                //*** Day End -- BEGIN ---
                let pre_dayend =new Date($("#dayend").dxDateBox("option", "value"));
                let pre_dayend_formatted = moment(pre_dayend).format("YYYY-MM-DD HH:mm:ss");
                let  pre_dayend_formatted_zone = moment.tz(pre_dayend_formatted, user_TimeZone);
                let dayend = moment.utc(pre_dayend_formatted_zone.format()).format();
                //*** Day End -- END ---
                let remove_jsondata =
                    {
                        "eventlist_id": " " + e.data.eventlist_id + " ",
                        "daybegin" : daybegin,
                        "dayend" : dayend,
                    };
                $.ajax({
                    url: "http://127.0.0.1:8001/removeeventslist",
                    type: "PUT",
                    data: JSON.stringify(remove_jsondata),
                    contentType: "application/json;charset=UTF-8",
                    dataType: "json",
                    success: function (data) {
                        if (data.loginstatus == 0)
                            Redirect_Home =1;
                        else {
                            ds_eventlist = data;
                            Reload_Eventlist = 1;
                        }
                    },
                    error: function (response) {
                        return console.error(response);
                    }
                });
            }
            , onRowRemoved: function (e) {
                // alert("RowRemoved");
            }
            , onSelectionChanged: function (e) {
                GlobalEventlistidCollection_FileUploader();
            }
        }).dxDataGrid("instance");
    }
// --- setEventGrid --- END --
// ------------------------------------------------------------------ Event Template --------- BEGIN ---
     $("#btnEventTemplate").dxButton
    ({
        text: "Event Template",
        type: "normal",
        onClick: ManageEventTemplate
    });
    function ManageEventTemplate()
    {
        if ($("#grid-container-category").is(":visible")) $("#grid-container-category").toggle("slow");
        if ($("#grid-container-goalobjective").is(":visible")) $("#grid-container-goalobjective").toggle("slow");
        if($("#grid-container-feedback").is(":visible")) $("#grid-container-feedback").toggle("slow");

        $("#grid-container-templateevents").toggle("slow");
        $("#slbxEventTemplate").toggle("slow");
        $("#btnLoadTemplate").toggle("slow");
        $("#btnUpdateWeekday").toggle("slow");
        $("#btnInsertTemplate").toggle("slow");
    }
    $("#slbxEventTemplate").dxSelectBox({
        dataSource: ds_weekdaylist,
        displayExpr: "DayName",
        valueExpr: "ID",
        value: ds_weekdaylist[(moment().add(1, 'days').isoWeekday() > 7) ? 0 : (moment().add(1, 'days').isoWeekday()-1) ].ID,
    });

    $("#btnLoadTemplate").dxButton
    ({
        text: "Load Template",
        type: "default",
        onClick: LoadEventTemplate
    });

    function LoadEventTemplate()
    {
        // alert($("#slbxEventTemplate").dxSelectBox("option", "value"));
        let loadeventtemplate_jsondata =
        {
            "weekdayid" : $("#slbxEventTemplate").dxSelectBox("option", "value"),
        };
        $.ajax({
            url: "http://127.0.0.1:8001/loadeventtemplate",
            type: "POST",
            data: JSON.stringify(loadeventtemplate_jsondata),
            contentType: "application/json;charset=UTF-8",
            dataType: "json",
            success: function (data)
            {
                if (data.loginstatus == 0)
                    Redirect_Home =1;
                else
                {
                    ds_event_objectiveslist = data.event_objectiveslist;
                    ds_event_categorylist = data.event_categorylist;
                    ds_templateeventlist = data.templateeventlist;
                    Reload_EventTemplate= 1;
                }
            },
            error: function (response)
            {
                return console.error(response);
            }
        });
    }

    function setEventTemplateGrid()
    {
        let the_selected_weekday = $("#slbxEventTemplate").dxSelectBox("option", "value");
        $("#grid-container-templateevents").dxDataGrid({
            dataSource: ds_templateeventlist,
            keyExpr: "templatelist_id",
            paging:
                {pageSize: 7},
            pager:
                {
                    showInfo: true,
                    showNavigationButtons: true
                },
            editing:
                {
                    mode: "form",
                    allowUpdating: true,
                    allowAdding: true,
                    allowDeleting: true
                },
            loadPanel:
                {
                    enabled: true
                },
            selection:
                {
                    mode: "multiple",
                    deferred: true
                },
            wordWrapEnabled: true,
            filterRow:
                {visible: true},
            onInitialized: function (e) {
                dataGrid_EventTemplate = e.component;
            },
            columns:
                [
                    {
                        dataField: "templatelist_id",
                        visible: false,
                        allowEditing: false
                    },
                    {
                        dataField: "template_event_description",
                        caption: "Todo Event"
                    },
                    {
                        dataField: "template_starttime",
                        dataType: "datetime",
                        caption: "Start Time"
                        ,format: 'shortTime',
                        editorOptions: {
                                          type: "time",
                                          // pickerType: "rollers",
                                       },
                    },
                    {
                        dataField: "template_expectfinishtime",
                        dataType: "datetime",
                        caption: "Expected Finish Time"
                        ,format: 'shortTime',
                        editorOptions: {
                                          type: "time",
                                          // pickerType: "rollers",
                                       },
                    },
                    {
                        dataField: "template_objectiveid",
                        caption: "Goal-Objective",
                        lookup:
                            {
                                dataSource: ds_event_objectiveslist,
                                displayExpr: "event_objectivename",
                                valueExpr: "objectiveid"
                            }
                    },
                    {
                        dataField: "template_categoryid",
                        caption: "Category",
                        lookup:
                            {
                                dataSource: ds_event_categorylist,
                                displayExpr: "event_categoryname",
                                valueExpr: "categoryid"
                            }
                    }
                ]
            , onRowInserting: function (e) {
                //*** Template Start time -- BEGIN ---
                let pre_starttime =new Date(e.data.template_starttime);
                let template_starttime = moment(pre_starttime).format("YYYY-MM-DD HH:mm:ss");
                //*** Template Start time -- END ---
                //*** Template End time -- BEGIN ---
                let pre_expectfinishtime = new Date(e.data.template_expectfinishtime);
                let template_expectfinishtime =moment(pre_expectfinishtime).format("YYYY-MM-DD HH:mm:ss");
                //*** Template End time -- END ---
                let insert_jsondata =
                    {
                        "template_event_description": " " + e.data.template_event_description.toString().trim() + " ",
                        "template_starttime": " " + template_starttime + " ",
                        "template_expectfinishtime": " " + template_expectfinishtime + " ",
                        "template_objectiveid": " " + e.data.template_objectiveid + " ",
                        "template_categoryid": " " + e.data.template_categoryid + " ",
                        "template_weekdayid": " " + the_selected_weekday + " ",
                    };
                $.ajax({
                    url: "http://127.0.0.1:8001/inserttemplateevent",
                    type: "POST",
                    data: JSON.stringify(insert_jsondata),
                    contentType: "application/json;charset=UTF-8",
                    dataType: "json",
                    success: function (data) {
                        if (data.loginstatus == 0)
                            Redirect_Home =1;
                        else {
                            ds_templateeventlist = data.templateeventlist;
                            Reload_EventTemplate = 1;
                        }
                    },
                    error: function (response) {
                        return console.error(response);
                    }
                });
            }
            , onEditingStart: function (e) {
                OnEditEventTemplateRowId = e.data.templatelist_id;
                the_selected_weekday =  $("#slbxEventTemplate").dxSelectBox("option", "value");
            }
            , onRowUpdating: function (e) {
                var template_event_description = "", template_starttime = "", template_expectfinishtime = "", template_eventcompletedstatus, template_objectiveid = "", template_categoryid = "";
                if (e.newData.template_event_description) template_event_description = e.newData.template_event_description;
                if (e.newData.template_starttime) {
                    //*** Template Start time -- BEGIN ---
                    let pre_starttime = e.newData.template_starttime;
                    template_starttime =moment(pre_starttime).format("YYYY-MM-DD HH:mm:ss");
                    //*** Template Start time -- END ---
                } else
                    {
                        template_starttime = "";
                    }
                if (e.newData.template_expectfinishtime) {
                    //*** Template End time -- BEGIN ---
                    let pre_expectfinishtime = e.newData.template_expectfinishtime;
                    template_expectfinishtime =moment(pre_expectfinishtime).format("YYYY-MM-DD HH:mm:ss");
                    //*** Template End time -- END ---
                } else {
                    template_expectfinishtime = "";
                }
                if (e.newData.template_objectiveid) template_objectiveid = e.newData.template_objectiveid;
                if (e.newData.template_categoryid) template_categoryid = e.newData.template_categoryid;
                let update_jsondata =
                    {
                        "templatelist_id": " " + OnEditEventTemplateRowId.toString().trim() + " ",
                        "template_event_description": " " + template_event_description.toString().trim() + " ",
                        "template_starttime": " " + template_starttime.trim() + " ",
                        "template_expectfinishtime": " " + template_expectfinishtime.trim() + " ",
                        "template_objectiveid": " " + template_objectiveid.toString().trim() + " ",
                        "template_categoryid": " " + template_categoryid.toString().trim() + " ",
                        "template_weekdayid": " " + the_selected_weekday + " ",
                    };
                $.ajax({
                    url: "http://127.0.0.1:8001/updatetemplateevent",
                    type: "PUT",
                    data: JSON.stringify(update_jsondata),
                    contentType: "application/json;charset=UTF-8",
                    dataType: "json",
                    success: function (data) {
                        if (data.loginstatus == 0)
                            Redirect_Home =1;
                        else {
                            ds_templateeventlist = data.templateeventlist;
                            Reload_EventTemplate= 1;
                        }
                    },
                    error: function (response) {
                        return console.error(response);
                    }
                });
                OnEditEventTemplateRowId = 0;
            }
            , onRowRemoving: function (e) {
                let remove_jsondata =
                    {
                        "templatelist_id": " " + e.data.templatelist_id + " ",
                        "template_weekdayid" : the_selected_weekday,
                    };
                $.ajax({
                    url: "http://127.0.0.1:8001/removetemplateevent",
                    type: "PUT",
                    data: JSON.stringify(remove_jsondata),
                    contentType: "application/json;charset=UTF-8",
                    dataType: "json",
                    success: function (data) {
                        if (data.loginstatus == 0)
                            Redirect_Home =1;
                        else {
                            ds_templateeventlist = data.templateeventlist;
                            Reload_EventTemplate = 1;
                        }
                    },
                    error: function (response) {
                        return console.error(response);
                    }
                });
            }
            , onSelectionChanged: function (e) {
                GetSelectedTemplateEvents();
            }
        }).dxDataGrid("instance");
    }


    function GetSelectedTemplateEvents()
    {
        dataGrid_EventTemplate.getSelectedRowsData().then(function (TemplaterowData)
        {
            if(TemplaterowData.length <= 0) return;
            global_templatelistidcollection = "";
            for (let i = 0; i < TemplaterowData.length; i++)
                {
                    global_templatelistidcollection = global_templatelistidcollection + TemplaterowData[i].templatelist_id + "," ;
                }
                global_templatelistidcollection = global_templatelistidcollection.replace(/,(?=[^,]*$)/, '');
        });
    }


    $("#btnInsertTemplate").dxButton
    ({
        text: "Insert Template as Events",
        type: "normal",
        icon: "runner",
        onClick: BulkInsertEventTemplate
    });

    function BulkInsertEventTemplate()
    {
        let weekdayname = $("#slbxEventTemplate").dxSelectBox("option", "text");
        let pre_assigndate = moment().day(weekdayname).toDate();
        let assigndate = moment(pre_assigndate).format("YYYY-MM-DD");
        let bulkinserteventtemplate_jsondata =
        {
            "weekdayid" : $("#slbxEventTemplate").dxSelectBox("option", "value"),
            "assigndate" : assigndate,
            "user_TimeZone" : user_TimeZone,
        };
        $.ajax({
            url: "http://127.0.0.1:8001/bulkinserteventtemplate",
            type: "POST",
            data: JSON.stringify(bulkinserteventtemplate_jsondata),
            contentType: "application/json;charset=UTF-8",
            dataType: "json",
            success: function (data)
            {
                if (data.loginstatus == 0)
                    Redirect_Home =1;
                else
                {
                    ds_eventlist = data.eventlist;
                    Reload_Eventlist = 1;
                }
            },
            error: function (response)
            {
                return console.error(response);
            }
        });
    }

    $("#btnUpdateWeekday").dxButton({
    text: "Move record to selected day",
    type: "normal",
    icon: "preferences",
    onClick: TransferWeekday
    });

    function TransferWeekday()
    {
        if(global_templatelistidcollection <= 0) return;
        let bulkeventtemplateweekdayid_jsondata =
                {
                    "templatelistid_collection" : " "+ global_templatelistidcollection +" ",
                    "weekdayid" : $("#slbxEventTemplate").dxSelectBox("option", "value"),
                };
        $.ajax({
                url: "http://127.0.0.1:8001/bulkeventtemplateweekdayid",
                type: "PUT",
                data: JSON.stringify(bulkeventtemplateweekdayid_jsondata),
                contentType: "application/json;charset=UTF-8",
                dataType: "json",
                success: function(data)
                {
                    if (data.loginstatus == 0)
                        Redirect_Home =1;
                    else {
                        ds_templateeventlist = data.templateeventlist;
                        Reload_EventTemplate = 1;
                        DevExpress.ui.notify("Updated event completed status.");
                    }
                },
                error: function(response)
                {return console.error(response);}
               });
    }
// ------------------------------------------------------------------ Event Template --------- END ---
// ------------------------------------------------------------------ Category--------- BEGIN ---
    $("#btnCategory").dxButton
    ({
        text: "Category",
        type: "normal",
        onClick: CategoryGrid
    });
    function CategoryGrid()
    {
        $("#grid-container-category").toggle("slow", function()
        {
            if($("#grid-container-category").is(":visible"))
            {
                if($("#grid-container-goalobjective").is(":visible"))
                    $("#grid-container-goalobjective").toggle("slow");

                //Event Template Section --- BEGIN ---
                if($("#slbxEventTemplate").is(":visible"))
                    $("#slbxEventTemplate").toggle("slow");

                if($("#btnLoadTemplate").is(":visible"))
                    $("#btnLoadTemplate").toggle("slow");

                if($("#btnUpdateWeekday").is(":visible"))
                    $("#btnUpdateWeekday").toggle("slow");

                if($("#grid-container-templateevents").is(":visible"))
                    $("#grid-container-templateevents").toggle("slow");

                if($("#btnInsertTemplate").is(":visible"))
                    $("#btnInsertTemplate").toggle("slow");
                //Event Template Section --- END ---

                if($("#grid-container-feedback").is(":visible"))
                    $("#grid-container-feedback").toggle("slow");

                $.ajax({
                    url: "http://127.0.0.1:8001/get_grid_categorylist",
                    type: "GET",
                    contentType: "application/json;charset=UTF-8",
                    dataType: "json",
                    success: function (data) {
                        if (data.loginstatus == 0)
                            Redirect_Home =1;
                        else {
                            ds_grid_categorylist = data.categorylist;
                            Reload_Grid_Categorylist = 1;
                        }
                    },
                    error: function (response) {
                        return console.error(response);
                    }
                });
            }
        });
    }
    function setCategoryGrid()
    {
        $("#grid-container-category").dxDataGrid({
            dataSource: ds_grid_categorylist,
            keyExpr: "category_id",
            paging:
                {pageSize: 12},
            pager:
                {
                    showInfo: true,
                    showNavigationButtons: true
                },
            editing:
                {
                    mode: "form",
                    allowUpdating: true,
                    allowAdding: true,
                    allowDeleting: true
                },
            loadPanel:
                {
                    enabled: true
                },
            selection:
                {
                    mode: "single"
                },
            wordWrapEnabled: true,
            filterRow:
                {visible: true},
            onInitialized: function (e) {
                dataGrid_Goal = e.component;
            },
            columns:
                [
                    {
                        dataField: "category_id",
                        visible: false,
                        allowEditing: false
                    },
                    {
                        dataField: "category_name",
                        caption: "Category Name"
                    }
                ]
            , onRowInserting: function (e) {
                let insert_category_jsondata =
                    {
                        "category_name": " " + e.data.category_name.toString().trim() + " ",
                    };
                $.ajax({
                    url: "http://127.0.0.1:8001/insert_grid_category",
                    type: "POST",
                    data: JSON.stringify(insert_category_jsondata),
                    contentType: "application/json;charset=UTF-8",
                    dataType: "json",
                    success: function (data)
                    {
                        if (data.loginstatus == 0)
                            Redirect_Home =1;
                        else {
                            ds_grid_categorylist = data;
                            Reload_Grid_Categorylist = 1;
                        }
                    },
                    error: function (response) {
                        return console.error(response);
                    }
                });
            }
            , onEditingStart: function (e) {
                // alert("EditingStart");
                OnEditCategoryRowId = e.data.category_id;
            }
            , onRowUpdating: function (e) {
                // alert("RowUpdating");
                var category_name = "";

                if (e.newData.category_name) category_name = e.newData.category_name;
                let update_category_jsondata =
                    {
                        "category_id": " " + OnEditCategoryRowId.toString().trim() + " ",
                        "category_name": " " + category_name.toString().trim() + " ",
                    };
                //alert(JSON.stringify(update_goal_jsondata));
                $.ajax({
                    url: "http://127.0.0.1:8001/update_grid_category",
                    type: "PUT",
                    data: JSON.stringify(update_category_jsondata),
                    contentType: "application/json;charset=UTF-8",
                    dataType: "json",
                    success: function (data)
                    {
                        if (data.loginstatus == 0)
                            Redirect_Home =1;
                        else {
                            ds_grid_categorylist = data;
                            Reload_Grid_Categorylist = 1;
                        }
                    },
                    error: function (response) {
                        return console.error(response);
                    }
                });
                OnEditCategoryRowId = 0;
            }
            , onRowUpdated: function (e) {
                // alert("RowUpdated");
            }
            , onRowRemoving: function (e) {
                // alert("RowRemoving");
                let remove_category_jsondata =
                    {
                        "category_id": " " + e.data.category_id + " "
                    };
                $.ajax({
                    url: "http://127.0.0.1:8001/remove_grid_category",
                    type: "PUT",
                    data: JSON.stringify(remove_category_jsondata),
                    contentType: "application/json;charset=UTF-8",
                    dataType: "json",
                    success: function (data)
                    {
                        if (data.loginstatus == 0)
                            Redirect_Home =1;
                        else {
                            ds_grid_categorylist = data;
                            Reload_Grid_Categorylist = 1;
                        }
                    },
                    error: function (response) {
                        return console.error(response);
                    }
                });
            }
        }).dxDataGrid("instance");
    }
// ------------------------------------------------------------------ Category--------- END ---
// ------------------------------------------------------------------ Goals and Objectives --------- BEGIN ---
    $("#btnGoalsObjectives").dxButton
    ({
        text: "Goals and Objectives",
        type: "normal",
        onClick: GoalObjectiveGrid
    });
    function GoalObjectiveGrid()
    {
        $("#grid-container-goalobjective").toggle("slow", function()
        {
            if($("#grid-container-goalobjective").is(":visible"))
            {
                if($("#grid-container-category").is(":visible"))
                    $("#grid-container-category").toggle("slow");

                //Event Template Section --- BEGIN ---
                if($("#slbxEventTemplate").is(":visible"))
                    $("#slbxEventTemplate").toggle("slow");

                if($("#btnLoadTemplate").is(":visible"))
                    $("#btnLoadTemplate").toggle("slow");

                if($("#btnUpdateWeekday").is(":visible"))
                    $("#btnUpdateWeekday").toggle("slow");

                if($("#grid-container-templateevents").is(":visible"))
                    $("#grid-container-templateevents").toggle("slow");

                if($("#btnInsertTemplate").is(":visible"))
                    $("#btnInsertTemplate").toggle("slow");
                //Event Template Section --- END ---

                 if($("#grid-container-feedback").is(":visible"))
                     $("#grid-container-feedback").toggle("slow");

                $.ajax({
                    url: "http://127.0.0.1:8001/getgoalcategorylist",
                    type: "GET",
                    contentType: "application/json;charset=UTF-8",
                    dataType: "json",
                    success: function (data) {
                        if (data.loginstatus == 0)
                            Redirect_Home =1;
                        else {
                            ds_goallist = data.goallist;
                            ds_categorylist = data.categorylist;
                            Reload_GoalCategorylist = 1;
                        }
                    },
                    error: function (response) {
                        return console.error(response);
                    }
                });
            }
        });
    }
    function setGoalsObjectives()
    {
        $("#grid-container-goalobjective").dxDataGrid({
            dataSource: ds_goallist,
            keyExpr: "goal_id",
            /*scrolling:
                {
                    mode: 'infinite'
                },*/
            paging:
                {pageSize: 3},
            pager:
                {
                    showInfo: true,
                    showNavigationButtons: true
                },
            editing:
                {
                    mode: "form",
                    allowUpdating: true,
                    allowAdding: true,
                    allowDeleting: true
                },
            loadPanel:
                {
                    enabled: true
                },
            selection:
                {
                    mode: "single"
                },
            wordWrapEnabled: true,
            filterRow:
                {visible: true},
            onInitialized: function (e) {
                dataGrid_Goal = e.component;
            },
            columns:
                [
                    {
                        dataField: "goal_id",
                        visible: false,
                        allowEditing: false
                    },
                    {
                        dataField: "goal_name",
                        caption: "Goal Name"
                    },
                    {
                        dataField: "goal_description",
                        caption: "Goal Description"
                    },
                    {
                        dataField: "categoryid",
                        caption: "Category",
                        lookup:
                            {
                                dataSource: ds_categorylist,
                                displayExpr: "category_name",
                                valueExpr: "category_id"
                            }
                    },
                    {
                        dataField: "goalcompletedstatus",
                        dataType: "boolean",
                        caption: "Goal Status"
                    }
                ]
            , masterDetail:
                {
                    enabled: true,
                    template: function (container, info)
                    {
                        let getobjective_jsondata =
                            {
                                "goal_id": info.data.goal_id.toString().trim(),
                            };
                        $.ajax({
                            url: "http://127.0.0.1:8001/getobjectiveslist",
                            type: "POST",
                            data: JSON.stringify(getobjective_jsondata),
                            contentType: "application/json;charset=UTF-8",
                            dataType: "json",
                            success: function (data)
                            {
                                if (data.loginstatus == 0)
                                    Redirect_Home =1;
                                else {
                                    ds_objective = data;
                                }
                            },
                            error: function (response) {
                                return console.error(response);
                            },
                            complete: function (data)
                            {
                                $("<div>")
                                    .addClass("master-detail-caption")
                                    .text("Add Objective(s) for " + info.data.goal_name + ".")
                                    .appendTo(container);

                                $("<div>")
                                    .dxDataGrid({
                                        dataSource: ds_objective,
                                        keyExpr: "objective_id",
                                        columnAutoWidth: true,
                                        showBorders: false,
                                        editing:
                                            {
                                                mode: "row",
                                                allowUpdating: true,
                                                allowAdding: true,
                                                allowDeleting: true
                                            },
                                        selection:
                                            {
                                                mode: "single"
                                            },
                                        wordWrapEnabled: true,
                                        filterRow:
                                            {visible: false},
                                        columns:
                                            [
                                                {
                                                    dataField: "objective_id",
                                                    visible: false,
                                                    allowEditing: false
                                                },
                                                {
                                                    dataField: "objective_name",
                                                },
                                                {
                                                    dataField: "objective_description",
                                                    caption: "Objective Description"
                                                },
                                                {
                                                    dataField: "objectivecompletedstatus",
                                                    dataType: "boolean",
                                                    caption: "Objective Status"
                                                }
                                            ]
                                        , onInitNewRow: function (e) {

                                        }
                                        , onRowInserting: function (e) {
                                            let insertobjective_jsondata =
                                                {
                                                    "objective_name": " " + e.data.objective_name.toString().trim() + " ",
                                                    "objective_description": " " + e.data.objective_description.toString().trim() + " ",
                                                    "goalid": " " + info.data.goal_id.toString().trim() + " ",
                                                    "categoryid": " " + info.data.categoryid.toString().trim() + " ",
                                                };
                                            $.ajax({
                                                url: "http://127.0.0.1:8001/insertobjective",
                                                type: "POST",
                                                data: JSON.stringify(insertobjective_jsondata),
                                                contentType: "application/json;charset=UTF-8",
                                                dataType: "json",
                                                success: function (data)
                                                {
                                                    if (data.loginstatus == 0)
                                                        Redirect_Home =1;
                                                    else {
                                                        ds_objective = data;
                                                        Reload_GoalCategorylist = 1;
                                                        LoadEvents();
                                                    }
                                                },
                                                error: function (response) {
                                                    return console.error(response);
                                                }
                                            });
                                        }
                                        , onEditingStart: function (e) {
                                            //alert("EditingStart");
                                            OnEditObjectiveRowId = e.data.objective_id;
                                        }
                                        , onRowUpdating: function (e) {
                                            //alert("RowUpdating");
                                            var objective_name = "", objective_description = "", goalid, categoryid,
                                                objectivecompletedstatus = "";
                                            if (e.newData.objective_name) objective_name = e.newData.objective_name;
                                            if (e.newData.objective_description) objective_description = e.newData.objective_description;
                                            if (e.newData.objectivecompletedstatus === true || e.newData.objectivecompletedstatus === false) {
                                                objectivecompletedstatus = Boolean(false);
                                                objectivecompletedstatus = e.newData.objectivecompletedstatus;
                                            }
                                            else
                                                objectivecompletedstatus = "undefined";
                                            let updateobjective_jsondata =
                                                {
                                                    "objective_id": " " + OnEditObjectiveRowId.toString().trim() + " ",
                                                    "objective_name": " " + objective_name.toString().trim() + " ",
                                                    "objective_description": " " + objective_description.toString().trim() + " ",
                                                    "objectivecompletedstatus": " " + objectivecompletedstatus.toString().trim() + " ",
                                                    "goalid": " " + info.data.goal_id.toString().trim() + " ",
                                                };
                                            $.ajax({
                                                url: "http://127.0.0.1:8001/updateobjective",
                                                type: "PUT",
                                                data: JSON.stringify(updateobjective_jsondata),
                                                contentType: "application/json;charset=UTF-8",
                                                dataType: "json",
                                                success: function (data)
                                                {
                                                    if (data.loginstatus == 0)
                                                        Redirect_Home =1;
                                                    else
                                                    {
                                                        ds_objective = data;
                                                        Reload_GoalCategorylist=1;
                                                    }
                                                },
                                                error: function (response) {
                                                    return console.error(response);
                                                }
                                            });
                                            OnEditObjectiveRowId = 0;
                                        }
                                        , onRowRemoving: function (e) {
                                            //alert("RowRemoving");
                                            var removeobjective_jsondata =
                                                {
                                                    "objective_id": " " + e.data.objective_id.toString().trim() + " ",
                                                    "goalid": " " + info.data.goal_id.toString().trim() + " ",
                                                };
                                            $.ajax({
                                                url: "http://127.0.0.1:8001/removeobjective",
                                                type: "PUT",
                                                data: JSON.stringify(removeobjective_jsondata),
                                                contentType: "application/json;charset=UTF-8",
                                                dataType: "json",
                                                success: function (data)
                                                {
                                                    if (data.loginstatus == 0)
                                                        Redirect_Home =1;
                                                    else {
                                                        ds_objective = data;
                                                        Reload_GoalCategorylist = 1;
                                                    }
                                                },
                                                error: function (response) {
                                                    return console.error(response);
                                                }
                                            });
                                        }
                                    }).appendTo(container);
                            }
                        });

                    }
                }
            ,onSelectionChanged: function(e) {
                e.component.collapseAll(-1);
                e.component.expandRow(e.currentSelectedRowKeys[0]);
                goal_RowKey =  e.currentSelectedRowKeys[0];
            }
            , onRowInserting: function (e) {
                let insert_goal_jsondata =
                    {
                        "goal_name": " " + e.data.goal_name.toString().trim() + " ",
                        "goal_description": " " + e.data.goal_description.toString().trim() + " ",
                        "categoryid": " " + e.data.categoryid + " ",
                    };
                $.ajax({
                    url: "http://127.0.0.1:8001/insertgoal",
                    type: "POST",
                    data: JSON.stringify(insert_goal_jsondata),
                    contentType: "application/json;charset=UTF-8",
                    dataType: "json",
                    success: function (data)
                    {
                        if (data.loginstatus == 0)
                            Redirect_Home =1;
                        else {
                            ds_goallist = data;
                            Reload_GoalCategorylist = 1;
                        }
                    },
                    error: function (response) {
                        return console.error(response);
                    }
                });
            }
            , onRowInserted: function (e) {
                //alert("RowInserted");
            }
            , onEditingStart: function (e) {
                // alert("EditingStart");
                OnEditGoalRowId = e.data.goal_id;
            }
            , onRowUpdating: function (e) {
                // alert("RowUpdating");
                var goal_name = "", goal_description = "", goalcompletedstatus, categoryid = "";

                if (e.newData.goal_name) goal_name = e.newData.goal_name;
                if (e.newData.goal_description) goal_description = e.newData.goal_description;
                if (e.newData.categoryid) categoryid = e.newData.categoryid;
                if (e.newData.goalcompletedstatus === true || e.newData.goalcompletedstatus === false) {
                    goalcompletedstatus = Boolean(false);
                    goalcompletedstatus = e.newData.goalcompletedstatus;
                }
                else
                    goalcompletedstatus = "undefined";

                //alert (OnEditGoalRowId +"; "+ "goal_name = " + goal_name +"; "+ "goal_description = " + goal_description +"; "+  "goalcompletedstatus = " +  goalcompletedstatus +"; "+  "categoryid = " + categoryid);
                let update_goal_jsondata =
                    {
                        "goal_id": " " + OnEditGoalRowId.toString().trim() + " ",
                        "goal_name": " " + goal_name.toString().trim() + " ",
                        "goal_description": " " + goal_description.toString().trim() + " ",
                        "categoryid": " " + categoryid.toString().trim() + " ",
                        "goalcompletedstatus": " " + goalcompletedstatus + " ",
                    };
                //alert(JSON.stringify(update_goal_jsondata));
                $.ajax({
                    url: "http://127.0.0.1:8001/updategoal",
                    type: "PUT",
                    data: JSON.stringify(update_goal_jsondata),
                    contentType: "application/json;charset=UTF-8",
                    dataType: "json",
                    success: function (data)
                    {
                        if (data.loginstatus == 0)
                            Redirect_Home =1;
                        else {
                            ds_goallist = data;
                            Reload_GoalCategorylist = 1;
                        }
                    },
                    error: function (response) {
                        return console.error(response);
                    }
                });
                OnEditGoalRowId = 0;
            }
            , onRowUpdated: function (e) {
                // alert("RowUpdated");
            }
            , onRowRemoving: function (e) {
                // alert("RowRemoving");
                let remove_goal_jsondata =
                    {
                        "goal_id": " " + e.data.goal_id + " "
                    };
                $.ajax({
                    url: "http://127.0.0.1:8001/removegoal",
                    type: "PUT",
                    data: JSON.stringify(remove_goal_jsondata),
                    contentType: "application/json;charset=UTF-8",
                    dataType: "json",
                    success: function (data)
                    {
                        if (data.loginstatus == 0)
                            Redirect_Home =1;
                        else {
                            ds_goallist = data;
                            Reload_GoalCategorylist = 1;
                        }
                    },
                    error: function (response) {
                        return console.error(response);
                    }
                });
            }
            , onRowRemoved: function (e) {
                // alert("RowRemoved");
            }
        }).dxDataGrid("instance");
        var dataGrid_GoalObjective = $("#grid-container-goalobjective").dxDataGrid("instance");
        dataGrid_GoalObjective.expandRow(goal_RowKey);
    }
    // ------------------------------------------------------------------ Goals and Objectives --------- END ---
    // ------------------------------------------------------------------ Logout --- BEGIN ---
    $("#btnLogout").dxButton
    ({
        text: "Logout",
        type: "normal"
    });
    // ------------------------------------------------------------------ Logout --- END ---
    $(document).ajaxStop(function()
    {
        if(Reload_Eventlist == 1)
        {
            //Get the "ds_eventlist" and modify 'starttime' and 'expectfinishtime' using moment.js library for each row data.
            $(ds_eventlist).each(function()
            {
                // starttime_utcformat = moment.utc(this.starttime);
                this.starttime = moment(this.starttime).tz(user_TimeZone).format("YYYY-MM-DD HH:mm:ss");
                this.expectfinishtime = moment(this.expectfinishtime).tz(user_TimeZone).format("YYYY-MM-DD HH:mm:ss");
            });
            setEventGrid();
            Reload_Eventlist = 0;
        }
        if(Reload_Feedbackgrid == 1)
        {
            $.each(ds_feedbackgrid, function(i, item)
            {
                $.each(ds_eventlist, function(j, item)
                {
                    if(ds_feedbackgrid[i].eventlistid == ds_eventlist[j].eventlist_id)
                    {
                        ds_feedbackgrid[i].eventdescription = ds_eventlist[j].event_description;
                        return false;
                    }
                });
            });
            Reload_Feedbackgrid = 0;
            setFeedbackGrid();
        }
        if(Reload_EventTemplate == 1)
        {
            //Get the "ds_templateeventlist" and modify 'starttime' and 'expectfinishtime' using moment.js library for each row data.
            $(ds_templateeventlist).each(function()
            {
                this.template_starttime = moment.parseZone(this.template_starttime).format("YYYY-MM-DD HH:mm:ss");
                this.template_expectfinishtime = moment.parseZone(this.template_expectfinishtime).format("YYYY-MM-DD HH:mm:ss");
            });
            setEventTemplateGrid();
            Reload_EventTemplate = 0;
        }

        if(Reload_GoalCategorylist == 1)
        {
            setGoalsObjectives();
            Reload_GoalCategorylist=0;
        }
        if(Reload_Grid_Categorylist == 1)
        {
            setCategoryGrid();
            Reload_Grid_Categorylist = 0;
        }
        if(Redirect_Home == 1)
        {
            Redirect_Home = 0;
            self.location = "http://127.0.0.1:8001";
        }
    });


    function GlobalEventlistidCollection_FileUploader()
    {
        dataGrid_Event.getSelectedRowsData().then(function (rowData)
        {
            if (rowData.length <= 0)
               $("#FileUploader").find("*").prop("disabled", true);
            else
            {
                global_eventlistidcollection = "";
                for (let i = 0; i < rowData.length; i++)
                {
                    global_eventlistidcollection = global_eventlistidcollection + rowData[i].eventlist_id + "," ;
                }
                global_eventlistidcollection = global_eventlistidcollection.replace(/,(?=[^,]*$)/, '');
                $("#FileUploader").find("*").prop("disabled", false);
            }

        });
    }

    $("#btnEventCompleted").dxButton({
        text: "Mark event(s) completed status",
        type: "success",
        icon: "check",
        onClick: SetEventCompletedStatus
    });
    function SetEventCompletedStatus()
    {
        dataGrid_Event.getSelectedRowsData().then(function (rowData)
        {
            if($("#grid-container-feedback").is(":visible"))
                $("#grid-container-feedback").toggle("slow");

            if(rowData.length <= 0) return;
            //*** Day Begin -- BEGIN ---
                let pre_daybegin =new Date($("#daybegin").dxDateBox("option", "value"));
                let pre_daybegin_formatted = moment(pre_daybegin).format("YYYY-MM-DD HH:mm:ss");
                let  pre_daybegin_formatted_zone = moment.tz(pre_daybegin_formatted, user_TimeZone);
                let daybegin = moment.utc(pre_daybegin_formatted_zone.format()).format();
                //*** Day Begin -- END ---
                //*** Day End -- BEGIN ---
                let pre_dayend =new Date($("#dayend").dxDateBox("option", "value"));
                let pre_dayend_formatted = moment(pre_dayend).format("YYYY-MM-DD HH:mm:ss");
                let  pre_dayend_formatted_zone = moment.tz(pre_dayend_formatted, user_TimeZone);
                let dayend = moment.utc(pre_dayend_formatted_zone.format()).format();
                //*** Day End -- END ---
            let bulkeventcompletedstatus_jsondata =
                    {
                        "eventlistid_collection" : " "+ global_eventlistidcollection +" ",
                        "daybegin" : daybegin,
                        "dayend" : dayend,
                    };
            $.ajax({
                    url: "http://127.0.0.1:8001/bulkeventcompletedstatus",
                    type: "PUT",
                    data: JSON.stringify(bulkeventcompletedstatus_jsondata),
                    contentType: "application/json;charset=UTF-8",
                    dataType: "json",
                    success: function(data)
                    {
                        if (data.loginstatus == 0)
                            Redirect_Home =1;
                        else {
                            ds_eventlist = data;
                            Reload_Eventlist = 1;
                            DevExpress.ui.notify("Updated event completed status.");
                        }
                    },
                    error: function(response)
                    {return console.error(response);}
                   });
        });
    }

    $("#btnLoadFeedback").dxButton({
        text: "Show selected feedback",
        type: "success",
        onClick: SetEventFeedback
    });
    function SetEventFeedback()
    {

                 if (global_eventlistidcollection == "") return;
                 $("#grid-container-feedback").toggle("slow", function()
                {
                    if($("#grid-container-feedback").is(":visible"))
                    {

                        if ($("#grid-container-goalobjective").is(":visible"))
                            $("#grid-container-goalobjective").toggle("slow");

                        //Event Template Section --- BEGIN ---
                        if ($("#slbxEventTemplate").is(":visible"))
                            $("#slbxEventTemplate").toggle("slow");

                        if ($("#btnLoadTemplate").is(":visible"))
                            $("#btnLoadTemplate").toggle("slow");

                        if ($("#btnUpdateWeekday").is(":visible"))
                            $("#btnUpdateWeekday").toggle("slow");

                        if ($("#grid-container-templateevents").is(":visible"))
                            $("#grid-container-templateevents").toggle("slow");

                        if ($("#btnInsertTemplate").is(":visible"))
                            $("#btnInsertTemplate").toggle("slow");
                        //Event Template Section --- END ---

                        if ($("#grid-container-category").is(":visible"))
                            $("#grid-container-category").toggle("slow");

                        let feedback_jsondata =
                            {
                                "eventlistid_collection": " " + global_eventlistidcollection + " ",
                            };
                        $.ajax({
                            url: "http://127.0.0.1:8001/loadfeedbackgrid",
                            type: "POST",
                            data: JSON.stringify(feedback_jsondata),
                            contentType: "application/json;charset=UTF-8",
                            dataType: "json",
                            success: function (data) {
                                if (data.loginstatus == 0)
                                    Redirect_Home = 1;
                                else {
                                    ds_feedbackgrid = data.feedbackgrid;
                                    Reload_Feedbackgrid = 1;
                                }
                            },
                            error: function (response) {
                                return console.error(response);
                            }
                        });
                    }
                });
    }
    function setFeedbackGrid()
    {
        $("#grid-container-feedback").dxDataGrid({
            dataSource: ds_feedbackgrid,
            keyExpr: "eventlistid",
            columnAutoWidth: true,
            paging:
                {pageSize: 9},
            pager:
                {
                    showInfo: true,
                    showNavigationButtons: true
                },
            editing:
                {
                    allowUpdating: false,
                    allowAdding: false,
                    allowDeleting: false
                },
            loadPanel:
                {
                    enabled: true
                },
            selection:
                {
                    mode: "single"
                },
            wordWrapEnabled: true,
            filterRow:
                {visible: true},
            onInitialized: function (e) {
                dataGrid_Feedback = e.component;
            },
            columns:
            [
                {
                    dataField: "eventlistid",
                    visible: false,
                    allowEditing: false
                },
                {
                    dataField: "eventdescription",
                    caption: "Event Description"
                },
                {
                    dataField: "feedbacknote",
                    caption: "Feedback Note"
                }
            ]
        }).dxDataGrid("instance");
    }

    $("#btnLoadGallery").dxButton
    ({
        text: "Load gallery for selected events",
        type: "default",
        onClick: LoadGallery
    });
    function LoadGallery()
    {
        dataGrid_Event.getSelectedRowsData().then(function (rowData)
        {
            if(rowData.length <= 0) return;
            if(global_eventlistidcollection == "") return;
            let eventlistidcollection_jsondata =
                    {
                        "eventlistid_collection" : " "+ global_eventlistidcollection +" "
                    };
            $.ajax({
                    url: "http://127.0.0.1:8001/eventlistgallery",
                    type: "POST",
                    data: JSON.stringify(eventlistidcollection_jsondata),
                    contentType: "application/json;charset=UTF-8",
                    dataType: "json",
                    success: function(data)
                    {
                        if (data.loginstatus == 0)
                            Redirect_Home =1;
                        else {
                            ds_gallery = data;
                            DevExpress.ui.notify("Loading gallery...");
                        }
                    },
                    error: function(response)
                    {
                         return console.error(response);
                    },
                    complete: function (data) {
                            $(Gallery).removeData();
                            $(Gallery).lightGallery
                            ({
                                escKey: true,
                                loop: true,
                                enableSwipe: true,
                                mousewheel: true,
                                dynamic: true,
                                share: false,
                                videojs : true,
                                download: true,
                                dynamicEl: ds_gallery
                            });
                    }
            });

        });
    }

    $("#FileUploader").dxFileUploader({
          name: "file"
        , accept: "*"
        , uploadMode: "instantly"
        , allowCanceling: true
        , multiple: false
        , value: []
        , uploadUrl: "http://127.0.0.1:8001/eventsfileupload"
        , onValueChanged: function (e)
        {
            uploadUrl = e.component.option("uploadUrl");
            uploadUrl = updateQueryStringParameter(uploadUrl, "eventlistid_collection", global_eventlistidcollection);
            e.component.option("uploadUrl", uploadUrl);
        }
    });
    $("#FileUploader").find("*").prop("disabled", true);
    function updateQueryStringParameter (uri, key, value)
    {
        var re = new RegExp("([?&])" + key + "=.*?(&|$)", "i");
        var separator = uri.indexOf('?') !== -1 ? "&" : "?";
        if (uri.match(re))
        {
            return uri.replace(re, '$1' + key + "=" + value + '$2');
        }
        else
        {
            return uri + separator + key + "=" + value;
        }
    }

    if (OnloadInitial == 1)
    {
        OnloadInitial=0;
        LoadEvents();
    }
});