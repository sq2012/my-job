$.blockUI.defaults.pageMessage="<img src='/media/img/loading.gif' />";
function actionSuccess(retdata){
	var message= retdata.message;
	$.unblockUI();
	if (tblName[g_activeTabID]=='Meet_order'){//实时刷新'会议预约'右侧内容
		 $.ajax({type: "POST",
			url: '/meeting/getData/?func=lastweekmeeting',
			dataType:"json",
			success: function(retdata){
							var re=retdata;
							var html="<div style='color:red;font-size:15px;padding: 5px;'>未来7天会议安排：</div>"
							for(var i=0;i< re.length;i++){
								html+="<div style='color:green;padding-left: 15px;'>"+re[i]['name']+"（"+re[i]['st']+"至"+re[i]['et']+"）</div>"
							}
							$("#west_content_tab_meeting_Meet_order").html(html)
			},
			error: function(){
			$.unblockUI();alert($.validator.format(gettext('Operating failed for {0} !'),options.title));}
			});
	}else{
		
	}
	if (tblName[g_activeTabID]=='level_emp'){
		reloadData('level_emp_east');
	}else{
		reloadData();
	}
	if(retdata.ret==1)
	alert(message)
	$("#id_message").html(message).css('color','red').css("display","block");
}
function actionSucess_NoReload(retdata)
{
	$.unblockUI();
	if(retdata.ret==0){
	}
	else
	{
		alert(retdata.message);
	}

}

function createDataDialog(ModalName, title,  width,actionUrl,tag)
{
	dataDialog(title, width,tag);
	procSimpleData(ModalName,actionUrl,tag)
}


function dataDialog(title, width,tag)
{
	
	var block_html="<div id='simple_data'>"
		+	createMiniGrid()
		+	"<div id='id_message_simple'></div>"
	if (tag) {
		block_html+='<span style="position: absolute;left: 15px;padding:5px"><input type="text" id="id_searchsn" name="searchsn"/> <button type="button" id="btnShowSearch" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" role="button"><span class="ui-button-text">模糊查询</span></button></span>'
	}
		block_html+="</div>"
	var dlg=$(block_html).dialog({	modal:true,
		                  resizable:false,
						  width: width,
						  height:550,
						  title:title,
						  close:function(){$(this).dialog("destroy")}
						})

	return	dlg;

}

function procSimpleData(ModalName,actionUrl,tag)
{
		var jqOptions_mini=copyObj(jq_Options);
		var miniDataUrl=actionUrl
		if(ModalName=='devcmds')		
		{
			jqOptions_mini.sortname='id';
			jqOptions_mini.sortorder='desc';
		}
		height=390
		if (tag) {
			height=360
		}
		$.ajax({
			type:"GET",
			url:"/iclock/att/getColModel/?dataModel="+ModalName,
			dataType:"json",
			data:'',
			success:function(json){
				jqOptions_mini.rows=100
				if (ModalName=='searchs') {
					jqOptions_mini.rows=300
				}
				jqOptions_mini.colModel=json['colModel']
				jqOptions_mini.height=height
				jqOptions_mini.url=miniDataUrl
				jqOptions_mini.pager="#id_pager_mini";
				jqOptions_mini.gridComplete=null;
				jqOptions_mini.editurl=miniDataUrl;
				renderGridData("mini",jqOptions_mini)
			}
		});
}













function createDialog(url, actionUrl, miniDataUrl, title, label, width, multiSel,ModelName)
{
	//miniDataUrl:	for fill the select box
	//title:		dialog title
	//label:		select box title
	//width:		dialog width
	miniDialog(title, label, width, multiSel,url,actionUrl);
	if(procMiniData(miniDataUrl,ModelName)){
		if(miniDataUrl.indexOf('/iclock/data/iclock/?mod_name=')!=-1){
			var html='<span style="position: absolute;left: 15px"><input type="text" id="id_searchsn" name="searchsn"/> <button type="button" id="btnShowSearch" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" role="button"><span class="ui-button-text">模糊查询</span></button></span>'
			$(".ui-dialog-buttonset").prepend(html)
			$("#btnShowSearch").click(function() {
				    var ss=$("#id_searchsn").val()
				    var jqOptions_mini=copyObj(jq_Options);
					jqrul="/iclock/data/iclock/?mod_name="+mod_name+"&q="+escape(ss);
					if (actionUrl.indexOf('add_meet_devices')!=-1) {
						jqOptions_mini.url=jqrul+'&t=iclock_mini.js'
					}else{
						jqOptions_mini.url=jqrul
					}
					jqOptions_mini.sortname='SN'
				    renderGridData("mini",jqOptions_mini)
				})
		}
		procSubmit("btnShowOK", url, actionUrl)
	}
}

function procSubmit(btnID, url, actionUrl)
{
	if(typeof actionUrl=="function"){
		$("#"+btnID).click(function() {
				var ss=getSelected_emp_ex("mini")
				if (ss.length==0){
					alert('请选择');return;
				}
			var slt=ss.join(',')
			actionUrl(url, slt);
			//$.unblockUI();
			
			
			});
	}
	else
		$("#"+btnID).click(function() {
			if(actionUrl!='?action=toDepart&department=')
			{
				var ss=getSelected_emp_ex("mini")
				if (ss.length==0){
					alert('请选择设备');return;
				}
			}
			else
			{
				var ss=getSelected_dept("showTree_toDepart")
				if(ss.length==0)
				{
					alert('请选择单位');return;
				
				}
				
			}
			var slt=ss.join(',')
			if (slt != "")
			{
				a = actionUrl + slt
				if(a.indexOf("action=")>=0 && url.ret.indexOf("K=")>=0)
				{
					$.blockUI({theme: true ,baseZ:10000,message: '<h1><img src="/media/img/loading.gif" /> <br>'+gettext("Please wait...")+'</br></h1>'});					
					$.ajax({type: "POST",
						url:g_urls[g_activeTabID].split("?")[0]+a,
						data: url.ret,
						dataType:"json",
						success: actionSuccess,
						error: function(request, errorMsg){
							alert($.validator.format(gettext('Operating failed for {0} : {1}'), options.title, errorMsg)); $.unblockUI();
							}
						});
				}
				else
					window.location.href = a +"&p="+page_index+url.ret
			}
		});
}

function procMiniData(miniDataUrl,ModelName)
{
	if(ModelName==undefined)
	ModelName="devices"
	if(miniDataUrl!="miniData?key=depart")
	{
		var jqOptions_mini=copyObj(jq_Options);
		if (ModelName=='devices') {
			jqOptions_mini.sortname='SN'
		}
		$.ajax({
			type:"GET",
			url:"/iclock/att/getColModel/?dataModel="+ModelName,
			dataType:"json",
			data:'',
			success:function(json){
				if(miniDataUrl.indexOf('/iclock/data/iclock/')!=-1){
					miniDataUrl=miniDataUrl+'&t=iclock_mini.js'

				}
				jqOptions_mini.colModel=json['colModel']
				jqOptions_mini.height=230
				jqOptions_mini.url=miniDataUrl
				jqOptions_mini.pager="#id_pager_mini";
				jqOptions_mini.gridComplete=null;

				renderGridData("mini",jqOptions_mini)
			}
		});
	}
	else
	{
		ShowDeptData("toDepart");	
		var zTree = $.fn.zTree.getZTreeObj("showTree_toDepart");
		zTree.setting.check.enable = false;
		
		
		
	}
	return true;
}

function miniDialog(title, label, width, multiSel,url,actionUrl)
{
	var block_html="<div id='emp_to_dev'>"
		+ 	"<div>"
		//+ 	"<label>"+$.validator.format(gettext('Please Select {0}'),label)+"</label>"
		+	createMiniGrid(actionUrl)
		+ 	"</div>"
		+	"<div id='id_message'></div>"
		+ 	"</div>"
	var dlg=$(block_html).dialog({	modal:true,
						   resizable:false,
						  width: width,
						  height:420,
						  title:title,
						  buttons:[{id:"btnShowOK",text:gettext("Submit"),click:function(){}},
								 {id:"btnShowCancel",text:gettext("Cancel"),click:function(){$(this).dialog("destroy");}
								}],
						  close:function(){$(this).dialog("destroy")}
						})

	return	dlg;

}

function createMiniGrid(actionUrl)
{
	if(actionUrl=='?action=toDepart&department=')	return "<div>"
		        +"<ul id='showTree_toDepart' class='ztree' style='height:260px;'></ul>"
		+"</div>"
	else	return "<div>"
			+"<table id='id_grid_mini' >	</table>"
			+"<div id='id_pager_mini'></div>"
		+"</div>"
}

function createDateRangeDlg(header,action)
{
	var block_html=
		  "<div id='emp_tmp_to_dev'>"
		+  "<div id='id_time_range' class=''>"
		+ 	"<label>"+gettext('Input the range of time')+"</label>"
		+   createTimeRangeEdit()
//		+gettext("Transfer employee to the device")
		+ "</div>"
		+createMiniGrid(action)
		+"<div id='id_message'></div>"
		+"</div>"
		var dlg=$(block_html).dialog({modal:true,
									   resizable:false,
									  width: 600,
									  height:450,
									  title:header,
									  buttons:[{id:"btnShowOK",text:gettext("Submit"),click:function(){}},
											 {id:"btnShowCancel",text:gettext("Cancel"),click:function(){$("#emp_tmp_to_dev").remove();}
											}],
									  close:function(){$(this).dialog("destroy")}
									  		
									})
	$("#id_date_range_from").datepicker(datepickerOptions);
	$("#id_date_range_to").datepicker(datepickerOptions);

}


function createPrivilegeDlg(header)
{

	var arr = ['0 正常', '4 登记员', '6 系统管理员', '14 超级管理员']
	var colCount = 3
	var block_html=
		  "<div id='emp_tmp_to_dev'>"
		+  "<div id='id_privilege' class=''>"
		+ 	"<label>"+gettext('select a privilege')+"</label>"
		+   createSelectHtml(arr, colCount)
		+ "</div>"
		+"<div id='id_message'></div>"
		+"</div>"
		var dlg=$(block_html).dialog({modal:true,
									 resizable:false,
									  width: 450,
									  height:200,
									  title:header,
									  buttons:[{id:"btnShowOK",text:gettext("Submit"),click:function(){}},
											 {id:"btnShowCancel",text:gettext("Cancel"),click:function(){$("#id_privilege").remove();$(this).dialog("destroy");}
											}],
									  close:function(){$(this).dialog("destroy");}		
									})

}


function createDateRangeDlg1(header)
{
	var block_html=
		  "<div id='emp_tmp_to_dev'>"
		+  "<div id='id_time_range' class=''>"
		+ 	"<label>"+gettext('Input the range of time')+"</label>"
		+   createTimeRangeEdit()
		+ "</div>"
		+"<div id='id_message'></div>"
		+"</div>"
		var dlg=$(block_html).dialog({modal:true,
									 resizable:false,
									  width: 460,
									  height:200,
									  title:header,
									  buttons:[{id:"btnShowOK",text:gettext("Submit"),click:function(){}},
											 {id:"btnShowCancel",text:gettext("Cancel"),click:function(){$("#emp_tmp_to_dev").remove();}
											}],
									  close:function(){$(this).dialog("destroy");}		
									})
	$("#id_date_range_from").datepicker(datepickerOptions);
	$("#id_date_range_to").datepicker(datepickerOptions);

}

function createDateDlg(header)
{
	var html=
		  "<div class='dialog'>"
		+  "<div class='dheader'><span>" + header + "</span><span class='close' onclick='javascript:$.unblockUI();'></span></div>"
		+  "<div class='dcontent'>"
		+ 	"<input class='dtitle' value='"+gettext('Input the range of time')+"' readonly />"
		+   createDateRangeEdit()
		+	"<br/>"
		+ "</div>"
        + createSubmitButton()
		+"</div>"
	scroll(0,0);
	$.blockUI(html);
	blockUI_center();
	DateTimeShortcuts.init();
	$("div.clockbox").css("z-index",2005);
	$("div.calendarbox").css("z-index",2005);
	$("#btnShowCancel").click(function() {
			$("div.clockbox").hide();
			$("div.calendarbox").hide();
			$.unblockUI();
			});
	$("input.dtitle").focus(function(){
			$("#id_date_range_from")[0].focus();
			})
}

function createEndDateDlg(header)
{
	var html=
		  "<div class='dialog'>"
		+  "<div class='dheader'><span>" + header + "</span><span class='close' onclick='javascript:$.unblockUI();'></span></div>"
		+  "<div class='dcontent'>"
		+ 	"<fieldset style='border:1px solid #000000;'><legend class='dtitle'>"+gettext('AC Clock-in/out Records')+"</legend>"
		+   createDateEdit(0) 
		+	"</fieldset>"
    	+ 	"<fieldset style='border:1px solid #000000;'><legend class='dtitle'>"+gettext('Attendance Picture Records')+"</legend>"
		+   createDateEdit(1) 
		+	"</fieldset>"
		+ 	"<fieldset style='border:1px solid #000000;'><legend class='dtitle'>"+gettext('Attendance Cacluate Records')+"</legend>"
		+   createDateEdit(2) 
		+	"</fieldset>"
		+'<span id="id_error"></span>'
        + "</div>"
    	+ createSubmitButton()
		+"</div>"
	scroll(0,0);
	$.blockUI(html);
	blockUI_center();
	DateTimeShortcuts.init();
	$("div.clockbox").css("z-index",2005);
	$("div.calendarbox").css("z-index",2005);
	$("#btnShowCancel").click(function() {
			$("div.clockbox").hide();
			$("div.calendarbox").hide();
			$.unblockUI();
			$("._pop_cal_").remove();
			DateTimeShortcuts.init();
			
	});


}
function createEndDateDlg1(header)
{
	var html=
		  "<div id='id_enddatedlg1'>"
		+   createDateEdit(0) 
		+'<span id="id_error"></span>'
		+"</div>"
		$(html).dialog({modal:true,
			 resizable:false,
                                width: 550,
				height:300,
				title:header,
			      buttons:[{id:"btnShowOK",text:gettext('Submit'),click:function(){}},
				      {id:"btnShowCancel",text:gettext('Cancel'),click:function(){$('#id_enddatedlg1').remove(); }}
				      ],
			      close:function(){$(this).dialog("destroy");}		

			      })
		$('#id_endTime'+0).datepicker(datepickerOptions);

}

function getDateRangeFor(fieldName)
{
	createDateRangeDlg(gettext('Please Input'));
	$("#btnShowOK").click(function() {
			var fromTime=$("#id_date_range_from").val();
			var toTime=$("#id_date_range_to").val();
			var url="";
			if(fromTime=="" ||toTime=="")
				url="";
			else{
				var isfromTime=false;
				var istoTime=false;
				if(fromTime.length<=11)
					isfromTime=valiDate(fromTime)
				else
					isfromTime=valiDateTimes(fromTime)
					
				if(toTime.length<=11)
					istoTime=valiDate(toTime)
				else
					istoTime=valiDateTimes(toTime)
				url=(isfromTime?("&"+fieldName+"__gte="+fromTime):"")+(istoTime?("&"+fieldName+"__lte="+toTime):"");
			}
			if(url=="") url=fieldName+"__isnull=True"
			window.location.href=getQueryStr(window.location.href, [fieldName+"*"], url)});
	$("#id_date_range_from")[0].focus();
}


function getCurFrontUrl()
{
	var scripts = document.getElementsByTagName('script');
	for (var i=0; i<scripts.length; i++) {
		if (scripts[i].src.match(/tools/)) {
			var idx = scripts[i].src.indexOf('jslib/tools');
			return scripts[i].src.substring(0, idx);
		}
	}
}

function blockUI_center()
{
	var box=$(".dialog")
	width = box.width()
	height = box.height()
	$(".blockMsg").css("width",width);
	$(".blockMsg").css("height",height);
	var m_left=($(window).width()-width)/2;
	var m_top=($(window).height()-height)/2;
	$(".blockMsg").css('left', m_left).css('top',m_top)
	/*
	if(!($.browser.msie && $.browser.version<7.0)){
		{
			var m_left=($(window).width()-width)/2;
			var m_top=($(window).height()-height)/2;
			$(".blockMsg").css('left', m_left).css('top',m_top)
		}
	}
	*/
}
function getQueryStr(q, keys, append)
{
	if(append && append.indexOf('?')==0)
		append=append.substr(1,1000)
	if(q.indexOf('?')<0)
	{
		if(append) return "?"+append;
		return q;
	}
	var qry=q.split("?")[1].split("&");
	var newQry=[];
	var rm=0;
	for(var i in qry)
	{
		rm=0;
		qk=qry[i].split("=")[0];
		for(var j in keys)
		{
			var k=keys[j];
			if((k==qk) ||
				(k.substr(k.length-1,1)=="*" && qk.indexOf(k.substr(0,k.length-1))==0))
			{
				rm=1;
				break;
			}
		}
		if(0==rm && qry[i].length>0) newQry.push(qry[i]);
		//k.indexOf("&"+qk+"&")<0) newQry.push(qry[i]);
	}
	if(newQry.length)
		return "?"+newQry.join("&")+(append?("&"+append):"");
	else
		return append?("?"+append):q.split("?")[0];
}

function getKeyQuery(key)
{
	var q=window.location.href;
	if(q.indexOf('?')<0) return "";
	var qry=q.split("?")[1].split("&");
	for(var i in qry)
		if(qry[i].split("=")[0]==key) return qry[i];
	return "";
}

function repUrlKey(key, newValue)
{
	return getQueryStr(window.location.href, [key], newValue?key+'='+newValue:"");
}

function renderResultTbl(p,page_style) 
{
	var emp_tmp=$.cookie("emp")
	var ct=$.cookie("ComeTime");
	var et=$.cookie("EndDate");
    var d=$.cookie("deptIDs")
    var emp="";
    var ComeTime="";
    var dept="";
    var EndDate="";
    var sidx="";
    var jqOptions=copyObj(jq_Options)
 
    if(emp_tmp!=null && emp_tmp!="")
        emp=emp_tmp;
    if(ct!=null && ct!="")
        ComeTime=ct;
    if(et!=null && et!="")
        EndDate=et;
    if(d!=null && d!="")
       dept="&deptIDs="+d;
   if( typeof(dept)=="object")
   	{
   		var maxUrlLength=$.browser.msie?2000:(20*1024);
   		while((dept.join(",").length>maxUrlLength))
   			dept.pop(0);
   	}
   if( typeof(emp)=="object")
	{
		var maxUrlLength=$.browser.msie?2000:(20*1024);
		while((emp.join(",").length>maxUrlLength))
			emp.pop(0);
	}
	if(page_style=='record_details'){
	
	var tblname="";
	var sortname="";
 	var order_type="";	
		tblname="attRecAbnormite"
		sortname="checktime"
		urlStr="/iclock/data/attRecAbnormite/?ot=0&checktime__gte="+ComeTime+"&checktime__lt="+EndDate+dept+"&UserID__id__in="+emp+"&stamp="+new Date().toUTCString();
	}	
	if(page_style=='exception_details'){
	    tblname="AttException"
		sortname="AttDate"
		urlStr="/iclock/data/AttException/?ot=0&t=AttException_list.js&AttDate__gte="+ComeTime+"&AttDate__lt="+EndDate+dept+"&UserID__id__in="+emp+"&stamp="+new Date().toUTCString();
	}
	if(page_style=='forget_records'){
		tblname="usetransaction"
		sortname="TTime"
		urlStr="/iclock/data/transactions/?Verify=5&TTime__gte="+ComeTime+"&TTime__lt="+EndDate+dept+"&UserID__id__in="+emp+"&stamp="+new Date().toUTCString();
	}
	if(page_style==14){
	    tblname="attpriReport"
	    sortname="AttDate"
		urlStr="/iclock/data/attpriReport/?t=attPriReport.html&AttDate__gte="+ComeTime+"&AttDate__lt="+EndDate+dept+"&UserID__id__in="+emp+"&stamp="+new Date().toUTCString();
		//urlStr="/iclock/data/attpriReport/"
	}
	savecookie("search_urlstr",urlStr);
	var ischecked=0;
	if($("#id_cascadecheck").prop("checked"))
		ischecked=1;
	urlStr+="&isContainChild="+ischecked;
	
		if($("#o_DeptID").prop("checked")==true){
			sidx=sidx+"UserID__DeptID,"
		}
		if($("#o_PIN").prop("checked")==true){
			sidx=sidx+"UserID__PIN,"
		}
		if($("#o_EName").prop("checked")==true){
			sidx=sidx+"UserID__EName,"
		}
		if($("#o_TTime").prop("checked")==true){
			sidx=sidx+sortname+","
		}

	if(sidx.length>0)
	{
	   sidx=sidx.substring(0,sidx.length-1);
	}
	else
	sidx=sortname
	
	$("#id_"+page_style+'_grid').jqGrid('GridUnload')
	//$.jgrid.gridUnload("#id_"+page_style+'_grid')
   var height=$(".tabpanel_content").height()-60;
    jqOptions.height=height;
	var pw=$("#id_content").width()
	jqOptions.autowidth=false
	jqOptions.width=pw-10
	
	$.ajax({
			type:"get",
			url:urlStr,
			dataType:"json",
			data:{flagpage:"1",tblName:tblname},
			success:function(data){
				grid_disabledfields[g_activeTabID]=data['disabledcols']
				jqOptions[g_activeTabID].colModel=data['colModel']
				get_grid_fields(jqOptions[g_activeTabID])
				hiddenfields(jqOptions[g_activeTabID])
				tblName[g_activeTabID]=tblname;
				jqOptions[g_activeTabID].sortname=sidx;
				if($("#o_Asc").prop("checked")==true){
				     jqOptions[g_activeTabID].sortorder="asc";
				}else{
				     jqOptions[g_activeTabID].sortorder="desc";
				}
				jqOptions[g_activeTabID].url=urlStr
				jqOptions[g_activeTabID].pager="#"+g_activeTabID+' #id_'+page_style+'_pager';
				$("#"+g_activeTabID+" #id_"+page_style+'_grid').jqGrid(jqOptions[g_activeTabID]);
	       }		   
	})
}

/*
function renderTransTbl(p)
{
	var search=window.location.search
	search=search.substring(1)
	var url=$.cookie("url")
	var ischecked=0;
	if($("#id_contain_chl").prop("checked"))
		ischecked=1;
	var urlStr="/iclock/data/transaction/?ot=0&t=empOfTrans.html&p="+p+"&isContainChild="+ischecked
	if (url!="" &&  url!=null)
		urlStr+=url;
	else
		urlStr+='&'+search
	if($.cookie("od")!="" && $.cookie("od")!=null)
		urlStr+=$.cookie("od");
	if($.cookie("op")!="" && $.cookie("op")!=null)
		urlStr+=$.cookie("op");
	if($.cookie("oe")!="" && $.cookie("oe")!=null)
		urlStr+=$.cookie("oe");
	if($.cookie("ot")!="" && $.cookie("ot")!=null)
		urlStr+=$.cookie("ot");
	var text=$.ajax({
		type:"POST",
		url: urlStr,
		async: false
		}).responseText;
	$("#show_tranctions").html(text);
}
*/

function renderAddTransTbl(p)
{
	var url=$.cookie("url")
	var ischecked=0;
	if($("#id_contain_chl").prop("checked"))
		ischecked=1;
	var urlStr="/iclock/data/transactions/?ot=0&Verify=5&t=addTrans.html&p="+p+"&isContainChild="+ischecked
	if (url!="" &&  url!=null)
		urlStr+=url;
	var text=$.ajax({
		type:"POST",
		url: urlStr,
		async: false
		}).responseText;
	$("#show_tranctions").html(text);
}



//综合排班列表
function renderEmpListShiftsTbl(p,page_style ){
//	var emp_tmp=$.cookie("emp")
//	var ct=$.cookie("ComeTime");
//	var et=$.cookie("EndDate");
//	var d=$.cookie("deptIDs")

	var d=$("#show_dept_emp_tree_"+page_style).find("#hidden_selDept").val()
	var ct=$("#id_ComeTime_"+page_style).val();
	var et=$("#id_EndTime_"+page_style).val();

	
	var emp="";
	var ComeTime="";
	var dept="";
	var EndDate="";
	var jqOptions=copyObj(jq_Options)
	if(typeof(emp_tmp)!='undefined'&&emp_tmp!=null && emp_tmp!="")
		emp=emp_tmp;
	if(ct!=null && ct!="")
		ComeTime=ct;
	if(et!=null && et!="")
		EndDate=et;
	if(d!=null && d!="")
		dept="&deptIDs="+d;
	if (dept==""&&p==0)
		dept="&deptIDs=-1";

	if(ComeTime!=""&&EndDate!="")
	{
		savecookie("id_ComeTime_"+page_style,ComeTime);
		savecookie("id_EndDate_"+page_style,EndDate);
		
	}

	var ischecked=0;
	if($("#id_contain_chl_"+page_tab).prop("checked"))
		ischecked=1;
	var queryStr="&startDate="+ComeTime+"&endDate="+EndDate+dept+"&UserIDs="+emp;
	$.cookie("queryStr",queryStr, { expires: 7 });
	
	var urlStr="/iclock/att/searchComposite/?page=1&flag=shift2&"+"&isContainChild="+ischecked+queryStr;
	tblName="shift2"
	$("#id_"+page_style+"grid").jqGrid('GridUnload')  //因该页面标题为动态的
	//$.jgrid.gridUnload("#id_"+page_style+"grid")

				$.ajax({
					type:"GET",
					url:"/iclock/att/searchComposite/?flag=shift2&"+queryStr,
					dataType:"json",
					success:function(json){
						tblName="shift2";
						grid_disabledfields[g_activeTabID]=json['disabledcols']
						jqOptions[g_activeTabID].colModel=json['colModel']
						get_grid_fields(jqOptions[g_activeTabID])
						hiddenfields(jqOptions[g_activeTabID])
						jqOptions.pager='#id_'+page_style+'pager';
						var height=$(".html_content").height()-150;
						jqOptions[g_activeTabID].height=height;
						jqOptions[g_activeTabID].sortname="";
						jqOptions[g_activeTabID].sortorder="desc";
						jqOptions[g_activeTabID].url=urlStr
						$("#id_"+page_style+'grid').jqGrid(jqOptions[g_activeTabID]);
						
					}
				});

	
}


function renderNewAttshifs(p){
	var queryStr_tmp=$.cookie("queryStr")
	var queryStr=""
	var ischecked=0;
	if($("#id_contain_chl").prop("checked"))
		ischecked=1;
	
	if(queryStr_tmp!=null && queryStr_tmp!="")
		queryStr=queryStr_tmp;
	$.ajax({
		type:"POST",
		url:"/iclock/att/calcAttShiftsReport/?p="+p,
		dataType:"json",
		data:queryStr,
		success:function(json){
			datas=json["datas"];
			fieldnames=json["fieldnames"];
			fieldcaptions=json["fieldcaptions"];
			disabledField=json["disableCols"]
			totalRecCnt_attTotal=json["item_count"];
			
			item_from_attTotal=json["from"];
			page_index_attTotal=json["page"];
			page_limit_attTotal=json["limit"];
			page_number_attTotal=json["page_count"];
			
			var html='<table class="autoht" width="100%" border="0">';
			html+='<tr><td colspan="'+fieldnames.length+'" style="border:0px;">'+getPagers("", item_from_attTotal-1, totalRecCnt_attTotal, page_limit_attTotal, page_index_attTotal, page_number_attTotal,3,1)+'</td></tr>'
			html+='<tr><td colspan="'+fieldnames.length+'" style="border:0px;"><table id="tbl"></table></td></tr></table>'
			$("#id_result").html(html);
			showCalcLogDatas();
			$("#id_result").find("li").html("");
			
		}
	});
}

function renderCompositeShiftTbl(p){
	var queryStr_tmp=$.cookie("queryStr")
	var queryStr=""
	var ischecked=0;
	if($("#id_contain_chl").prop("checked"))
		ischecked=1;
	
	if(queryStr_tmp!=null && queryStr_tmp!="")
		queryStr=queryStr_tmp;
	$.ajax({
		type:"POST",
		url:"/iclock/att/searchComposite/?p="+p,
		dataType:"json",
		data:queryStr,
		success:function(json){
			datas=json["datas"];
			fieldnames=json["fieldnames"];
			fieldcaptions=json["fieldcaptions"];
			disabledField=[];
			totalRecCnt_attTotal=json["item_count"];
			
			item_from_attTotal=json["from"];
			page_index_attTotal=json["page"];
			page_limit_attTotal=json["limit"];
			page_number_attTotal=json["page_count"];
			var html='<table class="autoht" width="100%" border="0">';
			html+='<tr><td colspan="'+fieldnames.length+'" style="border:0px;">'+getPagers("", item_from_attTotal-1, totalRecCnt_attTotal, page_limit_attTotal, page_index_attTotal, page_number_attTotal,12,1)+'</td></tr>'
			html+='<tr><td colspan="'+fieldnames.length+'" style="border:0px;"><table id="tbl"></table></td></tr></table>'
			$("#id_shift_details fieldset legend").html("<b><font size='2'>"+gettext("List Shift")+"</font></b>");
			$("#tz").html(html);
			showCalcLogDatas();
		}
	});
}
function renderTotalLeaveCalTbl(p){
	var queryStr_tmp=$.cookie("queryStr")
	var queryStr=""
	var ischecked=0;
	if($("#id_contain_chl").prop("checked"))
		ischecked=1;
	
	if(queryStr_tmp!=null && queryStr_tmp!="")
		queryStr=queryStr_tmp;
	$.ajax({
		type:"POST",
		url:"/iclock/att/calcLeaveReport/?p="+p,
		dataType:"json",
		data:queryStr,
		success:function(json){
			datas=json["datas"];
			fieldnames=json["fieldnames"];
			fieldcaptions=json["fieldcaptions"];
			disabledField=json["disableCols"]
			totalRecCnt_attTotal=json["item_count"];
			
			item_from_attTotal=json["from"];
			page_index_attTotal=json["page"];
			page_limit_attTotal=json["limit"];
			page_number_attTotal=json["page_count"];
			
			var html='<table class="autoht" width="100%" border="0">';
			html+='<tr><td colspan="'+fieldnames.length+'" style="border:0px;">'+getPagers("", item_from_attTotal-1, totalRecCnt_attTotal, page_limit_attTotal, page_index_attTotal, page_number_attTotal,13,1)+'</td></tr>'
			html+='<tr><td colspan="'+fieldnames.length+'" style="border:0px;"><table id="tbl"></table></td></tr></table>'
			$("#id_result").html(html);
			showCalcLogDatas();
			$("#id_result").find("li").html("");
			
		}
	});
}

function renderTotalCalTbl(p){
	var queryStr_tmp=$.cookie("queryStr")
	var queryStr=""
	var ischecked=0;
	if($("#id_contain_chl").prop("checked"))
		ischecked=1;
	
	if(queryStr_tmp!=null && queryStr_tmp!="")
		queryStr=queryStr_tmp;
	$.ajax({
		type:"POST",
		url:"/iclock/att/calcReport/?p="+p,
		dataType:"json",
		data:queryStr,
		success:function(json){
			datas=json["datas"];
			fieldnames=json["fieldnames"];
			fieldcaptions=json["fieldcaptions"];
			disabledField=json["disableCols"]
			totalRecCnt_attTotal=json["item_count"];
			
			item_from_attTotal=json["from"];
			page_index_attTotal=json["page"];
			page_limit_attTotal=json["limit"];
			page_number_attTotal=json["page_count"];
			
			var html='<table class="autoht" width="100%" border="0">';
			html+='<tr><td colspan="'+fieldnames.length+'" style="border:0px;">'+getPagers("", item_from_attTotal-1, totalRecCnt_attTotal, page_limit_attTotal, page_index_attTotal, page_number_attTotal,8,1)+'</td></tr>'
			html+='<tr><td colspan="'+fieldnames.length+'" style="border:0px;"><table id="tbl"></table></td></tr></table>'
			$("#id_result").html(html);
			showCalcLogDatas();
			$("#id_result").find("li").html("");
			
		}
	});
}
function renderDailyTotalCalTbl(p){
	var queryStr_tmp=$.cookie("queryStr")
	var queryStr=""
	var ischecked=0;
	if($("#id_contain_chl").prop("checked"))
		ischecked=1;
	
	if(queryStr_tmp!=null && queryStr_tmp!="")
		queryStr=queryStr_tmp;
	$.ajax({
		type:"POST",
		url:"/iclock/att/dailycalcReport/?p="+p,
		dataType:"json",
		data:queryStr,
		success:function(json){
			datas=json["datas"];
			fieldnames=json["fieldnames"];
			fieldcaptions=json["fieldcaptions"];
			disabledField=json["disableCols"]
			
			totalRecCnt_dailyattTotal=json["item_count"];
			item_from_dailyattTotal=json["from"];
			page_index_dailyattTotal=json["page"];
			page_limit_dailyattTotal=json["limit"];
			page_number_dailyattTotal=json["page_count"];
			
			var html='<table class="autoht" width="100%" border="0">';
			html+='<tr><td colspan="'+fieldnames.length+'" style="border:0px;">'+getPagers("", item_from_dailyattTotal-1, totalRecCnt_dailyattTotal, page_limit_dailyattTotal, page_index_dailyattTotal, page_number_dailyattTotal,9,1)+'</td></tr>'
			html+='<tr><td colspan="'+fieldnames.length+'" style="border:0px;"><table id="tbl"></table></td></tr></table>'
			$("#id_result").html(html);
			showCalcLogDatas();
			$("#id_result").find("li").html("");
		}
	});
}
function renderEmpsTbl(p){
	var queryStr_tmp=$.cookie("query_emp")
	var queryStr=""
	if(queryStr_tmp!=null && queryStr_tmp!="")
		queryStr=queryStr_tmp;
	var text=$.ajax({
	        type:"POST",
	        url: queryStr+'&p='+p,
	        async: false
	        }).responseText;
	$("#userid").html(text);
}
function renderDeptsTbl(p){
	var queryStr_tmp=$.cookie("query_dept")
	var queryStr=""
	if(queryStr_tmp!=null && queryStr_tmp!="")
		queryStr=queryStr_tmp;
	var text=$.ajax({
	        type:"POST",
	        url: queryStr+'&p='+p,
	        async: false
	        }).responseText;
	$("#deptid").html(text);

}

function showCalcLogDatas()
{
	var html="";
	tbl_head='<thead><tr>';
	for(var i=1;i<fieldcaptions.length;i++)  //显示标题的字段别名 后台传送 aliasnames
	{	
		if(isDisabled(fieldnames[i]))
			continue;
		tbl_head+='<th>'+fieldcaptions[i]+'</th>'
	}
	html+=tbl_head+'</tr></thead>';
	var tbl_body='<tbody>';
	for(var i=0;i<datas.length;i++)
	{	
		var row_html='<tr class=row'+(i%2+1)+'>';
		
		for(j=0;j<fieldnames.length;j++)
		{
			if(isDisabled(fieldnames[j]) ||fieldnames[j]=="userid")
				continue;
			row_html+='<td>'+(typeof(datas[i][fieldnames[j]])=='undefined'?'':datas[i][fieldnames[j]])+'</td>'
		}
		row_html+='</tr>'
		tbl_body+=row_html;
	}
	html+=tbl_body+'</tbody>';
	$("#tbl").html(html)

}
function renderDevOffset(p){
		$.ajax({type: "POST",
		url: "/iclock/data/iclock/",
		data:"rows=30&page="+p+"&sidx=&sord=asc",
		dataType:"json",
		success: function(retdata){
				if(retdata.records>0){	
					$.unblockUI();
				}
				$("#gbox_id_grid").css('overflow-y','auto').css('height','394px').html(showBox(retdata.rows))
				$("#pages").html(showoffset(retdata,30,p))
			}
		});
		$.cookie("page",p)
}
function pageUrl(pgNum,page_style) {
	if(typeof(page_style)=='undefined')
		return "<a href='"+getQueryStr(window.location.href, ["p"], "p="+pgNum)+"'>"+pgNum+"</a> ";
	else if(page_style==0)
		return "<a href='#' onclick='renderTransTbl("+pgNum+");'>"+pgNum+"</a> ";
	else if(page_style==1)
		return "<a href='#' onclick='renderEmpTbl("+pgNum+");'>"+pgNum+"</a> ";
	else if(page_style==2)
		return "<a href='#' onclick='renderDevsTb("+pgNum+");'>"+pgNum+"</a> ";
	else if(page_style==3)
		return "<a href='#' onclick='renderNewAttshifs("+pgNum+");'>"+pgNum+"</a> ";
	else if(page_style==5)
		return "<a href='#' onclick='renderEmpShiftsTbl("+pgNum+");'>"+pgNum+"</a> ";
	else if(page_style==6)
		return "<a href='#' onclick='renderEmpTmpShiftsTbl("+pgNum+");'>"+pgNum+"</a> ";
	else if(page_style==8)
		return "<a href='#' onclick='renderTotalCalTbl("+pgNum+");'>"+pgNum+"</a> ";
	else if(page_style==9)
		return "<a href='#' onclick='renderDailyTotalCalTbl("+pgNum+");'>"+pgNum+"</a> ";
	else if(page_style==12)
		return "<a href='#' onclick='renderCompositeShiftTbl("+pgNum+");'>"+pgNum+"</a> ";
	else if(page_style==13)
		return "<a href='#' onclick='renderTotalLeaveCalTbl("+pgNum+");'>"+pgNum+"</a> ";
	else if(page_style==15)
		return "<a href='#' onclick='renderAddTransTbl("+pgNum+");'>"+pgNum+"</a> ";
	else if(page_style==16)
		return "<a href='#' onclick='renderDeptsTbl("+pgNum+");'>"+pgNum+"</a> ";
	else if(page_style==17)
		return "<a href='#' onclick='renderEmpsTbl("+pgNum+");'>"+pgNum+"</a> ";
	else if(page_style==18)
		return "<a href='#' onclick='renderDevOffset("+pgNum+");'>"+pgNum+"</a> ";
	else if(page_style==19)
		return "<a href='#' onclick='renderEmpTbl_Radio("+pgNum+");'>"+pgNum+"</a> ";

	else 
		return "<a href='#' onclick='renderResultTbl("+pgNum+","+page_style+");'>"+pgNum+"</a> ";
	
}

function gotoPage(e,page_style,flag)
{
	var keynum;
	var keychar;
	var numcheck;
	if(window.event) // IE
	{
		keynum = e.keyCode;
	}
	else if(e.which) // Netscape/Firefox/Opera
	{
		keynum = e.which;
	}
	if(13!=keynum) return true;
	if(typeof(flag)=='undefined')
		pnum=parseInt($('#id_pageNumInput').val());
	else
		pnum=parseInt($('#id_pageNumInput1').val());
	if(isNaN(pnum)) pnum=1;
	if(typeof(page_style)=='undefined')
		window.location.href=getQueryStr(window.location.href, ["p"], "p="+pnum);
	else if(page_style==0)
		renderTransTbl(pnum);
	else if(page_style==1)
		renderEmpTbl(pnum);
	else if(page_style==3)
		renderNewAttshifs(pnum)
	else if(page_style==5)
		renderEmpShiftsTbl(pnum);
	else if(page_style==6)
		renderEmpTmpShiftsTbl(pnum);
	else if(page_style==8)
		renderTotalCalTbl(pnum);
	else if(page_style==9)	
		renderDailyTotalCalTbl(pnum);
	else if(page_style==12)	
		renderCompositeShiftTbl(pnum);
	else if(page_style==13)	
		renderTotalLeaveCalTbl(pnum);
	else if(page_style==15)	
		renderAddTransTbl(pnum);
	else if(page_style==16)	
		renderDeptsTbl(pnum);
	else if(page_style==17)	
		renderEmpsTbl(pnum);
	else if(page_style==18)
		renderDevOffset(pnum);
	else if(page_style==19)
		renderEmpTbl_Radio(pnum)
	else
		renderResultTbl(pnum,page_style);
	
	return false;
}

function getPagers(title, startRecord, totalRecords, pageSize, currPg, totPg,page_style,flag) {
    var last = startRecord + pageSize;
    if (last > totalRecords) {
        last = totalRecords;
    }
	
	if(title!="")
		title+=":"
	var s=title+ (startRecord + 1) + "-" + last + $.validator.format(gettext('(total {0})'),totalRecords)+ "&nbsp;&nbsp;";
	
	
	if (totPg<=1)
	{
		if(totalRecords>0)
			return $.validator.format(gettext('total {0}'),totalRecords)
		else
			return gettext('None')
	}
	if(typeof(flag)=='undefined')
		pf=gettext('Page:')+" <input id=id_pageNumInput value="+currPg+" type='text' onkeypress='return gotoPage(event,"+page_style+")' style='width: 35px !important;'> "
    else
		pf=gettext('Page:')+" <input id=id_pageNumInput1 value="+currPg+" type='text' onkeypress='return gotoPage(event,"+page_style+",1)' style='width: 35px !important;'> "
    if (currPg < 5) {
        s += pf;
        for (i = 1; i <= totPg && i <= currPg + 1; i++) {
            if (i == currPg) {
                s += "<font color=red>" + i + "</font> ";
            } else {
                s += pageUrl(i,page_style);
            }
        }
    } else {
        s += pf + pageUrl(1,page_style) + "... " + pageUrl((currPg - 1),page_style) + " <font color=red>" + currPg + "</font> " + (currPg == totPg ? "" : pageUrl((currPg + 1),page_style));
    }
    if (totPg - 3 <= currPg) {
        for (i = currPg + 2; i <= totPg; i++) {
            s += pageUrl(i,page_style);
        }
    } else {
        s += "... " + pageUrl(totPg,page_style);
    }
    return s;
}
function renderReport(fieldCaption,fieldValues,dis){
    var disableCol="";
    disableCol=","+dis.toString()+",";
    htmlHead="<thead><tr>"
    for(var i in fieldCaption)
    {
        if(-1==disableCol.indexOf(","+i+","))
            htmlHead+="<th>"+fieldCaption[i]+"</th>"
    }
    htmlHead+="</tr></thead>"
    var htmlBody=""
    for(var i in fieldValues){
        htmlBody+="<tr class=row"+(i%2+1)+">"
        for(var j in fieldValues[i]){
            if(-1==disableCol.indexOf(","+j+",")){
                htmlBody+="<td>"+fieldValues[i][j]+"</td>"
            }
       }
       htmlBody+="</tr><tr></tr>"
    }
    $("#tbl").html(htmlHead+htmlBody);
}

function removeNone(s){return s=="None"?"":s}
function renderTbl(data, options)
{	
	var disableCol="";
	if(options.disableCols) disableCol=","+options.disableCols.toString()+",";
	for(var row in data)
	if(typeof sortData=="function") data.sort(sortData);
	var pagers=''
	var tpage='';
	var tpage2='';
	var item_count=0;
	var sel=getSelected(data, options.keyFieldIndex);
	for(var i in data)
	if((typeof filterData!="function") || filterData(data[i]))
	{
		var colI=0;
		var key=data[i][options.keyFieldIndex];
		var apage='';
/*
		if(options.canSelectRow)
			apage+="<tr class=row"+(i%2+1)+" onclick='SelectRow(this);'>"+
				(options.showSelect?"<td class='class_select_col'><input type='checkbox' class='class_select' onclick='showSelected();' id='id_row_"+i+"' "+((sel.ret+"&").indexOf('&K='+key+'&')>=0?"checked":"")+"/></td>":"");
		else
			apage+="<tr class=row"+(i%2+1)+">"+
				(options.showSelect?"<td class='class_select_col'><input type='checkbox' class='class_select' onclick='showSelected();' id='id_row_"+i+"' "+((sel.ret+"&").indexOf('&K='+key+'&')>=0?"checked":"")+"/></td>":"");
*/
		for(j in data[i])
			if(-1==disableCol.indexOf(","+j+","))
			{
				colI+=1;
				var colData=data[i][j];
				if(typeof colData=="function")
					colData=colData(data[i]);
				else
					colData=removeNone(colData);
				if(options.canEdit && colI==1) //window.document.location.pathname
					apage+="<td><a class='can_edit' href='"+key+"/'>"+colData+"</td>";
				else
					apage+="<td>"+colData+"</td>";
			}
		apage+="</tr>";
		tpage+=apage;
		if(item_count%20==0)
		{
			tpage2+=tpage;
			tpage='';
			if(item_count%100==0)
			{
				pagers+=tpage2;
				tpage2='';
			}
		}
		item_count+=1;
	}
	pagers+=(tpage2+tpage);
	$("#"+options.pagerId).html(getPagers(options.title, item_from-1, totalRecCnt, page_limit, page_index, page_number));

	$("#"+options.tblId).html("<thead><tr>"+(options.showSelect?"<th width='15px' class='class_select_col'><input type='checkbox' class='class_select_all' onclick='check_all_for_row(this.checked);' /> </th>":"")+options.tblHeader+"</tr></head><tbody>"+pagers+'</tbody>');
	if(options.showSelect && item_count>0)
	{
		html='<div id="id_select_div">&nbsp;&nbsp;&nbsp;'+gettext('Selected:')+' <span id="id_selected_count">0</span></div>';
		$(".selectedDataOp #id_defSelectDataOp").html(html+'<div>&nbsp;&nbsp;&nbsp;</div>');
		html="";
		if(typeof extraBatchOp=="object")
		{
			for(var i in extraBatchOp)
			{
				if(extraBatchOp[i].action)
					html+="<li><a href='javascript: batchOp("+i+")'>"+extraBatchOp[i].title+"</a></li>";
				else
					html+="<li class='disablemenu'><div >&nbsp;"+extraBatchOp[i].title+"</div></li>";
			}
		
		}
		if(html=='')
		  $("#op_menu_div").hide();
		else
		{
			$("#op_menu").html(html);
			$("#op_menu_div").css("display","inline");
		}
	}
	else
		$("#id_defSelectDataOp").html("");
	if (window.hide_batchOp) hide_batchOp();
	if (window.last_action) last_action();
}

//function SelectRow(id) {
//alert(id);
//	var data=[16,'测试',2000-01-01,2099-12-31,1,'周',1];
//	if(typeof(PageSelectRow)=='function') PageSelectRow(data);
//}

function showSelected() {
    var c = 0;
    $.each($(".class_select"),function(){
			var tr=this.parentNode.parentNode;
			if(tr.nodeName=="TD") tr=tr.parentNode;
			if(this.checked) {
				$(tr).addClass("trSelected");
				c+=1;
			}
			else
				$(tr).removeClass("trSelected");
			})
    $("#id_selected_count").html("" + c);
}

function check_all_for_row(checked) {
    if (checked) {
        $(".class_select").attr("checked", "true");
    } else {
        $(".class_select").removeAttr("checked");
    }
    showSelected();
}
function showSelected_report(){
    var c = 0;
    $.each($(".class_select_report"),function(){
			if(this.checked) c+=1;})
    $("#selected_count").html("" + c);
}

function check_all_for_row_report(checked) {

    if (checked) {
        $(".class_select_report").attr("checked", "true");
    } else {
        $(".class_select_report").removeAttr("checked");
    }
    //showSelected_report();
}
function getSelected_report() {
	var ids=[];
	$.each($(".class_select_report"),function(){
			if(this.checked)
				ids.push(this.alt)
	});
	return ids;
}

function getSelected(keyIndex,itemCanSelect,grid_page){
	var ret="";
	var c=0, selCount=0;
	var ss=[];
	var rr=[]
	if(grid_page==undefined){
		grid_page=tblName[g_activeTabID];
	}
	var data=$("#id_grid_"+grid_page).jqGrid('getGridParam','selarrrow');
	for(i=0; i<data.length; i++)
	{
			if (typeof data[i]=='undefined') continue
			r=$("#id_grid_"+grid_page).jqGrid("getRowData",data[i]);
			selCount++;
			if(typeof itemCanSelect!="function" || itemCanSelect(r))
			{
				c++;
				var key=$("#id_grid_"+grid_page).jqGrid("getCell",data[i],keyIndex);
				
				ret+="&K="+stripHtml(key);
				if ($.isFunction(window['strOfData_'+tblName[g_activeTabID]]))
				{
					rr.push(window['strOfData_'+tblName[g_activeTabID]](r,grid_page))
				}
				// if(typeof strOfData=="function")
				// {
					// rr.push(strOfData(r,grid_page))
				// }
				ss.push(data[i]);
			}
	}

	var result={count: c, selectedCount: selCount, ret: ret, ss: ss,rr:rr};
	return result;
}

function formatArray(a)
{	if(a.length<11) return a.join("\n");
	var ret='';
	var c=0;
	var aa=[];
	for(var i in a)
	{
		c++;
		if(c>10) break;
		aa.push(a[i]);
	}
	return aa.join("\n")+"\n... ...";
}
function formatArrayEx(a)
{	if(a.length<11) return a.join(",");
	var ret='';
	var c=0;
	var aa=[];
	for(var i in a)
	{
		c++;
		if(c>10) break;
		aa.push(a[i]);
	}
	return aa.join(",")+"...";
}

function batchOp(action, itemCanSelect, opName,grid_page,postUrl)   //grid_page参数用来兼容不同grid键值,g_url不合适时传送postUrl
{

	if(grid_page==undefined){
		grid_page=tblName[g_activeTabID];
	}
	
	if(postUrl==undefined)
	postUrl=g_urls[g_activeTabID]
	if(typeof action=="number")
	{
		if(!itemCanSelect) itemCanSelect=extraBatchOp[action].itemCanBeOperated;
		if(!opName) opName=extraBatchOp[action].title;
		action=extraBatchOp[action].action;
	}
	else
		if(!opName) opName=gettext('Operation')
	var url=""

	if($("input[name='showStyle']:checked").val()==1){
		url=tblSelect(itemCanSelect)
	}else{
		url=getSelected(options[g_activeTabID].edit_col, itemCanSelect,grid_page);
	}
	if(url.selectedCount==0)
		alert($.validator.format(gettext('Please Select {1} to {0}'),opName,options[g_activeTabID].title))
	else if(url.count==0)
		alert($.validator.format(gettext('{1} disallowed for {0}!'),options[g_activeTabID].title,opName))
	else
	{
		var a='';
		if(typeof action=="function")
			a=action(url);
		else if(window.confirm($.validator.format(gettext('Will {2} the {0} {1} ?'),url.count,options[g_activeTabID].title,opName)+
					(typeof ActionHint=="function"?ActionHint(action,opName):"")+
					"\n\n"+formatArray(url.rr)+"\n\n"+gettext('Please Confirm!')))
					
			a=action
		if(a)
		{
			//window.location.href=getQueryStr(window.location.href, ["action"],a+url.ret);
			$.blockUI({title:'',theme: true ,baseZ:10000,message: '<h1><img src="/media/img/loading.gif" /> <br>'+ gettext('Please wait...')+'</br></h1>'});
			$.ajax({type: "POST",
					url: postUrl.split("?")[0]+a,//getQueryStr(window.location.href, ["action"],a),
					data: url.ret,
					dataType:"json",
					success: actionSuccess,
					error: function(request){
						alert($.validator.format(gettext('{0} failed!\n\n{1}'), opName, request.statusText)); $.unblockUI(); 
						//$('body').html(request.responseText);
						}
					});
		}
	}

}
function tblSelect(itemCanSelect){
	var ret="";
	var c=0, selCount=0;
	var ss=[];
	var rr=[];
	$("#"+g_activeTabID+" .class_select:checked").each(function(i){
		var dev=devs[i]
		ss.push(i+1);
		ret+="&K="+stripHtml(this.name)
		rr.push(stripHtml(this.name+" "+this.value))
		if(typeof itemCanSelect!="function" || itemCanSelect(dev)){
			c++
		}
		selCount=ss.length
	})
	var result={count: c, selectedCount: selCount, ret: ret, ss: ss,rr:rr};
	return result;
}
function searchKey(keyData)
{
	for(var i in data)
		if(keyData==data[i][options.keyFieldIndex]) return i;
	return -1;
}

function $s(s, len)
{
	if(!len) len=100
	if(s.length>len) return s.substr(0,len)+' ...';
	return s;
}

function $t(t){	return t.substr(0,19)}
function $t0(t){ return t.substr(5,14)}

function createSubmitButton()
{
	str = "<div style='text-align:right; margin-top: 10px; margin-right: 20px;margin-bottom:10px;'>"
	str += '<input type="button" value="'+gettext('Submit')+'" id="btnShowOK"  class="btnOKClass">&nbsp;&nbsp;&nbsp;'
	str += '<input type="button" value="'+gettext('Cancel')+'" id="btnShowCancel" onclick="javascript:$(\'#id_form\').remove();$(\'#dept_emp_dialog\').dialog(\'destroy\');" class="btnCancelClass">&nbsp;&nbsp;&nbsp;'
	str += "</div>"
	return str
}

function createTimeRangeEdit()
{
	return "<table style='text-align: center;'>"
		+  "<tr><td class='label'>"+gettext('Start Time')+"</td><td><input id='id_date_range_from' width=19 class='vDateField' /></td>"
		+  "<td class='label'>"+gettext('End Time')+"</td><td><input id='id_date_range_to' width=19 class='vDateField' /></td></tr>"
		+  "</table><p></p><hr />"
}
function createDateRangeEdit()
{
	return "<table style='text-align: center;'>"
		+  "<tr><td class='label'>"+gettext('Start Time')+"</td><td><input id='id_date_range_from' width=11 class='vDateOnlyField' /></td></tr>"
		+  "<tr><td class='label'>"+gettext('End Time')+"</td><td><input id='id_date_range_to' width=11 class='vDateOnlyField' /></td></tr>"
		+  "</table><div>&nbsp;</div><hr />"
}

function createDateEdit(index)
{
	return "<table style='text-align: center;border:0;'>"
		+  "<tr><td class='label'>"+gettext('End Time')+"</td><td><input id='id_endTime"+index+"' width=19 /></td></tr>"
		+  "</table><div></div>"
}

function createCheckBoxHtml(arr, colCount)
{
	str = "<table border=0>"
	for(var row in arr)
	{
		arrRow = arr[row].split(":");
		if (colCount && colCount == 1)
		{
			str += "<tr>"
				+ '<td width="20px"><input type="checkbox" id="chkShow_' + row + '" value="' + arrRow[0] + '" /></td>'
				+ "<td width='150px' align='left'><b>" + arrRow[1] + ":</b></td>"
				+ '<td width="260px">'
				+ '<span id="spanShow_' + row + '_value"></span></td>'
				+ "</tr>"
		}
		else
		{
			str += (parseInt(row) % 2 ? "" : "<tr>")
				+ '<td width="20px"><input type="checkbox" id="chkShow_' + row + '" value="' + arrRow[0] + '" /></td>'
				+ "<td width='80px' align='left'><b>" + arrRow[1] + ":</b></td>"
				+ '<td width="130px">'
				+ '<span id="spanShow_' + row + '_value"></span></td>'
				+ (parseInt(row) % 2 ? "</tr>" : "")
		}
	}
	str += "</table>"
	return str;
}

function createSelectHtml(arr, colCount)
{
	str = '<select name="sltShow" id="sltShow" style="width:360px;">';
	str += '<option value="">'+gettext('--- select ---')+'</option>'
	for(var row in arr)
	{
		if (colCount && colCount == 1)
		{
			str += '<option value="' + arr[row] + '">' + arr[row] + '&nbsp; </option>';
		}
		else
		{
			arrRow = arr[row].split(" ");
			str += '<option value="' + arrRow[0] + '">' + arrRow[1] + '&nbsp; ( ' + arrRow[0] + ' )</option>';
		}
	}
	str +='</select>';
	return str;
}

function IsSupportNewCSS()
{
	ua = navigator.userAgent;
	s = "MSIE";
	if ((i = ua.indexOf(s)) >= 0) {
		var version = parseFloat(ua.substr(i + s.length));
		if(version<7) return 0;
	}
	return 1;
}

function valiDate(str){                
    var reg = /^(\d+)-(\d{1,2})-(\d{1,2})$/;
    var r = str.match(reg);
    if(r==null)return false;
    r[2]=r[2]-1;
    var d= new Date(r[1], r[2],r[3]);
    if(d.getFullYear()!=r[1])return false;
    if(d.getMonth()!=r[2])return false;
    if(d.getDate()!=r[3])return false;
    return true;
}
function valiDateTimes(str){
  //   var reg = /^(\d+)-(\d{1,2})-(\d{1,2}) (\d{1,2}):(\d{1,2}):(\d{1,2})$/;
     var reg = /^(\d+)(-|\/)(\d{1,2})\2(\d{1,2}) (\d{1,2}):(\d{1,2}):(\d{1,2})$/; 
     var r = str.match(reg);
     if(r==null)return false;
     r[2]=r[2]-1;
     var d= new Date(r[1], r[2],r[3], r[4],r[5], r[6]);
     if(d.getFullYear()!=r[1])return false;
	 if(d.getMonth()!=r[2])return false;
     if(d.getDate()!=r[3])return false;
     if(d.getHours()!=r[4])return false;
     if(d.getMinutes()!=r[5])return false;
     if(d.getSeconds()!=r[6])return false;
     return true;
 }

//快速备份数据库
function QuiklybackupData(){
    var block_html="<div class='dialog' style='width:400px;'>"
   						+ 		"<div class='dheader'><span>"+gettext("QuiklybackupData")+"</span><span class='close' onclick='javascript:$.unblockUI();'></span></div>"
   						+ 		"<div class='dcontent'style='height:200px;'>"
						+       "<fieldset  style='height:175px;'><legend>备份路径</legend>"
					    +       "<table cellpadding='10'><tr><td>"
						+       "<input type='radio' name='back_type' id='been' checked>使用备份与恢复中配置的保存路径"
						+       "<br></br><input type='radio' id='definepath' name='back_type'>自定义保存路径"
						+		"</tr></td><tr><td>"
						+       "<div style='display:none' id='pathvisit'><input type='file' name='backupPath' id='backupPath'/></div>"
						+		"</tr></td><tr><td>"
						+		"<input  name='button' id='id_backup_submit' value='"+gettext('Submit')+"' type='button' class='btnOKClass' />&nbsp;&nbsp;&nbsp;"
						+		"<input type='button' value='"+gettext('Cancel')+"' class='btnCancelClass' onclick='$.unblockUI();'>&nbsp;&nbsp;&nbsp;"
						+       "</td></tr></table>"
						+       "</fieldset>"
				        +       "</div>"
					+"</div>"
    $.blockUI(block_html);
//	blockUI_center();
	$("#definepath").click(function(){
	      $("#pathvisit").css("display","");
	})
	$("#been").click(function(){
	      $("#pathvisit").css("display","none");
	})
	$("#backupPath").change(function(){
	   alert($(this).val())
	   //$(this).val($(this).val().substring(0,10));
	})
	
	$("#id_backup_submit").click(function(){
	     // $.blockUI();
	      $.ajax({
		        type:"POST",
		        url:"/iclock/backup/mysql/",
				dataType:"json",
				data:{"backupPath":$("#backupPath").val()},
				success:function(json){
				    $.blockUI("<div class='dialog' style='width:400px;'>"
						+ 		"<div class='dheader'><span>"+gettext("QuiklybackupData")+"</span><span class='close' onclick='javascript:$.unblockUI();'></span></div>"
						+ 		"<div class='dcontent'style='height:350px;'>"
					    +       "<div>数据备份成功<br></br><input type='button' value='Close' onclick='$.unblockUI();'></div>"
						+     "</div></div>");
				    blockUI_center();
				}
		  })
	})
	
}


function showResponse(ret, statusText, xhr, $form){
	$("#id_message").css("display","block")
	$("#id_message").html(unescapeHTML(ret.message))
	reloadData();
	$.unblockUI();
	

/*
	if(responseText.indexOf("result=0")!=-1){
		if(typeof reloadData=="function"){
			reloadData();
		}
		var info=gettext("Data has been imported successfully");
	}else {
		var info=gettext("occur error!");
	}
	$("#id_message").html(info).css('color','red');
*/
}



function importDepartment(){
	var block_html=
				"<form id='frmComebackDb' name='frmComebackDb' method='POST' action='/iclock/tasks/import_dept/' enctype='multipart/form-data'>"
	           +"<table>"
					+'<tr><td cols="3">&nbsp;</td></tr>'
					+'<tr><th>'+gettext("Support Upload Fields" )+'</th><th>'+gettext("Index in File" )+'</th></tr>'
					+'<tr><td><input id="id_DeptNumber" name="DeptNumber" type="checkbox" checked disabled/>'+gettext("department number")+'</td>'
					+'<td><input name="DeptNumber2file" id="id_DeptNumber2file" type="text"  style="width:100px !important;"/></td>'
					+'</tr>'
					+'<tr><td><input id="id_DeptName" name="DeptName"  type="checkbox" checked disabled/>'+gettext("department name")+'</td>'
					+'<td><input name="DeptName2file" id="id_DeptName2file" type="text" style="width:100px !important;"/></td>'
					+'</tr>'
					+'<tr><td><input id="id_supdeptnum" name="supdeptnum" type="checkbox" checked disabled/>'+gettext("parent")+'</td>'
					+'<td><input name="supdeptnum2file" id="id_supdeptnum2file" type="text"  style="width:100px !important;"/></td>'
					+'</tr>'

					+'<tr><td><input id="id_DeptAddr" name="DeptAddr" type="checkbox"  />'+gettext("DeptAddr")+'</td>'
					+'<td><input name="DeptAddr2file" id="id_DeptAddr2file" type="text"  style="width:100px !important;"/></td>'
					+'</tr>'
					+'<tr><td><input id="id_DeptPerson" name="DeptPerson" type="checkbox" />'+gettext("DeptPerson")+'</td>'
					+'<td><input name="DeptPerson2file" id="id_DeptPerson2file" type="text"  style="width:100px !important;"/></td>'
					+'</tr>'
					+'<tr><td><input id="id_DeptPhone" name="DeptPhone" type="checkbox" />'+gettext("DeptPhone")+'</td>'
					+'<td><input name="DeptPhone2file" id="id_DeptPhone2file" type="text"  style="width:100px !important;"/></td>'
					+'</tr>'
					
					+'<tr style="color:red;"><td><input id="id_whatrowid" name="whatrowid" type="checkbox" checked disabled/>'+gettext("whatrowid")+'</td>'
					+'<td><input name="whatrowid2file" id="id_whatrowid2file" type="text" value="1"  style="width:100px; color:red; !important;"/>'+gettext("行开始导入")+'</td>'
					+'</tr>'
					
				+'<tr><td cospan="2"><input  type="hidden" name="fields" id="id_fields"/></td></tr>'		
					+'</table>'
					+'<div style="float:left;">'
					+gettext("Upload file location")
					+'<div>'
					+"<input type='file' class='text' value='' name='fileUpload' id='fileUpload'/><br />"
					+'<br /><label>'+gettext("Support three formats files,one is text which is Tab Separated ,another is csv which is Comma Separated,the last one is xls which is Excel standard format")+'</label>'
					+'<br /><label>'+gettext("DeptID is char")+'</label>'
					+'<br /><label>'+gettext("DeptName\'s length is 40")+'</label>'
					+'<br /><label>'+gettext("parent should be exist in department")+'</label>'
					+'<br />'
					//+'<div><input class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only"  type="submit" value='+gettext("Submit")+' >'
					//+'<input id="btnCancel" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" type="button" value='+gettext("Cancel")+' ></div>'
					+'<div id="id_message"></div>'
					+'</div></div></form>'

		$(block_html).dialog({modal:true,
					resizable:false,
					width: 600,
					height:570,
					buttons:[{id:'btnShowOK',text:gettext("Submit"),click:function(){$(this).submit();}},{text:gettext("Cancel"),click:function(){$(this).dialog("close"); }}],

							  title:gettext("import department data"),
							  close:function(){$(this).dialog("destroy");}	
							});
		//$("#btnCancel").click(function(){$("#frmComebackDb").remove();});
		var opts = { 
				url:'/iclock/tasks/import_dept/',
				dataType:'json',
				success: showResponse
			};
		
		var fields=["DeptNumber","DeptName","supdeptnum","DeptAddr","DeptPerson","DeptPhone"];
		for(var i=0;i<fields.length;i++){
			value=$.cookie("dept"+fields[i]+"_value");
			if(value)
				$("#id_"+fields[i]+"2file").val(value);
			else
				$("#id_"+fields[i]+"2file").val((i+1));
		}

		$('#frmComebackDb').submit(function() { 
			$(".errorlist").css("display","none");
			var fields=["DeptNumber","DeptName","supdeptnum","DeptAddr","DeptPerson","DeptPhone"];
			$("#id_fields").val(fields);
			for(var i=0;i<fields.length;i++){
				 isChecked=($("#id_"+fields[i]).prop("checked"))?true:false
				 value=$("#id_"+fields[i]+"2file").val();
				 value1=$("#id_whatrowid2file").val();
				 if(isChecked && value==""||value.match(/^[1-9]\d*$/)==null){
					$("#id_"+fields[i]+"2file").after("<ul class='errorlist'><li>Please input selected field index in file</li></ul>");
					return false;
				 }
				if(value1==""||value1.match(/^[1-9]\d*$/)==null){
					$("#id_whatrowid2file").after("<ul class='errorlist'><li>Please input selected field index in file</li></ul>");
					return false;
				
				}
				 $.cookie("dept"+fields[i]+"_checked",isChecked, { expires: 7 });
				 $.cookie("dept"+fields[i]+"_value",value, { expires: 7 });
			}
			var flag=checkForm();
			if(flag){
				$(this).ajaxSubmit(opts); 
			}
			return false;
		});

}
function checkForm()
{
	var fileName = document.frmComebackDb.fileUpload.value;
	var postfix = fileName.substring(fileName.length - 4).toUpperCase();
	if ((postfix !=".TXT") && (postfix !=".CSV")&& (postfix !=".XLS")&& (postfix !="XLSX"))
	{
		alert(gettext('Please select .txt or .csv or .xls file!'));
		return false;
	}

	if(($("#id_defaultdeptid").prop("checked")==false)&&($("#departments").val()=="")){
		if($("#id_nodept").prop("checked")==false)
		{
			alert(gettext("Please select department or checked department number field!"));
			return false;
		}
	}
	var fields=	$("#id_fields").val().split(',');
    for(var i=0;i<fields.length;i++){
         var isChecked=$("#id_"+fields[i]).prop("checked")?true:false;
         var value=$("#id_"+fields[i]+"2file").val();
        if(isChecked && value==""){
            $("#id_"+fields[i]+"2file").after("<ul class='errorlist'><li>"+gettext('Please input selected field index in file' )+"</li></ul>");
            return false;
         }
    }
	return true;
}

function importIclock(){
	var block_html=""
		+"<form id='frmComebackDb_iclock' name='frmComebackDb' method='POST' action='/iclock/tasks/importclock/' enctype='multipart/form-data'>"
		+"<table>"
			+"<tr>"
				+"<td style='width:65%;'>"
					+"<table>"
						+"<tr><th>"+gettext("Support Upload Fields" )+"</th><th width='20'>&nbsp;</th><th>"+gettext("Index in File" )+"</th></tr>"
						+"<tr><td><input id='id_SN' name='SN'  type='checkbox' checked disabled/>序列号</td>"
						+"<td>&nbsp;</td>"
						+"<td><input name='SN2file' id='id_SN2file' type='text' style='width:100px !important;'/></td>"
						+"</tr>"
						+"<tr><td><input id='id_Alias' name='Alias' type='checkbox'/>设备别名</td>"
						+"<td>&nbsp;</td>"
						+"<td><input name='Alias2file' id='id_Alias2file' type='text' style='width:100px !important;'/></td>"
						+"</tr>"
						+"<tr><td><input id='id_DeptID' name='DeptID' type='checkbox' checked disabled/>"+gettext("单位编号" )+"</td>"
						+'<td>&nbsp;</td>'
						+'<td><input name="DeptID2file" id="id_DeptID2file" type="text"  style="width:100px !important;"/></td>'
						+'</tr>'
						+'<tr><td><input id="id_City" name="City" type="checkbox"/>所在位置</td>'
						+'<td>&nbsp;</td>'
						+'<td><input name="City2file" id="id_City2file" type="text"  style="width:100px !important;"/></td>'
						+'</tr>'
						//+"<tr><td><input id='id_GCard' name='GCard' type='checkbox'/>3G卡号</td>"
						//+'<td>&nbsp;</td>'
						//+'<td><input name="GCard2file" id="id_GCard2file" type="text"  style="width:100px !important;"/></td>'
						//+'</tr>'
						+'<tr><td cospan="3"><input  type="hidden" name="fields" id="id_fields"/></td></tr>'		
					+'</table>'
				+'</td>'
				+'<td style="vertical-align:top;">'
					+"<table>"
						+"<tr><td cospan='2'>"
							+gettext("Upload file location")
						+"</td></tr>"
						+"<tr><td cospan='2'>"
							+"<input type='file' class='text' value='' name='fileUpload' id='fileUpload'/>"
						+"</td></tr>"
						+'<tr style="color:red;"><td><input id="id_whatrowid" name="whatrowid" type="checkbox" checked disabled/>'+gettext("whatrowid")
							+'<input name="whatrowid2file" id="id_whatrowid2file" type="text" value="1"  style="width:50px; color:red; !important;"/>'+gettext("行开始导入")+'</td>'
						+'</tr>'
						+"<tr>"
							+"<td cospan='2'>"
							+"</td>"
						+"</tr>"
						+"<tr><td cospan='2'>"
							+'<label>'+gettext("Support three formats files,one is text which is Tab Separated ,another is csv which is Comma Separated,the last one is xls which is Excel standard format")+'</label>'
						+"</td></tr>"
						+"<tr><td cospan='2'>"
							+'<div id="id_message"></div>'
						+"</td></tr>"
					+"</table>"
				+'</td>'
			+'</tr>'
		+'</table>'
		+'</form>'
	$(block_html).dialog({modal:true,
		resizable:false,
		width: 550,
		height:380,
		buttons:[{id:'btnShowOK',text:gettext("Submit"),click:function(){$(this).submit();}},{text:gettext("Cancel"),click:function(){$(this).dialog("destroy"); }}],
		title:gettext("导入设备"),
		close:function(){$(this).dialog("destroy");}		
	});
	var opts = { 
		url:'/iclock/tasks/importclock/',
		dataType:'json',
		success: showResponse
	};
	var fields=["SN","Alias","DeptID","City","GCard"]
	for(var i=0;i<fields.length;i++){
		isChecked=$.cookie("iclock"+fields[i]+"_checked");
		value=$.cookie("iclock"+fields[i]+"_value");
		if(fields[i]!='SN' && fields[i]!='DeptID'){
			if(isChecked=="true")
				$("#id_"+fields[i]).attr("checked",true);
			else
				$("#id_"+fields[i]).attr("checked",false);
		}
		if(value)
			$("#id_"+fields[i]+"2file").val(value)
		else
			$("#id_"+fields[i]+"2file").val((i+1))
	}
	$("#frmComebackDb_iclock").submit(function(){
		var fields=["SN","Alias","DeptID","City","GCard"]
	
		$("#id_fields").val(fields);
		for(var i=0;i<fields.length;i++){
			isChecked=($("#id_"+fields[i]).prop("checked"))?true:false
			value=$("#id_"+fields[i]+"2file").val();
			value1=$("#id_whatrowid2file").val();
			if(isChecked && value==""){
				$("#id_"+fields[i]+"2file").after("<ul class='errorlist'><li>"+gettext('Please input selected field index in file' )+"</li></ul>");
				return false;
			}
			if(value1==""||value1.match(/^[1-9]\d*$/)==null){
			       $("#id_whatrowid2file").after("<ul class='errorlist'><li>Please input selected field index in file</li></ul>");
			       return false;
			}
			$.cookie("iclock"+fields[i]+"_checked",isChecked, { expires: 7 });
			$.cookie("iclock"+fields[i]+"_value",value, { expires: 7 });
		}
		$("#id_message").html("")
		var flag=checkForm();
		if(flag){
			$.blockUI({theme: true ,baseZ:10000,message: '<h1><img src="/iclock/media/img/loading.gif" /> <br>'+gettext("Please wait...")+'</br></h1>'});					
			$(this).ajaxSubmit(opts); 
		}
		return false;
	})
}

function importEmployee(){
var block_html=""
//		   +"<div>"
           +"<form id='frmComebackDb' name='frmComebackDb' method='POST' action='/iclock/tasks/import_emp/' enctype='multipart/form-data'>"
           +"<table><tr><td style='width:65%;'>"
           +"<table>"
				//+"<tr><td cols='3'>&nbsp;</td></tr>"
				+"<tr><th>"+gettext("Support Upload Fields" )+"</th><th width='20'>&nbsp;</th><th>"+gettext("Index in File" )+"</th></tr>"
//                +'<tr><td><input id="id_row" name="row"  type="checkbox" />'+ "Heading to the number of rows to skip"+'</td>'
//                +'<td><input name="row2file" id="id_row2file" type="text" style="width:100px !important;" value="0"/></td>'
//               +'</tr>'
				+"<tr><td><input id='id_badgenumber' name='badgenumber'  type='checkbox' checked disabled/>"+gettext("身份证号" )+"</td>"
				+"<td>&nbsp;</td>"
				+"<td><input name='badgenumber2file' id='id_badgenumber2file' type='text' style='width:100px !important;' value='1'/></td>"
				+"</tr>"
				+"<tr><td><input id='id_Workcode' name='Workcode'  type='checkbox' />"+gettext("考勤编号" )+"</td>"
				+"<td>&nbsp;</td>"
				+"<td><input name='Workcode2file' id='id_Workcode2file' type='text' style='width:100px !important;' value='2'/></td>"
				+"</tr>"
				+"<tr><td><input id='id_name' name='name' type='checkbox'/>"+gettext("name" )+"</td>"
				+'<td>&nbsp;</td>'
				+'<td><input name="name2file" id="id_name2file" type="text"  style="width:100px !important;" value="3"/></td>'
				+'</tr>'
				+'<tr><td><input id="id_defaultdeptid" name="defaultdeptid" type="checkbox"/>'+gettext("单位编号" )+'</td>'
				+'<td>&nbsp;</td>'
				+'<td><input name="defaultdeptid2file" id="id_defaultdeptid2file" type="text"  style="width:100px !important;" value="4"/></td>'
				+'</tr>'
				+'<tr><td><input id="id_Gender" name="Gender" type="checkbox" />'+gettext("Sex" )+'&nbsp;('+gettext("Man")+'=<input type="text" id="id_man" value="'+($.cookie("man_value")==null?''+gettext("Man")+'':$.cookie("man_value"))+'" name="man" style="width:30px !important;"/>&nbsp;'+gettext("Woman")+'=<input id="id_woman" name="woman" value="'+($.cookie("woman_value")==null?''+gettext("Woman")+'':$.cookie("woman_value"))+'" type="text" style="width:30px !important;"/>)</td>'
				+'<td>&nbsp;</td>'
				+'<td><input name="Gender2file" id="id_Gender2file" type="text"  style="width:100px !important;" value="6"/></td>'
				+'</tr>'
				+'<tr><td><input id="id_Card" name="Card" type="checkbox" />'+gettext("Id card" )+'</td>'
				+'<td>&nbsp;</td>'
				+'<td><input name="Card2file" id="id_Card2file" type="text" style="width:100px !important;" value="7"/></td>'
				+'</tr>'
				+'<tr><td><input id="id_Employeetype" name="Employeetype" type="checkbox" />'+gettext("人员类别" )+'（在编,聘用,合同内,合同外）</td>'
				+'<td>&nbsp;</td>'
				+'<td><input name="Employeetype2file" id="id_Employeetype2file" type="text"  style="width:100px !important;" value="9"/></td>'
				+'</tr>'
				+'<tr><td><input id="id_Birthday" name="Birthday" type="checkbox" />'+gettext("Birthday" )+'</td>'
				+'<td>&nbsp;</td>'
				+'<td><input name="Birthday2file" id="id_Birthday2file" type="text"  style="width:100px !important;" value="10"/></td>'
				+'</tr>'
				+'<tr><td><input id="id_minzu" name="minzu" type="checkbox" />'+gettext("nationality" )+'</td>'
				+'<td>&nbsp;</td>'
				+'<td><input name="minzu2file" id="id_minzu2file" type="text"  style="width:100px !important;" value="11"/></td>'
				+'</tr>'
				+'<tr><td><input id="id_title" name="title" type="checkbox"/>'+gettext("Title" )+'</td>'
				+'<td>&nbsp;</td>'
				+'<td><input name="title2file" id="id_title2file" type="text"  style="width:100px !important;" value="12"/></td>'
				+'</tr>'
				+'<tr><td><input id="id_ophone" name="ophone" type="checkbox" />'+gettext("Office phone" )+'</td>'
				+'<td>&nbsp;</td>'
				+'<td><input name="ophone2file" id="id_ophone2file" type="text"  style="width:100px !important;" value="13"/></td>'
				+'</tr>'
				//+'<tr><td><input id="id_FPHONE" name="FPHONE" type="checkbox" />'+gettext("Home phone" )+'</td>'
				//+'<td>&nbsp;</td>'
				//+'<td><input name="FPHONE2file" id="id_FPHONE2file" type="text" style="width:100px !important;"/></td>'
				//+'</tr>'
				+'<tr><td><input id="id_pager" name="pager" type="checkbox" />'+gettext("Mobile" )+'</td>'
				+'<td>&nbsp;</td>'
				+'<td><input name="pager2file" id="id_pager2file" type="text"  style="width:100px !important;" value="14"/></td>'
				+'</tr>'
                // +'<tr><td><input id="id_street" name="street" type="checkbox" />'+gettext("Address" )+'</td>'
                // +'<td>&nbsp;</td>'
                // +'<td><input name="street2file" id="id_street2file" type="text"  style="width:100px !important;"/></td>'
                // +'</tr>'
				+'<tr><td><input id="id_Hiredday" name="Hiredday" type="checkbox" />'+gettext("参加工作时间" )+'</td>'
                +'<td>&nbsp;</td>'
                +'<td><input name="Hiredday2file" id="id_Hiredday2file" type="text"  style="width:100px !important;" value="15"/></td>'
                +'</tr>'
				+'<tr><td><input id="id_email" name="email" type="checkbox" />'+gettext("e-mail address" )+'</td>'
				+'<td>&nbsp;</td>'
				+'<td><input name="email2file" id="id_email2file" type="text"  style="width:100px !important;" value="16"/></td>'
				+'</tr>'
				+'<tr><td><input id="id_OffDuty" name="OffDuty" type="checkbox" />'+gettext("OffDuty" )+'&nbsp;('+gettext("OffDuty_yes")+'=<input type="text" id="id_OffDuty_yes" value="'+($.cookie("OffDuty_yes_value")==null?''+gettext("Yes")+'':$.cookie("OffDuty_yes_value"))+'" name="OffDuty_yes" style="width:30px !important;"/>)</td>'
				+'<td>&nbsp;</td>'
				+'<td><input name="OffDuty2file" id="id_OffDuty2file" type="text"  style="width:100px !important;" value="17"/></td>'
				+'</tr>'
//				+'<tr><td><input id="id_Annualleave" name="Annualleave" type="checkbox" />'+gettext("Annual leave" )+'</td>'
//			    +'<td>&nbsp;</td>'
//			    +'<td><input name="Annualleave2file" id="id_Annualleave2file" type="text"  style="width:100px !important;"/></td>'
//			    +'</tr>'
                +'<tr><td cospan="3"><input  type="hidden" name="fields" id="id_fields"/></td></tr>'		
		+'</table></td>'
       +'<td style="vertical-align:top;">'
				+"<table>"
				+"<tr><th>"
                +gettext("选择将人员导入到的单位")
				+"</th></tr>"
                +"<tr>"
				+"<td cospan='2'>"
                +'<input type="text" style="width:150px !important;" readOnly="readOnly"  name="department"  id="departments"/>'
                +'<img  alt="open department tree" src="/media/img/sug_down_on.gif" id="id_drop_depts"/>'
				+"</td>"
                +"</tr>"
				+"<div id='show_dept_tree_'>"
				+"	<ul id='showTree_' class='ztree' style='margin-left:0px;overflow:auto;'></ul>	"
				+"</div> "
                +"<div style='display:none;'><input type='hidden' id='id_dept_val' name='dept' value='' /></div>"
				+"<tr><td cospan='2'>"
                +gettext("Upload file location")
				+"</td></tr>"
				+"<tr><td cospan='2'>"
                +"<input type='file' class='text' value='' name='fileUpload' id='fileUpload'/>"
				+"</td></tr>"
		+'<tr style="color:red;"><td><input id="id_whatrowid" name="whatrowid" type="checkbox" checked disabled/>'+gettext("whatrowid")
		+'<input name="whatrowid2file" id="id_whatrowid2file" type="text" value="1"  style="width:50px; color:red; !important;"/>'+gettext("行开始导入")+'</td>'
		+'</tr>'
		+'<tr><td><input id="id_nodept" name="nodept" type="checkbox"/>允许不选择单位导入(仅用于修改系统存在的人员信息)'
		+'</tr>'
		
		
		+"<tr>"
		+"<td cospan='2'>"
//                +"<input  name='button' class='ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only' id='id_import_submit' value='"+gettext('Submit')+"' type='submit' class='btnOKClass' />&nbsp;&nbsp;&nbsp;"
//                +"<input type='button' class='ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only' value='"+gettext('Return')+"' class='btnCancelClass' onclick='javascript:$(\"#importEmpId\").remove();$(\"#importEmpId\").dialog(\"destroy\");'>&nbsp;&nbsp;&nbsp;"
				+"</td>"
				+"</tr>"
				+"<tr><td cospan='2'>"
				+'<label>'+gettext("Support three formats files,one is text which is Tab Separated ,another is csv which is Comma Separated,the last one is xls which is Excel standard format")+'</label>'
                +'<label><br/>'+gettext("日期字段在excel中的单元格格式需设置为日期类型。")+'</label>'
				+"</td></tr>"
				+"<tr><td cospan='2'>"
                +'<div id="id_message"></div>'
				+"</td></tr>"
				+"</table>"
           +'</td></tr></table>'
    +'</form>'
//    +'</div>'
   // +'</div>'
   // +'</div>'

$(block_html).dialog({modal:true,
	              resizable:false,
				  width: 750,
				  height:540,
  				  buttons:[{id:'btnShowOK',text:gettext("Submit"),click:function(){$(this).submit();}},{text:gettext("Cancel"),click:function(){$(this).dialog("close"); }}],
				  
				  
				  title:gettext("Import employee setting"),
				  close:function(){$(this).dialog("destroy");}		
				});
//$("#btnCancel").click(function(){$("#frmComebackDb").remove();});
//$("#btnCancel").click(function(){$("#importEmpId").remove();});
$("#departments").val("");
//$("#id_dept_val").val(1);
$("#id_drop_depts").click(function(){
		createQueryDlgbypage('drop_depts')
		$('#dlg_for_query_drop_depts').dialog({position: { my: "right top", at: "right bottom",of:"#departments"},
		buttons:[{id:"btnShowOK",text:gettext('确定'),
		  click:function(){
			$("#id_dept_val").val(1);
			deptNames=getSelected_deptNames("showTree_drop_depts");
			$("#departments").val(formatArrayEx(deptNames));
			var deptids=getSelected_dept("showTree_drop_depts");
			$("#id_dept_val").val(deptids);
			$(this).dialog("destroy"); 
		}},
		 {id:"btnShowCancel",text:gettext('Return'),click:function(){$(this).dialog("destroy"); }
		}] })
		var zTree = $.fn.zTree.getZTreeObj("showTree_drop_depts");
		zTree.setting.check.enable = false;
		$("#dlg_dept_title_drop_depts").remove()
		
	 });
    var opts = {
		url:'/iclock/tasks/import_emp/',
		dataType:'json',
		success: showResponse
	};

var fields=["badgenumber",'Workcode',"name","defaultdeptid","Gender","Birthday","minzu","title","Card","ophone","pager","email","Hiredday","Employeetype","OffDuty"]
for(var i=0;i<fields.length;i++){
    isChecked=$.cookie("emp_"+fields[i]+"_checked");
    value=$.cookie("emp_"+fields[i]+"_value");
    if(fields[i]!='badgenumber'){
	
        if(isChecked=="1")
            $("#id_"+fields[i]).attr("checked",true);
        else
            $("#id_"+fields[i]).attr("checked",false);

    }
    // if(value)
        // $("#id_"+fields[i]+"2file").val(value)
    // else
        // $("#id_"+fields[i]+"2file").val((i+1))
}
$("#frmComebackDb").submit(function(){



	var fields=["badgenumber",'Workcode',"name","defaultdeptid","Gender","Birthday","minzu","title","Card","ophone","pager","email","Hiredday","Employeetype","OffDuty"]
	$("#id_fields").val(fields);
    for(var i=0;i<fields.length;i++){
         isChecked=($("#id_"+fields[i]).prop("checked"))?1:0
         value=$("#id_"+fields[i]+"2file").val();
		 value1=$("#id_whatrowid2file").val();
         if(isChecked && value==""){
            $("#id_"+fields[i]+"2file").after("<ul class='errorlist'><li>"+gettext('Please input selected field index in file' )+"</li></ul>");
            return false;
         }
		if(value1==""||value1.match(/^[1-9]\d*$/)==null){
			$("#id_whatrowid2file").after("<ul class='errorlist'><li>Please input selected field index in file</li></ul>");
			return false;

		}
         if(fields[i]=="Gender")
        {
          // $.cookie("man_value",$("#id_man").val(), { expires: 7 });
           //$.cookie("woman_value",$("#id_woman").val(), { expires: 7 });
        }
        //$.cookie("emp_"+fields[i]+"_checked",isChecked, { expires: 7 });
       // $.cookie("emp_"+fields[i]+"_value",value, { expires: 7 });
    }
	$("#id_message").html("")
	
	var flag=checkForm();

	if(flag){
		$.blockUI({theme: true ,baseZ:10000,message: '<h1><img src="/media/img/loading.gif" /> <br>'+gettext("Please wait...")+'</br></h1>'});
		$(this).ajaxSubmit(opts); 
	}
	return false;

})

}



function importSpeday(){
var block_html=""
           +"<form id='frmComebackDb' name='frmComebackDb' method='POST' action='/iclock/tasks/import_Speday/' enctype='multipart/form-data'>"
           +"<table><tr><td style='width:65%;'>"
           +"<table>"
				+"<tr><th>"+gettext("Support Upload Fields" )+"</th><th width='20'>&nbsp;</th><th>"+gettext("Index in File" )+"</th></tr>"
				+"<tr><td><input id='id_badgenumber' name='badgenumber'  type='checkbox' checked disabled/>"+gettext("PIN" )+"</td>"
				+"<td>&nbsp;</td>"
				+"<td><input name='badgenumber2file' id='id_badgenumber2file' type='text' style='width:100px !important;'/></td>"
				+"</tr>"
				+"<tr><td><input id='id_StartSpecDay' name='StartSpecDay' type='checkbox' checked disabled/>"+gettext("开始日期" )+"</td>"
				+"<td>&nbsp;</td>"
				+"<td><input name='StartSpecDay2file' id='id_StartSpecDay2file' type='text'  style='width:100px !important;'/>(2017-01-01)</td>"
				+"</tr>"
				+"<tr><td><input id='id_EndSpecDay' name='EndSpecDay' type='checkbox' checked disabled/>"+gettext("结束日期" )+"</td>"
				+"<td>&nbsp;</td>"
				+"<td><input name='EndSpecDay2file' id='id_EndSpecDay2file' type='text'  style='width:100px !important;'/>(2017-01-01)</td>"
				+"</tr>"
				
				
				+"<tr><td><input id='id_StartSpecDayTime' name='StartSpecDayTime' type='checkbox' checked disabled/>"+gettext("开始时间" )+"</td>"
				+"<td>&nbsp;</td>"
				+"<td><input name='StartSpecDayTime2file' id='id_StartSpecDayTime2file' type='text'  style='width:100px !important;'/>(09:00)</td>"
				+"</tr>"
				+"<tr><td><input id='id_EndSpecDayTime' name='EndSpecDaytime' type='checkbox' checked disabled/>"+gettext("结束时间" )+"</td>"
				+"<td>&nbsp;</td>"
				+"<td><input name='EndSpecDayTime2file' id='id_EndSpecDayTime2file' type='text'  style='width:100px !important;'/>(18:00)</td>"
				+"</tr>"
				
				+"<tr><td><input id='id_DateID' name='DateID' type='checkbox' checked disabled/>"+gettext("假类" )+"</td>"
				+"<td>&nbsp;</td>"
				+"<td><input name='DateID2file' id='id_DateID2file' type='text'  style='width:100px !important;'/>(病假)</td>"
				+"</tr>"
				+'<tr><td><input id="id_YUANYING" name="YUANYING" type="checkbox" />'+gettext("原因" )+'</td>'
				+'<td>&nbsp;</td>'
				+'<td><input name="YUANYING2file" id="id_YUANYING2file" type="text"  style="width:100px !important;"/></td>'
				+'</tr>'
                +'<tr><td cospan="3"><input  type="hidden" name="fields" id="id_fields"/></td></tr>'		
		+'</table></td>'
       +'<td style="vertical-align:top;">'
				+"<table>"
				+"<tr><td cospan='2'>"
                +gettext("Upload file location")
				+"</td></tr>"
				+"<tr><td cospan='2'>"
                +"<input type='file' class='text' value='' name='fileUpload' id='fileUpload'/>"
				+"</td></tr>"
		+'<tr><td><input id="id_whatrowid" name="whatrowid" type="checkbox" checked disabled/>'+gettext("whatrowid")
		+'<input name="whatrowid2file" id="id_whatrowid2file" type="text" value="2"  style="width:50px !important;"/></td>'
		+'</tr>'
		+"<tr>"
		+"<td cospan='2'>"
				+"</td>"
				+"</tr>"
				+"<tr><td cospan='2'>"
				+'<label>'+gettext("Support three formats files,one is text which is Tab Separated ,another is csv which is Comma Separated,the last one is xls which is Excel standard format")+'</label>'
                +"</td></tr>"
				+"<tr><td cospan='2'>"
                +'<div id="id_message"></div>'
				+"</td></tr>"
				+"</table>"
           +'</td></tr></table>'
    +'</form>'

$(block_html).dialog({modal:true,
	              resizable:false,
				  width: 750,
				  height:530,
  				  buttons:[{id:'btnShowOK',text:gettext("Submit"),click:function(){$(this).submit();}},{text:gettext("Cancel"),click:function(){$(this).dialog("close"); }}],
				  
				  
				  title:gettext("导入请假设置"),
				  close:function(){$("#frmComebackDb").remove();}		
				});
var opts = { 
		url:'/iclock/tasks/import_Speday/',
		dataType:'json',
		success: showResponse
	};

var fields=["badgenumber","StartSpecDay","EndSpecDay","StartSpecDayTime","EndSpecDayTime","DateID","YUANYING","clearance"]
for(var i=0;i<fields.length;i++){
    isChecked=$.cookie("Speday"+fields[i]+"_checked");
    value=$.cookie("Speday"+fields[i]+"_value");
    if(fields[i]!='badgenumber' && fields[i]!='StartSpecDay' && fields[i]!='EndSpecDay'&& fields[i]!='DateID'&& fields[i]!='StartSpecDayTime'&& fields[i]!='EndSpecDayTime'){
	
        if(isChecked=="true")
            $("#id_"+fields[i]).attr("checked",true);
        else
            $("#id_"+fields[i]).attr("checked",false);

    }
    if(value)
        $("#id_"+fields[i]+"2file").val(value)
    else
        $("#id_"+fields[i]+"2file").val((i+1))
}
$("#frmComebackDb").submit(function(){
	var fields=["badgenumber","StartSpecDay","EndSpecDay","StartSpecDayTime","EndSpecDayTime","DateID","YUANYING","clearance"]
	$("#id_fields").val(fields);
    for(var i=0;i<fields.length;i++){
         isChecked=($("#id_"+fields[i]).attr("checked"))?true:false
         value=$("#id_"+fields[i]+"2file").val();
		 value1=$("#id_whatrowid2file").val();
         if(isChecked && value==""){
            $("#id_"+fields[i]+"2file").after("<ul class='errorlist'><li>"+gettext('Please input selected field index in file' )+"</li></ul>");
            return false;
         }
		if(value1==""||value1.match(/^[1-9]\d*$/)==null){
			$("#id_whatrowid2file").after("<ul class='errorlist'><li>Please input selected field index in file</li></ul>");
			return false;

		}
         if(fields[i]=="clearance")
        {
            $.cookie("clearance_yes_value",$("#id_clearance_yes").val(), { expires: 7 });
            $.cookie("clearance_no_value",$("#id_clearance_no").val(), { expires: 7 });  
        }
         $.cookie("Speday"+fields[i]+"_checked",isChecked, { expires: 7 });
         $.cookie("Speday"+fields[i]+"_value",value, { expires: 7 });
    }
	$("#id_message").html("")
	
	var flag=checkForm();

	if(flag){
		$.blockUI({theme: true ,baseZ:10000,message: '<h1><img src="/media/img/loading.gif" /> <br>'+gettext("Please wait...")+'</br></h1>'});					
		$(this).ajaxSubmit(opts);
	}
	return false;

})

}





//自动发送人员信息到设备
function autoSendEmpToDev(){
  $.blockUI({theme: true ,baseZ:10000,message: '<h1><img src="/media/img/loading.gif" /> <br>'+gettext("Please wait...")+'</br></h1>'});					
  $.ajax({type: "POST",
		   url:'/iclock/data/autosendemptodev',
				  dataType:"json",
		success: function (retdata){
					$.unblockUI();
					alert(retdata.message);
			},
		error:function(){
					$.unblockUI();
					alert("Server Error")
				}
	});	
	
}


//上传设置到门禁设备
function setToDevs(model){
	$.ajax({ 
	        type: "POST",
	        url:'/acc/getData/?func=devs',
	        dataType:"json",
	        success:function(devs){
			var block_html="<div id='dev_dialog' style='width:500px;'>"
									+ 		"<div class='dheader'><span>选择上传设备</span><span class='close' onclick='javascript:$.unblockUI();'></span></div>"
									+ 		"<div class='dcontent' style='height:200px;overflow:auto;'>"
									+           "<table width=100%>"
									+'<tr id="id_toolbar_emp"><td id="divPage_emp" colspan="3">'
									+'<form id="id_changelist-search" action="" method="get">'
									+'<div id="line"><!-- DIV needed for valid HTML -->'
									+'<label for="id_searchbar_emp"></label>'
									+'<input type="text" title="根据设备序列号、设备别名进行查询" size="10" style="width:150px !important;" name="q_emp" value="" id="id_searchbar_emp"/>'
									+"<span id='id_search' ><a class='m-btn  blue rnd mini'>"+gettext('Query')+"</a></span>"
											+'</div>'
									+'</form>'
									+'</td></tr><tr><td><table id="id_ret">'
									+				getDevHtml(devs)
									+            "</table></td></tr></table>"
									+       "</div>"
										//+createSubmitButton_acc()
									+       "</div>"
					$(block_html).dialog({modal:true,
						      resizable:false,
							  buttons:[{id:"btnShowOK",text:gettext("Submit"),click:function(){}},
								 {id:"btnShowCancel",text:gettext("Cancel"),click:function(){$(this).dialog("destroy");}
								}],
									  width: 350,
										  height:350,
										  title:gettext("设备"),
										  close:function(){$(this).dialog("destroy");}	
										});
					
					$("#btnShowOK").click(function(){
						var sns=getSelected_emp()
                        
                        urlAddr="/iclock/iacc/setToDevice/";
                        queryStr="&SNS="+sns+"&model="+model
                        $.ajax({
                            type:"POST",
                            url:urlAddr,
                            data:queryStr,
                            dataType:"json",
                            async:false,
                            success:function(msg){
                                $("#id_error").html(msg.message).css("color","red");
                            }
                        });
                        $("#dev_dialog").remove();
                        })
					$("#id_search").click(function(){
						var v=$("#id_searchbar_emp")[0].value;
						$.cookie("q",v,{expires:10})
						$.ajax({
								type:"POST",
								dataType:"json",
								url: "/acc/getData/?func=devs&q="+escape(v),
								success:function(data){
										$("#id_ret").html(getDevHtml(data))
								}
							})		
						return false;
					});
			}
		})
	
}
function getDevHtml(devs){
	var retHtml="<tr><th><input type='checkbox' id='is_select_all_emp' onclick='check_all_for_row_emp(this.checked);' /></th><th>设备序列号</th><th>设备名称</th></tr>"

	for(var i=0;i<devs.length;i++){
		retHtml+="<tr><td><input type='checkbox' class='class_select_emp' onclick='showSelected_emp();'  name='"+devs[i].SN+"' id='"+devs[i].SN+"' alt='' /></td><td>"+devs[i].SN+"</td><td>"+devs[i].Alias+"</td></tr>"
	}
	return retHtml;
}

function createSubmitButton_acc()
{
	str = "<div style='text-align:right; margin-top: 10px; margin-right: 20px;margin-bottom:10px;'>"
	str += '<input type="button" value="'+gettext('Submit')+'" id="btnShowOK"  class="btnOKClass">&nbsp;&nbsp;&nbsp;'
	str += '<input type="button" value="'+gettext('Cancel')+'" id="btnShowCancel_acc"  class="btnCancelClass">&nbsp;&nbsp;&nbsp;'
	str += "</div>"
	return str
}


function createSelect_html(arrays){
	var html=""
	for(var i=0;i<arrays.length;i++)
		html+="<option value='"+arrays[i]+"' selected>"+arrays[i]+"</option>"
	return html;
	
}
function getextraBatchOpHTML(BatchOp)
{
	var retHtml=""
	if(typeof extraBatchOp!="object"||extraBatchOp==[]) return retHtml;
	for(var m in extraBatchOp)
	{
		retHtml+="<li><span>"+extraBatchOp[m].caption+"</span><ul>"
		var submenu=extraBatchOp[m].submenu
		for(var i in submenu)
		{
			if(submenu[i].action)
				retHtml+="<li onclick='javascript:batchOp("+submenu[i].action+","+submenu[i].itemCanBeOperated+","+'"'+submenu[i].title+'"'+");'><a href='#'>"+submenu[i].title+"</a></li>";
			else
				retHtml+="<li><div class='no_permissions'>"+submenu[i].title+"</div></li>";
							
				
		}
		retHtml+="</ul></li>"
	}
	return retHtml;	
}
function renderGridData(PageName,Options)
{
	var IsGridExist=$("#id_grid_"+PageName).jqGrid('getGridParam','records')
	if(typeof(IsGridExist)=='undefined')
	{
		$("#id_grid_"+PageName).jqGrid(Options).navGrid("#id_pager_"+PageName,{edit:false,add:false,del:false,search:false,refresh:true});
		$("#id_grid_"+PageName).jqGrid('setFrozenColumns');

	}
	else
	{
		$("#id_grid_"+PageName).jqGrid('setGridParam',{url:Options.url,datatype:"json"}).trigger("reloadGrid").navGrid("#id_pager_"+PageName,{edit:false,add:false,del:false,search:false,refresh:true});
	}
}


function renderLeftInformation(info,isShowDate)
{
	
	//outerLayout.show('west')
	//$("#west_content").html("<div  id='menu_div' ></div><div class='ui-widget' style='margin:20px 4px;'><div id='left_datepicker'></div><div class='info'></div></div>")
	//if(isShowDate==undefined||isShowDate==true)
	//	$("#left_datepicker").datepicker()
	
	if(info) $('#west_content_'+g_activeTabID).html(info)
 
}

function loadPageData(query, value)
{
	var postData={}//{'addition_fields': options.addition_fields,'exception_fields': options.exception_fields};
	var url=pageQueryString;
	if(query!=undefined)
		reloadData();
	else
	{
		var postUrl=g_urls[g_activeTabID]+url;
		if(tblName=='USER_SPEDAY'||tblName=='USER_OVERTIME'){
			if('{{roles}}'!='-1'){
				if(postUrl.indexOf("?")==-1){
					postUrl=postUrl+"?filtertag=1";
				}else{
					postUrl=postUrl+"&filtertag=1";
				}
			}
		}
		if(postUrl.indexOf("?")==-1){
			postUrl=postUrl+"?mod_name="+mod_name;//+"?stamp="+new Date().toUTCString();
		}else{
			postUrl=postUrl+"&mod_name="+mod_name;//+"&stamp="+new Date().toUTCString();
		}
		var hcontent=$("#"+g_activeTabID+" #id_content").height();
		var hbar=$("#"+g_activeTabID+" #id_top").height();
		var height=hcontent-hbar-70;
		if (groupHeaders.length>0)
		 height=height-30;
		
		if(typeof(Custom_Jqgrid_Height)!='undefined'&&Custom_Jqgrid_Height!=""){
			jqOptions[g_activeTabID].height=Custom_Jqgrid_Height;
		}else{jqOptions[g_activeTabID].height=height;}
		//jqOptions.rowList=[jqOptions.rowNum,jqOptions.rowNum*2]
		jqOptions[g_activeTabID].url=postUrl;

		
		$("#id_grid_"+tblName[g_activeTabID]).jqGrid(jqOptions[g_activeTabID]);
		
		//$("#id_grid").jqGrid('setFrozenColumns');
		if (groupHeaders.length>0)
		$("#id_grid_"+tblName[g_activeTabID]).jqGrid('setGroupHeaders', {useColSpanStyle: true,groupHeaders:groupHeaders})
		//else
	        $("#id_grid_"+tblName[g_activeTabID]).jqGrid('setFrozenColumns');

	}
}

function editclick(key,editUrl,other)
{
	if(editUrl== undefined)
	{
		var Href=g_urls[g_activeTabID].split("?")[0]+key+'/'+"?stamp="+moment().unix();
		var posturl=g_urls[g_activeTabID].split("?")[0]+key+'/?mod_name='+mod_name
	}
	else
	{
		var Href=editUrl+key+'/'+"?stamp="+moment().unix();
		var posturl=editUrl+key+'/?mod_name='+mod_name
	}
	$.ajax({
		type:"GET",
		url:Href+'&mod_name='+mod_name,
		dataType:"html",
		async:false,
		success:function(msg){
                        msg=$.trim(msg)
			processEdit(msg, posturl,key,tblName[g_activeTabID],other);
		}
	});
}
//预先处理对话框中的一些通用功能, 对自定义功能可在相应_list.html页面中写process_dialog()函数实现
function init_dialog(obj)  
{

    if (dtFields != '')
    {//日期时间 字段，加日历和时间
        arr = dtFields.split(',')
        for (var row in arr)
        {
            var o = $('#id_' + arr[row] + '',obj); 
			if(o.length>0)
			{
              //限制日期时间长度为19，处理服务器日期时间默认值的毫秒问题
              if (o.val().length > 19)  o.val(o.val().substring(0,19));
			}
        }
    }
}

function SaveFormData(FormObj,url,flag,tableName)
{
	f=$(FormObj).find("#id_edit_form").get(0)
	if (!$(f).valid()){$("#id_error").html(gettext("occur error!")).css("color","red").css('display','block'); return 0;}
	//var formStr=formToRequestString(f);
	$(FormObj).find("#id_edit_form").ajaxSubmit({
            type: "POST",
            url: url,
            dataType: "json",
            success: function (ret) {
                if (ret.ret == 0) {
                    if (flag == 'addandcontinue') {
                        if ($.isFunction(window['afterPost_' + tableName])) {
                            window['afterPost_' + tableName](flag, FormObj);
                        }
                    }
                    else {
                        if ($.isFunction(window['afterPost_' + tableName])) {
                            window['afterPost_' + tableName](flag, FormObj);
                        }
                        $(FormObj).dialog("destroy");
                        reloadData();
                    }

                }
			//$("#id_error").html(ret.message).css("color","red").css('display','block');
			$("#id_error",FormObj).html('<ul class="errorlist"><li>'+ret.message+'</li></ul>').show();



            }
        }
	)

	// $.post(url,
	// 	formStr,
	// 	function (ret, textStatus) {
	// 		if(ret.ret==0)
	// 		{
	// 			if(flag=='addandcontinue')
	// 			{
	// 				if($.isFunction(window['afterPost_'+tableName]))
	// 				{
	// 					window['afterPost_'+tableName](flag,FormObj);
	// 				}
	// 			}
	// 			else
	// 			{
	// 				if($.isFunction(window['afterPost_'+tableName]))
	// 				{
	// 					window['afterPost_'+tableName](flag,FormObj);
	// 				}
	// 				$(FormObj).dialog("destroy");
	// 				reloadData();
	// 			}
	// 		}
	// 		//$("#id_error").html(ret.message).css("color","red").css('display','block');
	// 		$("#id_error",FormObj).html('<ul class="errorlist"><li>'+ret.message+'</li></ul>').show();
	// 	},
	// 	"json");
}



function initGridHtml(tbl) {
	var html="<table id='id_grid_"+tbl+"' >	</table>"
	html=html+"<div id='id_pager_"+tbl+"'></div>"
	$('#'+g_activeTabID+' .module').html(html)
	
}

function reloadData(grid_page,url)
{	
	if(grid_page==undefined){
		grid_page=tblName[g_activeTabID]
	}
	//initwindow_tabs(g_activeTabID);
	if(url!=undefined&&url!=''){
		$("#id_grid_"+grid_page).jqGrid('setGridParam',{url:url,datatype:"json"}).trigger('reloadGrid');
	} else{
		$("#id_grid_"+grid_page).trigger('reloadGrid');
	}
	
}


function addZKOnline() {
/*
    if (!$("#id_zkonline").html())
	{
		$("#id_north").before("<div style='display:none;' id='id_zkonline'>"
					+"<OBJECT classid='clsid:A318A9AC-E75F-424C-9364-6B40A848FC6B'  style='width:20px;height:20px;' id=zkonline >"
					+"</OBJECT>"
					+"<COMMENT>"
					+"<EMBED type='application/x-eskerplus' classid='clsid:A318A9AC-E75F-424C-9364-6B40A848FC6B' codebase='ZKOnline.ocx' width=20 height=20></EMBED>"
					+"</COMMENT>"
				    +"</div>"
		);
	}
*/	
	
}

function getProcessLog(id){
	window.open("/iclock/att/showApprovals/?id="+id); 
}

function getFileDetail(url){
	window.open(url); 
}


/*******************************自定义字段验证******************************************/

function isIdCardNo(num) {

var factorArr = new Array(7,9,10,5,8,4,2,1,6,3,7,9,10,5,8,4,2,1);
var parityBit=new Array("1","0","X","9","8","7","6","5","4","3","2");
var varArray = new Array();
var intValue;
var lngProduct = 0;
var intCheckDigit;
var intStrLen = num.length;
var idNumber = num;
// initialize
if ((intStrLen != 15) && (intStrLen != 18)) {
return false;
}
// check and set value
for(i=0;i<intStrLen;i++) {
varArray[i] = idNumber.charAt(i);
if ((varArray[i] < '0' || varArray[i] > '9') && (i != 17)) {
return false;
} else if (i < 17) {
varArray[i] = varArray[i] * factorArr[i];
}
}

if (intStrLen == 18) {
//check date
var date8 = idNumber.substring(6,14);
if (isDate8(date8) == false) {
return false;
}
// calculate the sum of the products
for(i=0;i<17;i++) {
lngProduct = lngProduct + varArray[i];
}
// calculate the check digit
intCheckDigit = parityBit[lngProduct % 11];
// check last digit
if (varArray[17] != intCheckDigit) {
return false;
}
}
else{ //length is 15
//check date
var date6 = idNumber.substring(6,12);
if (isDate6(date6) == false) {

return false;
}
}
return true;

}

jQuery.validator.addMethod("isIdCardNo", function(value, element) {
return this.optional(element) || isIdCardNo(value);
}, "请正确输入身份证号码");





jQuery.validator.addMethod("isMobile", function(value, element) {
var length = value.length;
var mobile = /^(((13[0-9]{1})|(15[0-9]{1}))+\d{8})$/;
return this.optional(element) || (length == 11 && mobile.test(value));
}, "请正确填写手机号码");

jQuery.validator.addMethod("alnum", function(value, element) {
return this.optional(element) || /^[a-zA-Z0-9]+$/.test(value);
}, "只能包括英文字母和数字");

jQuery.validator.addMethod("string", function(value, element) {
return this.optional(element) || /^[\u4e00-\u9fa5a-zA-Z0-9_.（）()@-]+$/.test(value);
}, "不允许包含特殊符号!");

jQuery.validator.addMethod("ip", function(value, element) { 
var ip = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/; 
return this.optional(element) || (ip.test(value) && (RegExp.$1 < 256 && RegExp.$2 < 256 && RegExp.$3 < 256 && RegExp.$4 < 256)); 
}, "Ip地址格式错误");



/*******************************自定义字段验证结束******************************************/


