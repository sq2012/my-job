var g_url
var logtimer1,logtimer2;
var grid_fieldnames={};
var grid_fieldcaptions={};
var grid_disabledfields={};
var grid_frozenfields={}
var tblName={};
var outerLayout='';
var g_search_urls={}
var IsShowLeftInfo=false
var mod_name=''
var pos_start_date=''
var pos_end_date=''
var home_url={}
var $tabs
var g_urls={}
var jqOptions={}
var g_activeTabID='default'
var tabs_style=0;//1=¶àÒ³ä¯ÀÀ
var options={}
var defVal={}
var initCloseWest=['tab_ipos_ICConsumerList','tab_ipos_CardCashSZ','tab_visitors_visitionlogs_his']

//var options={default:{pagerId:"pages", tblId:"tbl", showSelect: true, canSelectRow:false,showStyle:false,
//	canEdit: true,
//	canAdd: true,
//	canDelete: true,
//	canSearch: true, keyFieldIndex:"0", title:'',
//	tblHeader:'',
//	dlg_width:500,
//	dlg_height:'auto',
//	edit_col:1}
//};
var lang = {
		Pane:		"Pane"
	,	Open:		gettext("Open")	// eg: "Open Pane"
	,	Close:		gettext("Close")
	,	Resize:		gettext("Resize")
	,	Slide:		gettext("Slide Open")
	,	Pin:		"Pin"
	,	Unpin:		gettext("")
	,	selector:	"selector"
	,	msgNoRoom:	"Not enough room to show this pane."
	,	errContainerMissing:	"UI.Layout Initialization Error\n\nThe specified layout-container does not exist."
	,	errContainerHeight:		"UI.Layout Initialization Error\n\nThe layout-container \"CONTAINER\" has no height!"
	,	errButton:				"Error Adding Button \n\nInvalid "
	};

var layoutSettings_Outer = {
	name: "outerLayout" // NO FUNCTIONAL USE, but could be used by custom code to 'identify' a layout
	// options.defaults apply to ALL PANES - but overridden by pane-specific settings
,	defaults: {
		size:					"auto"
	,	applyDemoStyles: 		false		// NOTE: renamed from applyDefaultStyles for clarity
	,	minSize:				50
	,	paneClass:			"ui-layout-pane" 		// default = 'ui-layout-pane'
	,	contentSelector:		".west-content"	// inner div to auto-size so only it scrolls, not the entire pane!
	,	west__paneSelector:   		"ui-layout-west"
	,	center__paneSelector:   		".tab-ui-layout-center"
	,	resizerClass:			"ui-layout-resizer"	// default = 'ui-layout-resizer'
	,	togglerClass:			"ui-layout-toggler"	// default = 'ui-layout-toggler'
	,	buttonClass:			"button"	// default = 'ui-layout-button'
//	,	contentSelector:		".ui-layout-content"	// inner div to auto-size so only it scrolls, not the entire pane!
	,	contentIgnoreSelector:	"span"		// 'paneSelector' for content to 'ignore' when measuring room for content
	,	togglerLength_open:		0			// WIDTH of toggler on north/south edges - HEIGHT on east/west edges
	,	togglerLength_closed:	0			// "100%" OR -1 = full height
	,	hideTogglerOnSlide:		true		// hide the toggler when pane is 'slid open'
	,	togglerTip_open:		gettext("Close")//lang.Close//"ÊÕÆðÃæ°å"
	,	togglerTip_closed:		gettext("Open")//lang.Open//"Õ¹¿ªÃæ°å"
	,	resizerTip:				"Resize"//lang.Resize//"ÍÏ¶¯Ãæ°å"
	,	sliderTip:				"Slide Open"//lang.Slide//"Õ¹¿ªÃæ°å"
	//	effect defaults - overridden on some panes
	,	fxName:					"slide"		// none, slide, drop, scale
	,	fxSpeed_open:			0
	,	fxSpeed_close:			0
	,	fxSettings_open:		{easing: "easeInQuint"}
	,	fxSettings_close:		{easing: "easeOutQuint"}
	,	onresize_end:			function () { AutoResizeWindow(); }
}

,	north: {
	    minSize:				76
	,   maxSize:                0
	,	spacing_open:			0			// cosmetic spacing
	,	togglerLength_open:		0			// HIDE the toggler button
	,	togglerLength_closed:	-1			// "100%" OR -1 = full width of pane
	,	resizable: 				false
	,	slidable:				false
	//	override default effect
	,	fxName:					"none"
	}
//,	south: {
//	    minSize:				5
//	,   maxSize:                5
//	,	spacing_closed:			0			// HIDE resizer & toggler when 'closed'
//	,	resizable: 				false
//	,	slidable:				false		// REFERENCE - cannot slide if spacing_closed = 0
//	,	initClosed:				false
//	,	spacing_open:			0			// cosmetic spacing
//	,	togglerLength_open:		0			// HIDE the toggler button
//	,	togglerLength_closed:	-1			// "100%" OR -1 = full width of pane
//	}
,	west: {
		size:					220
	,	minSize:200
	,	spacing_open:           7
	,	spacing_closed:			9			// wider space when closed
	,	togglerLength_closed:	56			// make toggler 'square' - 21x21
	,	togglerAlign_closed:	"center"		// align to top of resizer
	,	togglerLength_open:		56			// NONE - using custom togglers INSIDE west-pane
//	,	togglerTip_open:		"ÊÕÆðÖ÷²Ëµ¥"
//	,	togglerTip_closed:		"Õ¹¿ªÖ÷²Ëµ¥"
//	,	resizerTip_open:		"ÍÏ¶¯Ãæ°å"
	,	slideTrigger_open:		"click" 	// default
	,	resizable: 				true
	,	slidable:				false		// REFERENCE - cannot slide if spacing_closed = 0
	,	initClosed:				false
	,	onclose_end:			function () {  }
	,	onopen_end:			function () {  }
	//,	contentSelector:		".west-content"	// inner div to auto-size so only it scrolls, not the entire pane!

	//	add 'bounce' option to default 'slide' effect
	,	fxSettings_open:		{easing: "easeOutBounce"}
	}

,	center: {
	
		minWidth:				600
	,	minHeight:				200
//	,	contentSelector:		"._home_"	// inner div to auto-size so only it scrolls, not the entire pane!
	
	}
};

var layoutSettings_default = {
	name: "InnerLayout" // NO FUNCTIONAL USE, but could be used by custom code to 'identify' a layout
	// options.defaults apply to ALL PANES - but overridden by pane-specific settings
,	defaults: {
		size:					"auto"
	,	center__paneSelector:   		"ui-layout-tabs"
//	,	contentSelector:		".ui-layout-content"	// inner div to auto-size so only it scrolls, not the entire pane!
	,	onresize:			function () {$("#g_tabs").tabs('refresh') }
}
,	north: {
	    minSize:				0
	,   maxSize:                0
	,	spacing_open:			0			// cosmetic spacing
	,	togglerLength_open:		0			// HIDE the toggler button
	,	togglerLength_closed:	-1			// "100%" OR -1 = full width of pane
	,	resizable: 				false
	,	slidable:				false
	//	override default effect
	,	fxName:					"none"
	}

//,	south: {
//	    minSize:				0
//	,   maxSize:                0
//	,	spacing_closed:			0			// HIDE resizer & toggler when 'closed'
//	,	resizable: 				false
//	,	slidable:				false		// REFERENCE - cannot slide if spacing_closed = 0
//	,	initClosed:				false
//	,	spacing_open:			0			// cosmetic spacing
//	,	togglerLength_open:		0			// HIDE the toggler button
//	,	togglerLength_closed:	-1			// "100%" OR -1 = full width of pane
//	}
,	center: {
		minWidth:				400
	,	minHeight:				200
	}
	
	
};
var innerSettings_default = {
	name: "InnerLayout" // NO FUNCTIONAL USE, but could be used by custom code to 'identify' a layout
	// options.defaults apply to ALL PANES - but overridden by pane-specific settings
,	defaults: {
		size:					"auto"
	,	contentSelector:		".inner-west-content"	// inner div to auto-size so only it scrolls, not the entire pane!
	,	center__paneSelector:   		".inner-ui-layout-center"
	,	west__paneSelector:   		".inner-ui-layout-west"
	,	onresize:			function () {AutoResizeReportGrid(); }
}
,	north: {
	    minSize:				0
	,   maxSize:                0
	,	spacing_open:			0			// cosmetic spacing
	,	togglerLength_open:		0			// HIDE the toggler button
	,	togglerLength_closed:	-1			// "100%" OR -1 = full width of pane
	,	resizable: 				false
	,	slidable:				false
	//	override default effect
	,	fxName:					"none"
	}

//,	south: {
//	    minSize:				0
//	,   maxSize:                0
//	,	spacing_closed:			0			// HIDE resizer & toggler when 'closed'
//	,	resizable: 				false
//	,	slidable:				false		// REFERENCE - cannot slide if spacing_closed = 0
//	,	initClosed:				false
//	,	spacing_open:			0			// cosmetic spacing
//	,	togglerLength_open:		0			// HIDE the toggler button
//	,	togglerLength_closed:	-1			// "100%" OR -1 = full width of pane
//	}
,	center: {
		minWidth:				200
	,	minHeight:				200
	}
 
	
	
};





jq_Options={
   	url:'',
	mtype:"POST",
	postData:{},
	datatype: "json",
	colModel:[],
	autowidth: true,
	shrinkToFit:false,
   	rowNum:50,
	rownumber:true,
	gridview:true,
	multiselect:true,
   	rowList:[],
   	pager: '#id_pager',
   	sortname: 'id',
	//ajaxGridOptions:{async: false },
	viewrecords: true,
	multiboxonly:true,
	sortorder: "asc",
	//loadui:'disable',
	jsonReader: {repeatitems : false},
	height:300,
	gridComplete: function(){
			//preprocessEdit();
		}
	};
timepickerOptions={
	inline: true,
	buttonImage: '/media/img/icon_clock.gif',
	buttonText:gettext("Time"),
	buttonImageOnly: true,		
	showOn:'button',//ÔÚÊäÈë¿òÅÔ±ßÏÔÊ¾°´Å¥´¥·¢£¬Ä¬ÈÏÎª£ºfocus¡£»¹¿ÉÒÔÉèÖÃÎªboth  
	showButtonPanel: true,  
	autoSize:false
//	hourText:gettext('Hour'),
//	minuteText:gettext('Minute'),
//	timeText:gettext('Time'),
//	timeOnlyTitle:gettext('Choose Time'),
//	currentText:gettext('Now')
	};
datepickerOptions={
	dateFormat:'yy-mm-dd',
	inline: true,
	changeMonth: true,
	buttonImage: '/media/img/Calendar.png',
//	buttonText:gettext("Calendars"),
	buttonImageOnly: true,		
	showOn:'button',//ÔÚÊäÈë¿òÅÔ±ßÏÔÊ¾°´Å¥´¥·¢£¬Ä¬ÈÏÎª£ºfocus¡£»¹¿ÉÒÔÉèÖÃÎªboth  
	showButtonPanel: true,  
	autoSize:false
//	showTimepicker:false
	};


datetimepickerOptions={
	dateFormat:'yy-mm-dd',
	inline: true,
	changeMonth: true,
	buttonImage: '/media/img/Calendar.png',
	//buttonText:gettext("Calendars"),
	buttonImageOnly: true,		
	showOn:'button',//ÔÚÊäÈë¿òÅÔ±ßÏÔÊ¾°´Å¥´¥·¢£¬Ä¬ÈÏÎª£ºfocus¡£»¹¿ÉÒÔÉèÖÃÎªboth  
	showButtonPanel: true,  
	autoSize:false,
	timeOnly: false
//	hourText:gettext('Hour'),
//	minuteText:gettext('Minute'),
//	timeText:gettext('Time'),
//	timeOnlyTitle:gettext('Choose Time'),
//	currentText:gettext('Now')
	}

//copy jq_Options¶ÔÏó,
function copyObj(obj){
   var jp=new Object()
   for(p in obj){
      jp[p]=obj[p]
   }
  return jp;
}

function AutoResizeWindow() {
    
    if(g_activeTabID=='tab_id_menu_home'&&($.isFunction(window['AutoResizeHome_'])))
       AutoResizeHome_();
       
     if($.isFunction(window['SetGridWidth']))
        SetGridWidth('#id_content')
                
}

function load_AboutDlg(title) {
	$.getScript("/media/jslib/license.min.js?scriptVersion=10.0", function(data, status, jqxhr) {});
	$.ajax({
		type:"GET",
		url:"/iclock/accounts/About/",
		dataType:"html",
		async:false,
		success:function(msg){
			 msg=$.trim(msg);
			$(msg).dialog({modal:true,
							  width: 550,
							  height:460,
							  resizable:false,
							  title:title,
							  close:function(){$(this).dialog("destroy")}
							})

		}
	});
	
}
function AutoResizeReportGrid() {
 	var grid_width=$("#report_module .ui-layout-center").width()-10
	$("#id_grid_report").jqGrid('setGridWidth',grid_width);
}
function refresh_tree(treeID)
{
	var treeObj = $.fn.zTree.getZTreeObj(treeID);
    var nodes = treeObj.getSelectedNodes();
    if (nodes.length>=0) {
         treeObj.reAsyncChildNodes(nodes[1], "refresh");
    }
}
