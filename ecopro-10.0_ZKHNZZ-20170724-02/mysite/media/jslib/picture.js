function show_during_times(t1,t2)
{	
	
	if(t1==t2)
		return "";
	else
		return getDuring_time_Str(t1)+"-"+getDuring_time_Str(t2);
}
function getDuring_time_Str(t)
{
	var sec=1/24/60/60;
	t_hour=parseInt((t+sec)*24*60/60)
	t_minute=Math.round((t+sec)*24*60%60)
	return getTimeStr(t_hour)+":"+getTimeStr(t_minute);
	
}
function getTimeStr(t)
{	if(t<10)
		return "0"+t;
	else
		return t;
}
function normalP(v)
{	
	return v*810/10000;  
}
function getTZDateAlt(index,sdate)
{
	if(sdate==undefined)
        return "";
    var tmp=new Date(sdate.valueOf()+index*1000*3600*24);
	var m="00"+(tmp.getMonth()+1);
	var d="00"+tmp.getDate();
	return	tmp.getFullYear()+"-"+m.substring(m.length-2)+"-"+d.substring(d.length-2);
}
function createTZTable(tzData, dayLabelFun, dayCount,sDate)
{
  var tz, i, dayi=0, curDay=-1, timei=0, temp=[];
  html='<table class="timezone-table"><tr><td width="120px">&nbsp;</td><td class="timezone-header">&nbsp;</td></tr>';
  for(i=0;i<tzData.length || temp.length>0;)
  {
    if(temp.length==0)
		tz=tzData[i]
	else
	{
		tz=temp[0];
		temp=[];
	}
	dayi=Math.floor(tz.StartTime)
    while(curDay<dayi) //new a day row
	{
		curDay+=1;
		if(curDay<dayi) html+='</td></tr>';
		html+='<tr>'
		if(sDate==undefined) 
			html+='<td class=txalign>'+dayLabelFun(curDay)+'</td><td class="timezones-container">'
		else
			html+='<td class=txalign>'+dayLabelFun(curDay,sDate)+'</td><td class="timezones-container" >'
		timei=0;
	}
	var dayi2=Math.floor(tz.EndTime)
	var time1=Math.round((tz.StartTime-Math.floor(tz.StartTime))*10000);
	var time2=Math.round((tz.EndTime-Math.floor(tz.EndTime))*10000);
	if(dayi2>dayi) 
	{
		var obj={}
		for (f in tz) { obj[f]=tz[f] }
		obj.StartTime=dayi+1;
		temp=[obj];
		time2=10000;
	}
	var hex="000000"+parseInt(tz['Color'],10).toString(16)	
	hex=hex.substring(hex.length-6,hex.length)	
	if(time1>timei) html+='<div style="width: '+normalP(time1-timei)+'px;" class="tzbar space"></div>'
	html+='<div title="'+tz['SchName']+'" alt0="'+tz['StartTime']+'" alt1="'+tz['EndTime']+'" alt2="'+tz['alt2']+'" alt4="'+tz['SchClassID']+'" style="text-align: center; width: '+normalP(time2-time1)+'px;'+
		(tz['Color']==undefined?' ':' background-color: #'+hex+' ')+
		'" class="tzbar"><span alt3="'+tz['SchName']+'" style="color:white;font-size:10px;vertical-align:top;">'+show_during_times(tz.StartTime-Math.floor(tz.StartTime),tz.EndTime-Math.floor(tz.EndTime))+'</span></div>'
	timei=time2;
	if(temp.length==0)
		i+=1;
  }
  html+='</td></tr>'
  curDay+=1;
  if(dayCount!=undefined)
  while(curDay<dayCount)
  {
	if(sDate==undefined)
		html+='<tr><td class=txalign>'+dayLabelFun(curDay)+'</td><td class="timezones-container"></td></tr>'
    else
		html+='<tr><td class=txalign>'+dayLabelFun(curDay,sDate)+'</td><td class="timezones-container"></td></tr>'
    curDay+=1;
  }
  html+='<tr style="background: #ccc"><td colspan="2" style="height:2px;"></td></tr></table>'
  return html
}


function show_shift_Detail(rowData,delflag,ii)
{  
	if (ii==1) {
		var Shift_id=rowData[0];
		$("#id_Shift_Detail_dlg fieldset legend").html(rowData[1]+"&nbsp;&nbsp;"+gettext('Shift detail'));
		queryStr="Shift_id="+Shift_id+"&unit="+rowData[6]+"&weekStartDay="+weekStartDay;
		$.ajax({
			type:"POST",
			url: "/iclock/att/shift_detail/",
			data:queryStr,
			dataType:"json",
			success:function(json){
				var unit=rowData[6];
				if(unit==1)   //按周显示班次明细
				{
					var days=rowData[4]*7; 
					$("#tz_dlg").html(createTZTable(json,getTZWeekLabel,days));
				}
				else if(unit==0)  //按天显示班次明细
				{ 
					var days=rowData[4]*1+1; 
					$("#tz_dlg").html(createTZTable(json,getTZDayLabel,days));
				}
				else if(unit==2)          //按月显示班次明细
				{ 
					var days=rowData[4]*31; 
					$("#tz_dlg").html(createTZTable(json,getTZDayLabel,days));
				}
			   $("#tz_dlg .tzbar").tooltip()	
				
				if(typeof(delflag)=='undefined'){
					delflag=1
				}
				
				if (options.canDelete==true&&options.canEdit&&delflag==1)
				{
					$("#id_numrun_tip").mouseover(function(e){
						$(this).css({"z-index":1024,"visibility":"visible","position":"absolute","top":e.clientY,"left":e.clientX+50})
					}).mouseout(function(){
						$("#id_numrun_tip").css("visibility","hidden");
					});
	
					$(".tzbar").dblclick(function(){
						var start=$(this).attr("alt0");
						var end=$(this).attr("alt1");
						var NumID=$(this).attr("alt4");
						if(start!=undefined&&end!=undefined){
							ret=window.confirm(gettext("Are you sure delete the time-table?"));
							if(ret)
							{
	//							var queryStr="shift_id="+Shift_id+"&numid="+NumID+"&start="+start+"&end="+end+"&unit="+rowData[6]+"&weekStartDay="+weekStartDay;
								var queryStr="num_id="+NumID;
								$.ajax({ type: "POST",
										url: "/iclock/att/deleteShiftTime/",
										data:queryStr,
										dataType:"json",
										success: function(retdata){
											if(retdata.ret==0){
												if(typeof data!='undefined')
													selected_data=data;
												else selected_data=selected_data;
												actionSucess_NoReload(retdata,selected_data)
											}
											else
											{
		//										var i=retdata.indexOf("errorInfo=\"");
												alert(retdata.message);
											}
										
										
										
										},
										error: function(request, errorMsg){
										   alert($.validator.format(gettext('Operating failed for {0} : {1}'), options.title, errorMsg)); 
										   }
								   });
					
								
							}
						}
					});
	
				}           
			}
		 });
	}else{
		var Shift_id=rowData[0];
		$("#id_Shift_Detail_dlg fieldset legend").html(rowData[1]+"&nbsp;&nbsp;"+gettext('Shift detail'));
		queryStr="Shift_id="+Shift_id+"&unit="+rowData[6]+"&weekStartDay="+weekStartDay;
		$.ajax({
			type:"POST",
			url: "/iclock/att/shift_detail/",
			data:queryStr,
			dataType:"json",
			success:function(json){
				var unit=rowData[6];
				if(unit==1)   //按周显示班次明细
				{
					var days=rowData[4]*7; 
					$("#tz_dlg_NUM_RUN").html(createTZTable(json,getTZWeekLabel,days));
				}
				else if(unit==0)  //按天显示班次明细
				{ 
					var days=rowData[4]*1+1; 
					$("#tz_dlg_NUM_RUN").html(createTZTable(json,getTZDayLabel,days));
				}
				else if(unit==2)          //按月显示班次明细
				{ 
					var days=rowData[4]*31; 
					$("#tz_dlg_NUM_RUN").html(createTZTable(json,getTZDayLabel,days));
				}
			   $("#tz_dlg_NUM_RUN .tzbar").tooltip()	
				
				if(typeof(delflag)=='undefined'){
					delflag=1
				}
				
				if (options.canDelete==true&&options.canEdit&&delflag==1)
				{
					$("#id_numrun_tip").mouseover(function(e){
						$(this).css({"z-index":1024,"visibility":"visible","position":"absolute","top":e.clientY,"left":e.clientX+50})
					}).mouseout(function(){
						$("#id_numrun_tip").css("visibility","hidden");
					});
	
					$(".tzbar").dblclick(function(){
						var start=$(this).attr("alt0");
						var end=$(this).attr("alt1");
						var NumID=$(this).attr("alt4");
						if(start!=undefined&&end!=undefined){
							ret=window.confirm(gettext("Are you sure delete the time-table?"));
							if(ret)
							{
	//							var queryStr="shift_id="+Shift_id+"&numid="+NumID+"&start="+start+"&end="+end+"&unit="+rowData[6]+"&weekStartDay="+weekStartDay;
								var queryStr="num_id="+NumID;
								$.ajax({ type: "POST",
										url: "/iclock/att/deleteShiftTime/",
										data:queryStr,
										dataType:"json",
										success: function(retdata){
											if(retdata.ret==0){
												if(typeof data!='undefined')
													selected_data=data;
												else selected_data=selected_data;
												actionSucess_NoReload(retdata,selected_data)
											}
											else
											{
		//										var i=retdata.indexOf("errorInfo=\"");
												alert(retdata.message);
											}
										
										
										
										},
										error: function(request, errorMsg){
										   alert($.validator.format(gettext('Operating failed for {0} : {1}'), options.title, errorMsg)); 
										   }
								   });
					
								
							}
						}
					});
	
				}           
			}
		 });
	}
}




function show_lineshift_Detail(rowData,delflag)
{  

    var Shift_id=rowData[0];
    $("#id_Shift_Detail_dlg fieldset legend").html(rowData[1]+"&nbsp;&nbsp;"+gettext('Shift detail'));
    queryStr="Shift_id="+Shift_id+"&unit="+rowData[6]+"&weekStartDay="+weekStartDay;
    $.ajax({
        type:"POST",
        url: "/patrol/shift_detail/",
        data:queryStr,
        dataType:"json",
        success:function(json){
            var unit=rowData[6];
            if(unit==1)   //按周显示班次明细
            {
                var days=rowData[4]*7; 
                $("#tz_dlg").html(createTZTable(json,getTZWeekLabel,days));
            }
            else if(unit==0)  //按天显示班次明细
            { 
                var days=rowData[4]*1+1; 
                $("#tz_dlg").html(createTZTable(json,getTZDayLabel,days));
            }
            else if(unit==2)          //按月显示班次明细
            { 
                var days=rowData[4]*31; 
                $("#tz_dlg").html(createTZTable(json,getTZDayLabel,days));
            }
           $("#tz_dlg .tzbar").tooltip()	
			
			if(typeof(delflag)=='undefined'){
				delflag=1
			}
			
			if (options.canDelete==true&&options.canEdit&&delflag==1)
			{
				$("#id_numrun_tip").mouseover(function(e){
					$(this).css({"z-index":1024,"visibility":"visible","position":"absolute","top":e.clientY,"left":e.clientX+50})
				}).mouseout(function(){
					$("#id_numrun_tip").css("visibility","hidden");
				});

				$(".tzbar").dblclick(function(){
					var start=$(this).attr("alt0");
					var end=$(this).attr("alt1");
					var NumID=$(this).attr("alt4");
					if(start!=undefined&&end!=undefined){
						ret=window.confirm(gettext("Are you sure delete the time-table?"));
						if(ret)
						{
//							var queryStr="shift_id="+Shift_id+"&numid="+NumID+"&start="+start+"&end="+end+"&unit="+rowData[6]+"&weekStartDay="+weekStartDay;
							var queryStr="num_id="+NumID;
							$.ajax({ type: "POST",
									url: "/patrol/deleteShiftTime/",
									data:queryStr,
									dataType:"json",
									success: function(retdata){
										if(retdata.ret==0){
											if(typeof data!='undefined')
												selected_data=data;
											else selected_data=selected_data;
											actionSucess_NoReload(retdata,selected_data)
										}
										else
										{
	//										var i=retdata.indexOf("errorInfo=\"");
											alert(retdata.message);
										}
									
									
									
									},
									error: function(request, errorMsg){
									   alert($.validator.format(gettext('Operating failed for {0} : {1}'), options.title, errorMsg)); 
									   }
							   });
				
							
						}
					}
				});

			}           
        }
     });
}


function ShowCalenderData(year,page,op,key,jqOptions_record)
{
	$('#id_card_west #id_opt_tree').html('&nbsp;&nbsp;'+year)

	
	var setting = {
            check: {enable: false,chkStyle: "checkbox",chkboxType: { "Y": "", "N": "" }},          
	    async: {
			    enable: true,
			    url: "/iclock/att/getData/?func=picture_canlendar&year="+year,
			    autoParam: ["id"]
		    }
	};
	$.fn.zTree.init($("#showTree_"+page), setting,null);	
	var zTree = $.fn.zTree.getZTreeObj("showTree_"+page);
	zTree.setting.callback.onClick = function onClick(e, treeId, treeNode){
			jqOptions_record.datatype='json'
			jqOptions_record.url="/iclock/pics/"+op+'/?ttime='+treeNode.value+'&key='+key
			renderGridData('picture',jqOptions_record)
			
	}

}




function createPictureDialog(op,title,key)
{
	var block_html="<div class='module' style='position:relative; width: 100%;margin-top: 0px;'>"
	+"<div id='id_card_west' style='border:1px solid #e9e9e9;width: 180px;' class='left ui-layout-west' >"
				+"<div class='ui-widget-header' style='height: 25px;'>"
					+"<span><a class='_year_select_'><</a></span>"
					+"<span id=id_opt_tree>"
						+"<input type='hidden' value='2014' readonly='readonly' id='id_cascadecheck_'/>&nbsp;&nbsp;2014"
					+"</span>"
					+"<span style='float:right;'><a  class='_year_select_'>></a></span>"
				+"</div>"
				+"<div id='show_date_tree_'>"
				+"<ul id='showTree_picture' class='ztree' style='margin-left: 0px;overflow:auto;height:410px;'></ul>"	
				+"</div> "  
			+"</div>"
		+"<div id='id_picture_middle' style='height: 450px; width: 6px; top: 0px;' class='left ui-layout-resizer ui-layout-resizer-west ui-layout-resizer-open ui-layout-resizer-west-open'>"
			
		+"</div>"		
		
		+"<div id='id_picture_info' class='left' style='width: 780px;margin-right: 10px;'>"
		
			+"<table id='id_grid_picture'>	</table>"
			+"<div id='id_pager_picture'></div>"

		+"</div>"
	+"</div>"
	$(block_html).dialog({	modal:true,resizable:false,
						  width: 1040,
						  height:550,
						  //position:{ my: "top right", at: "right top", of: window },
						  title:title,
						  close:function(){$(this).dialog("destroy")}
						})
	var y=moment().year()
	
	var jqOptions_record=copyObj(jq_Options);
	jqOptions_record.colModel=[
		{'name':'id','hidden':true},
		{'name':'p0','sortable':false,'width':122,'title':false,'resizable':false,'align':'center','label':''},
		{'name':'p1','sortable':false,'width':122,'resizable':false,'title':false,'label':''},
		{'name':'p2','sortable':false,'width':122,'resizable':false,'title':false,'label':''},
		{'name':'p3','sortable':false,'width':122,'resizable':false,'title':false,'label':''},
		{'name':'p4','sortable':false,'width':122,'resizable':false,'title':false,'label':''},
		{'name':'p5','sortable':false,'width':122,'resizable':false,'title':false,'label':''}
	]

		jqOptions_record.datatype='local'
		jqOptions_record.height=420
		jqOptions_record.multiselect=false
		jqOptions_record.width='auto'
		jqOptions_record.pager='id_pager_picture'
		jqOptions_record.altRows=true
		jqOptions_record.altclass='altclass'
		jqOptions_record.hoverrows=false
		//jqOptions_record.caption=moment().format('YYYY-MM-DD')+' 照片...'
		$("#id_grid_picture").jqGrid(jqOptions_record);
	
	
	
	
	$('._year_select_').click(function(){
		txt=$(this).text()
		if (txt=='<')
		{
			var year =parseInt($('#id_card_west #id_opt_tree').text())
			ShowCalenderData(year-1,'picture',op,key,jqOptions_record)
			
		}
		else if (txt=='>')
		{
			var year =parseInt($('#id_card_west #id_opt_tree').text())
			ShowCalenderData(year+1,'picture',op,key,jqOptions_record)
			
			
			
		}
	})
	
	ShowCalenderData(y,'picture',op,key,jqOptions_record)
						
						
						
						
						
						
						
	return	true
	
	
	
	
	
	
}
