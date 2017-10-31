department=[];
show=0
check=0
function getDept_to_show_emp(lheight,lwidth,emp_w,pageName){
	$("#show_dept_emp_tree").html(getLayout_html(lheight,lwidth,emp_w,pageName));
	ShowDeptData(pageName)
}
function getLayout_html(lheight,lwidth,emp_w,pageName)
{
	lwidth=lwidth!=undefined?lwidth:260
	var w=$("#id_content").width()-5
	var emp_w=(emp_w!=undefined&&emp_w!='')?emp_w:w-lwidth-10
	
	var layout_html="<table width=100% ><tr><td class=border_td style='width:"+(lwidth!=undefined?lwidth:260)+"px;'>"
		+"<div >"
			+"<div id=id_opt_title>"
				+"<span>"+gettext("Department")+"</span>"
				+"<span id=id_opt_tree>"
				+"<input type='checkbox' id='id_cascadecheck_"+pageName+"'/>"+gettext("级联下级单位")+"</span>"
			+"</div>"
			+"<div id='showTree_"+pageName+"' class='ztree' style='overflow:auto;height:"+lheight+"px;width:"+(lwidth!=undefined?lwidth:260)+"px;'></div>"
		+"</div></td>"
		+"<td class='border_td'><div>"
			+"<div><span class='title_bar'>"+gettext("Employee")+"</span></div>"
			+"<div style='overflow:hidden;height:"+lheight+"px;width:"+emp_w+"px;' id='id_emp'><table id='id_grid_"+pageName+"' ></table><div id='id_pager_"+pageName+"'></div></div>"
		+"</td></tr></table>"
		+"<input type='hidden' value='' id='hidden_depts' />"
		+"<input type='hidden' value='' id='hidden_deptsName' />"
		+"<input type='hidden' value='' id='hidden_selDept' />"
	return layout_html;
}




//加载提示项目显示样式
function gethrreminddiaplay(lheight,lwidth,ds){
	$("#"+page_tab).html(getLayout_ihrreminded(lheight,lwidth));
	Showihrremined('ihrremined')
	
}

function getreverselist(lheight,lwidth,ds){
	$("#"+page_tab).html(getLayout_reverse(lheight,lwidth));
	Showreverse('reverse')
}

function getLayout_Dept_ex(lheight,lwidth)
{	
	jqOptions.height=lheight-80;
	lwidth=lwidth!=undefined?lwidth:260
	w=$("#id_content").width()-5
	grid_w=w-lwidth-20
	var h=lheight-30
	var layout_html="<table width="+w+"px><tr><td class='border_td' style='width:"+lwidth+"px;'>"
						+"<div>"
								+"<div id='id_opt_title'>"
									+"<span>"+gettext("Department")+"</span>"
									+"<span id='id_opt_tree'>"
									+"<input type='checkbox' id='id_contain_chl_"+page_tab+"'/>"+gettext("Contain Children")+"</span>"
								+"</div>"
						        +"<div id='showTree' style='overflow:auto;height:"+h+"px;width:"+(lwidth!=undefined?lwidth:260)+"px;'></div>"
						+"</div></td>"
						+"<td class='border_td'><div>"
							+"<div><span class='title_bar'>"+gettext("Employee")+"</span></div>"
								+"<div id='id_empl' style='height:"+h+"px;width:"+grid_w+"px;'"+"><table id=id_"+page_tab+"grid ></table><div id=id_"+page_tab+"pager></div></div>"
						+"</div>"
						+"</td></tr></table>"
						+"<input type='hidden' value='' id='hidden_depts' />"
						+"<input type='hidden' value='' id='hidden_deptsName' />"
						+"<input type='hidden' value='' id='hidden_selDept' />"

//						+"<div id='hidden_selDept' style='display:none'></div>"
	return layout_html;
}

function getLayout_ihrreminded(lheight,lwidth)
{	
	jqOptions.height=$("#id_content").height()-100;
	lwidth=lwidth!=undefined?lwidth:260
	w=$("#id_content").width()-5
	grid_w=w-lwidth-20
	var h=$("#id_content").height()-70
	var layout_html="<table  width="+w+"px><tr>"
						+"<td class='border_td' style='width:"+lwidth+"px;'><div>"
								+"<div id='id_opt_title'>"
									+"<span>"+gettext("人员日期提醒")+"</span>"

								+"</div>"
								+"<div id='showremindTree' class='ztree' style='overflow:auto;height:"+h+"px;width:"+(lwidth!=undefined?lwidth:260)+"px;'></div>"
						+"</div></td>"
					
						+"<td class='border_td'><div>"
								+"<div id='id_empl' style='height:"+h+"px;width:"+grid_w+"px;'"+"><table id=id_grid_"+page_tab+" ></table><div id=id_pager_"+page_tab+"></div></div>"
						+"</div>"
						+"</td></tr></table>"

	return layout_html;
}

function getLayout_reverse(lheight,lwidth)
{	
	jqOptions.height=$("#id_content").height()-100;
	lwidth=lwidth!=undefined?lwidth:260
	w=$("#id_content").width()-5
	grid_w=w-lwidth-20
	var h=$("#id_content").height()-70
	var layout_html="<table  width="+w+"px><tr>"
						+"<td class='border_td' style='width:"+lwidth+"px;'><div>"
								+"<div id='id_opt_title'>"
									+"<span>"+gettext("人员异常查询")+"</span>"

								+"</div>"
								+"<div id='showreverseTree' class='ztree' style='overflow:auto;height:"+h+"px;width:"+(lwidth!=undefined?lwidth:260)+"px;'></div>"
						+"</div></td>"
					
						+"<td class='border_td'><div>"
								+"<div id='id_empl' style='height:"+h+"px;width:"+grid_w+"px;'"+"><table id=id_grid_"+page_tab+" ></table><div id=id_pager_"+page_tab+"></div></div>"
						+"</div>"
						+"</td></tr></table>"

	return layout_html;
}

function IsContain(arr,value)
{
  for(var i=0;i<arr.length;i++)
  {
     if(arr[i]==value)
      return true;
  }
  return false;
}
//更新所选择的授权部门   
function click_dept_checkbox(obj){
	var selectDept=[];
	var deptid=$(obj).attr("alt");
	var deptName=$(obj).attr("alt2");
	if(typeof(selectDept)!='undefined'){
		var flag=IsContain(selectDept,deptid)
		if($(obj).prop("checked"))
			{
				if(!flag){   //选中  不存在 加入;
					if(selectDept.length==0)
						names+=deptName
					else
						names+=","+deptName
					selectDept.push(deptid);
				}
			}
		else
			{
				if(flag){  //不选中 存在 删除
					for(var i=0;i<selectDept.length;i++){
						if(deptid==selectDept[i])
							selectDept.splice(i,1)
					}
					names=names.replace(","+deptName," ")
				}	
			}
	}
}
//单击+号 自动将 已授权的部门 复选上
function show_selected_dept(){
	if(typeof(selectDept)!='undefined'){
		for(var i=0;i<selectDept.length;i++)
			{
				$.each($(".file input"),function(){
						if($(this).attr("alt")==selectDept[i]) 
							$(this).attr("checked","checked")
					
				});
				$.each($(".folder input"),function(){
					if($(this).attr("alt")==selectDept[i]) 
						$(this).attr("checked","checked")
				});
			}
	}

}

//单击 部门名称 ----- 人员 
function click_dept_file(obj){
		$("#id_addsch_tmpShift").attr("disabled","disabled");
		$.cookie("q","",{expires:0});
		var deptID=$(obj).attr("alt");
		var deptName=$(obj).attr("alt1")
		$("#hidden_selDept").val(deptID);
		$("#hidden_depts").val(deptID);
		$("#hidden_deptsName").val(deptName)
		renderEmpTbl(1,'id_cascadecheck');
}

//加载提醒醒目
function Showihrremined(page)
{
    var ComeTime=$("#id_ComeTime").val();
	var setting = {
	           check: {enable: false},          
	    async: {
			    enable: true,
			    url: "/iclock/att/getData/?func=ihrremind&cometime="+ComeTime ,
			    autoParam: ["id"]
		    },
			callback: {
				onClick: showhrreminddetail
			},
			data: {
				simpleData: {
					enable: true,
					idKey: "id",
					pIdKey: "pid",
					rootPId: 0
				}
			}
	};
	$.fn.zTree.init($("#showremindTree"), setting,null);	
}
function Showreverse(page)
{
	var setting = {
	           check: {enable: false},          
	    async: {
			    enable: true,
			    url: "/iclock/att/getData/?func=reverse",
			    autoParam: ["id"]
		    },
			callback: {
				onClick: showhreversedetail
			},
		data: {
			simpleData: {
				enable: true,
				idKey: "id",
				pIdKey: "pid",
				rootPId: 0
			}
		}
			
	};
	$.fn.zTree.init($("#showreverseTree"), setting,null);	
}


// 渲染 人员
function renderEmpTbl(p,checkid){
	deptID=$.cookie("dept_ids");
	var ischecked=0;
	if($("#"+checkid).prop("checked"))
		ischecked=1;
	var thtml='empsInDept.html'
	if(checkid=='id_contain_chl')
		thtml='empsInDepts.html'
	if($.cookie("q")==null||$.cookie("q")=="")
		urlStr="/iclock/att/getData/?func=employees&l=50&t="+thtml+"&DeptID__DeptID__in="+deptID+"&p="+p+"&isContainChild="+ischecked;
	else
		urlStr="/iclock/att/getData/?func=employees&l=50&t="+thtml+"&DeptID__DeptID__in="+deptID+"&q="+$.cookie("q")+"&p="+p+"&isContainChild="+ischecked
	var text=$.ajax({
		type:"POST",
		url: urlStr,
		async: false
		}).responseText;
	if ($("#id_form").is("div"))
	{
	    $("#id_form").find("#id_emp").html(text);
	}else if($("#show_dept_emp_tree").is("div")){
		$("#show_dept_emp_tree").find("#id_emp").html(text)
	}
	else
	{
	    $("#id_emp").html(text);
	}
	
}
function renderEmpTbl_Radio(p,checkid){
	deptID=$.cookie("dept_ids");
	var ischecked=0;
	if($("#"+checkid).prop("checked"))
		ischecked=1;
	if($.cookie("q")==null||$.cookie("q")=="")
		urlStr="/iclock/att/getData/?func=employees&l=50&t=empsInDept_radio.html&DeptID__DeptID__in="+deptID+"&p="+p+"&isContainChild="+ischecked;
	else
		urlStr="/iclock/att/getData/?func=employees&l=50&t=empsInDept_radio.html&DeptID__DeptID__in="+deptID+"&q="+$.cookie("q")+"&p="+p+"&isContainChild="+ischecked
	var text=$.ajax({
		type:"POST",
		url: urlStr,
		async: false
		}).responseText;
	if ($("#id_form").is("div"))
	{
	    $("#id_form").find("#id_emp").html(text);
	}else if($("#show_dept_emp_tree").is("div")){
		$("#show_dept_emp_tree").find("#id_emp").html(text)
	}
	else
	{
	    $("#id_emp").html(text);
	}
}

function renderEmp_ex(p){
	//deptID=$.cookie("dept_ids");
	deptID=$("#show_dept_emp_tree_"+page_tab).find("#hidden_selDept").val()
	var ischecked=0;
	if($("#id_contain_chl_"+page_tab).prop("checked"))
		ischecked=1;
	if($.cookie("q")==null||$.cookie("q")=="")
		urlStr="/iclock/data/employee/?t=employee_shift.js&deptIDs="+deptID+"&isContainChild="+ischecked
	else
		urlStr="/iclock/data/employee/?t=employee_shift.js&deptIDs="+deptID+"&q="+$.cookie("q")+"&p="+p+"&isContainChild="+ischecked
	jqOptions.url=urlStr	
	jqOptions.pager='#id_'+page_tab+'pager';
	$("#id_"+page_tab+"grid").jqGrid('GridUnload')
	//$.jgrid.gridUnload("#id_"+page_tab+"grid" )
	$("#id_"+page_tab+"grid").jqGrid(jqOptions)
//	$("#id_"+page_tab+"_grid").jqGrid('setGridParam',{url:urlStr}).trigger("reloadGrid");

/*
	var text=$.ajax({
		type:"POST",
		url: urlStr,
		async: false
		}).responseText;
	if ($("#id_form").is("div"))
	{
	    $("#id_form").find("#id_empl").html(text);
	}else if($("#show_dept_emp_tree").is("div")){
		$("#show_dept_emp_tree").find("#id_empl").html(text)
	}
	else
	{
	    $("#id_empl").html(text);
	}
*/


	
}

function renderEmp_finger(p){
	//deptID=$.cookie("dept_ids");
	deptID=$("#show_dept_emp_tree_"+page_tab).find("#hidden_selDept").val()
	var ischecked=0;
	if($("#id_contain_chl_"+page_tab).prop("checked"))
		ischecked=1;
	if($.cookie("q")==null||$.cookie("q")=="")
		urlStr="/iclock/data/fptemp/?deptIDs="+deptID+"&isContainChild="+ischecked
	else
		urlStr="/iclock/data/fptemp/?deptIDs="+deptID+"&q="+$.cookie("q")+"&p="+p+"&isContainChild="+ischecked
	jqOptions.url=urlStr	
	jqOptions.pager="#id_pager";
	var height=$("#id_empl").height()-60;
	jqOptions.height=height;	
	$("#id_grid").jqGrid('GridUnload')
	//$.jgrid.gridUnload("#id_grid" )
	$("#id_grid").jqGrid(jqOptions)
	//$("#id_"+page_tab+"_grid").jqGrid('setGridParam',{url:urlStr}).trigger("reloadGrid");
}

function renderEmp_face(p){
	//deptID=$.cookie("dept_ids");
	deptID=$("#show_dept_emp_tree_"+page_tab).find("#hidden_selDept").val()
	var ischecked=0;
	if($("#id_contain_chl_"+page_tab).prop("checked"))
		ischecked=1;
	if($.cookie("q")==null||$.cookie("q")=="")
		urlStr="/iclock/data/facetemp/?deptIDs="+deptID+"&isContainChild="+ischecked
	else
		urlStr="/iclock/data/facetemp/?deptIDs="+deptID+"&q="+$.cookie("q")+"&p="+p+"&isContainChild="+ischecked
	jqOptions.url=urlStr	
	jqOptions.pager="#id_pager";
	//jqOptions.autowidth=true
	var height=$("#id_empl").height()-60;
	jqOptions.height=height;	
	$("#id_grid").jqGrid('GridUnload')
	//$.jgrid.gridUnload("#id_grid" )
	$("#id_grid").jqGrid(jqOptions)
	//$("#id_"+page_tab+"_grid").jqGrid('setGridParam',{url:urlStr}).trigger("reloadGrid");
}


/**
function renderDevsTb(p){
	urlStr="/iclock/att/getData/?func=devs&l=10&t=devsInUserAC.html&p="+p;
	var text=$.ajax({
		type:"POST",
		url: urlStr,
		async: false
		}).responseText;
	if ($("#id_form").is("div"))
	{
	    $("#id_form").find("#id_devs").html(text);
	}
	else
	{
	    $("#id_devs").html(text);
	}
	
}

function showSelected_dev(){
    var c = 0;
	$("#id_addsch_tmpShift").attr("disabled","disabled");
    $.each($(".class_select_dev"),function(){
			if(this.checked) c+=1;})
    $("#selected_count_dev").html("" + c);
}
function check_all_for_row_dev(checked) {

    if (checked) {
        $(".class_select_dev").attr("checked", "true");
    } else {
        $(".class_select_dev").removeAttr("checked");
    }
    showSelected_dev();
}


**/
function getDeptTree(s,c){   //得到部门树
	show=s;
	check=c;
	var tree="<ul id='deptBrowser' class='filetree' style='margin-left:0px;color: black;'>";
	tree+=getTreeString(department,show,check)+"</ul>"

	tree+="<input type='hidden' value='' id='hidden_depts' />"
		+"<input type='hidden' value='' id='hidden_deptsName' />"
		+"<input type='hidden' value='' id='hidden_selDept' />"
	return tree;
}


function showSelected_emp(){
    var c = 0;
	$("#id_addsch_tmpShift").attr("disabled","disabled");
    $.each($(".class_select_emp"),function(){
			if(this.checked) c+=1;})
    $("#selected_count").html("" + c);
}

function check_all_for_row_emp(checked) {

    if (checked) {
        $(".class_select_emp").attr("checked", "true");
    } else {
        $(".class_select_emp").removeAttr("checked");
    }
    showSelected_emp();
}


function getSelected_emp() {
	var emp=[];
	$.each($(".class_select_emp"),function(){
			if(this.checked)
				emp.push(this.id)
	});
	return emp;
}
//得到Grid选中行的id列表，建议使用此函数替换getSelected_emp_ex
function getSelectedIDs(page_style) {
	if (!page_style)
		page_style=tblName[g_activeTabID]
	
	var ss=$("#id_grid_"+page_style).jqGrid('getGridParam','multiselect')
	if(ss){
		var emp=$("#id_grid_"+page_style).jqGrid('getGridParam','selarrrow');
		if(typeof emp=='undefined') emp=[]
	}else{
		var emp=$("#id_grid_"+page_style).jqGrid('getGridParam','selrow');
		if(typeof emp=='undefined') emp=[]
	}
	return emp
}


function getSelected_emp_ex(page_style) {
	var ss=$("#id_grid_"+page_style).jqGrid('getGridParam','multiselect')
	if(ss){
		var emp=$("#id_grid_"+page_style).jqGrid('getGridParam','selarrrow');
		if(typeof emp=='undefined') emp=[]
	}else{
		var emp=$("#id_grid_"+page_style).jqGrid('getGridParam','selrow');
		if(typeof emp=='undefined') emp=''
	}
	return emp
}

function getSelected_empPin() {
	var pin=[];
	$.each($(".class_select_emp"),function(){
			if(this.checked) 
				pin.push(this.alt)
	});
	return pin;
}
function getSelected_empid() {
	var id=[];
	$.each($(".class_select_emp"),function(){
			if(this.checked) 
				id.push(this.id)
	});
	return id;
}

function getSelected_empNames(){
	var empNames=[];
	$.each($(".class_select_emp"),function(){
			if(this.checked)
				empNames.push(this.name)
	});
	return empNames;
}
//得到所有选中部门的ID,注意tree_obj前面不要加#
function getSelected_dept(tree_obj)
{
	if ( typeof tree_obj == "string" )
		var zTree = $.fn.zTree.getZTreeObj(tree_obj)
	else
		var zTree = $.fn.zTree.getZTreeObj("id_dept")
	var depts=[]
	if (zTree!=null)
	{
		//getCheckedNodes(true)
		if(zTree.setting.check.enable){
			var nodes = zTree.getCheckedNodes(true)
		}else{
			var nodes = zTree.getSelectedNodes()
		}
		for(var i=0;i<nodes.length;i++){
			
			//var halfCheck = nodes[i].getCheckStatus();
			//if(halfCheck==null || !halfCheck.half)
				depts.push(nodes[i].id);
		}
	}
	return depts
}






function getSelected_deptNames(tree_obj) {//得到所有选中部门的名称

	var zTree = $.fn.zTree.getZTreeObj(tree_obj)
	if(zTree.setting.check.enable){
		var nodes = zTree.getCheckedNodes(true)
	}else{
		var nodes = zTree.getSelectedNodes()
	}
	var depts=[]
	for(var i=0;i<nodes.length;i++){
		depts.push(nodes[i].name);
	}
	//return formatArrayEx(depts);
	return depts;
}

function showDeptment (obj) {
	var top =  $("#department",obj).position().top;
	var left =  $("#department",obj).position().left;
	var d_height=$("#department",obj).height();
	$("#show_deptment",obj).css("display","block").css({position: 'absolute',"top": top+d_height+6+'px',"left": left+'px'});
}
function showDeptments () {
	var top =  $("#departments").position().top;
	var left =  $("#departments").position().left;
	var d_height=$("#departments").height();
	$("#show_deptments").css("display","block").css({position: 'absolute',"top": top+d_height+6+'px',"left": left+'px'});
}

function hideDeptment () {
	$("#show_deptment").css("display","none").css("top", -1000).css("left",  -1000);
}
function hide_Autued_Deptment () {
	$("#show_Autued_deptment").css("display","none").css("top", -1000).css("left",  -1000);
}
function hideDeptments () {
	$("#show_deptments").css("display","none").css("top", -1000).css("left",  -1000);
}

function hideFields () {
	$("#show_field").css("display","none").css("top", -1600).css("left",  -1600);
}
function save_hideDeptment (){//保存选中部门
	hideDeptment ();
	var dept_ids=getSelected_dept();
	$.cookie("dept_ids",dept_ids, { expires: 7 });
	var dept_names=getSelected_deptNames();
	$("#department").val(dept_names);
	//renderEmpTbl(1);
	$.each($(".class_select_emp"),function(){
			this.checked=false
	});

	$.cookie("emp",'', { expires: 7 });


}

function showEmployee () {
	var top =  $("#Employee").position().top;
	var left =  $("#Employee").position().left;
	var e_height=$("#Employee").height();

	$("#show_emp").css("display","block").css("top", top+e_height+6).css("left", left);
	$.cookie("pin","", { expires: 0 });
}
function hideEmployee () {
	$("#show_emp").css("display","none").css("top", -1500).css("left",  -1500);
}
function save_hideEmployee(){//保存选中人员
	$("#show_emp").css("display","none").css("top", -1500).css("left",  -1500);
	showEmployeeEmployee();
}
function showEmployeeEmployee () {
	names=getSelected_empNames();
	$("#Employee").val(names);

}


//page:_id,tag:为true时不显示check,isDiy:是否在部门右边增加自定义控件，目前仅授权部门的功能需要
function createQueryDlgbypage(page,tag,isDiy)//生成部门框
{

	if(page==undefined){
		page=''
	}
   var html="<div id='dlg_for_query_"+page+"' style='overflow:hidden;'>"
		+"<div id='dlg_dept_"+page+"' class='dlgdiv'>"
			+"<div id='dlg_dept_title_"+page+"' class='cascadecheck'><input type='checkbox' id='id_cascadecheck_"+page+"'/>"+gettext('级联下级单位')+"</div>"
   			+"<div id='dlg_dept_body_"+page+"' style='overflow:hidden;'>"
				+"<ul id='showTree_"+page+"' class='ztree' style='height:300px;overflow:auto;'></ul>"
			+"</div>"
		+"</div>"
		+"<div id='dlg_emp_"+page+"' style='display:none'>"
		+"<div id='dlg_emp_title_"+page+"'>"
		+"<div style='float:left;width:100px;text-align:left;height: 20px;;'><input type='button' value='"+gettext("查询")+"' id='searchbydept_"+page+"' title='"+gettext("根据部门查询人员")+"'  onclick='showgridbydept(\""+page+"\")' ></div><input id='search_"+page+"' style='height: 18px; position: relative; top: -7px;'/><img src='/media/img/filter.gif' style='height:24px;' title='"+gettext('默认查询所有部门')+"' onclick='showgridsearch(\""+page+"\")'></div>"
		+"<div id='dlg_emp_body_"+page+"'>"
		+"<table id='id_grid_"+page+"' ></table><div id='id_pager_"+page+"'></div>"
		+"</div>"
		+"</div>"
		+"<div id='dlg_other_"+page+"' style='display:none'>"
			+"<div id='dlg_other_title_"+page+"'></div>"
			+"<div id='dlg_other_body_"+page+"'>"
				+"<span id='id_error' style='display:none;float:right'></span>"
			+"</div>"
		+"</div>"
   +"</div>"

	$(html).dialog({modal:true,resizable:false,
			//dialogClass: "no-close",
			width: 410,
			height:440,
                        position: { my: "center", at: "center"},
						  buttons:[{id:"btnShowOK",text:gettext('确定'),
								  click:function(){save_hideDeptments(page);}},
								 {id:"btnShowCancel",text:gettext('Return'),click:function(){$(this).dialog("destroy"); }
								}],
                                                  open:function(){ShowDeptData(page,tag,isDiy);},
						  close:function(){$(this).dialog("destroy"); } 		
						})
}

function cascadecheckchange(page,check){//级联修改ztree的setting
	var zTree = $.fn.zTree.getZTreeObj("showTree_"+page)
	type = { "Y": "", "N": "" };
	if(check){
		type = { "Y": "s", "N": "s" };
	}
	zTree.setting.check.chkboxType = type;
}

function createQueryDlgbypage_zone(page,tag,isDiy)//生成部门框
{

	if(page==undefined){
		page=''
	}
   var html="<div id='dlg_for_query_"+page+"' style='overflow:hidden;'>"
		+"<div id='dlg_dept_"+page+"' class='dlgdiv'>"
			+"<div id='dlg_dept_title_"+page+"' class='cascadecheck'><input type='checkbox' id='id_cascadecheck_"+page+"'/>"+gettext('级联下级区域')+"</div>"
   			+"<div id='dlg_dept_body_"+page+"' style='overflow:hidden;'>"
				+"<ul id='showTree_"+page+"' class='ztree' style='height:300px;overflow:auto;'></ul>"
			+"</div>"
		+"</div>"
		+"<div id='dlg_emp_"+page+"' style='display:none'>"
		+"<div id='dlg_emp_title_"+page+"'>"
		+"<div style='float:left;width:100px;text-align:left;height: 20px;;'><input type='button' value='"+gettext("查询")+"' id='searchbydept_"+page+"' title='"+gettext("根据部门查询人员")+"'  onclick='showgridbydept(\""+page+"\")' ></div><input id='search_"+page+"' style='height: 18px; position: relative; top: -7px;'/><img src='/media/img/filter.gif' style='height:24px;' title='"+gettext('默认查询所有部门')+"' onclick='showgridsearch(\""+page+"\")'></div>"
		+"<div id='dlg_emp_body_"+page+"'>"
		+"<table id='id_grid_"+page+"' ></table><div id='id_pager_"+page+"'></div>"
		+"</div>"
		+"</div>"
		+"<div id='dlg_other_"+page+"' style='display:none'>"
			+"<div id='dlg_other_title_"+page+"'></div>"
			+"<div id='dlg_other_body_"+page+"'>"
				+"<span id='id_error' style='display:none;float:right'></span>"
			+"</div>"
		+"</div>"
   +"</div>"

	$(html).dialog({modal:true,resizable:false,
			dialogClass: "no-close",
			width: 410,
			height:430,
                        position: { my: "center", at: "center"},
						  buttons:[{id:"btnShowOK",text:gettext('确定'),
								  click:function(){save_hideDeptments(page);}},
								 {id:"btnShowCancel",text:gettext('Return'),click:function(){$(this).dialog("destroy"); }
								}],
                                                  open:function(){ShowZoneData(page,tag,isDiy);},
						  close:function(){$(this).dialog("destroy"); } 		
						})
}


function addDiyDom(treeId, treeNode) {
	IDMark_A = "_a";
	//if (treeNode.pid!=1&&treeNode.id!=1) return;
	if (treeNode.level>3) return;
	
	var aObj = $("#" + treeNode.tId + IDMark_A);
		//var editStr = "<select class='selDemo' id='diyBtn_" +treeNode.id+ "'><option value=1>包含下级</option><option value=2>不包含下级</option><option value=3>3</option></select>";
		var editStr="(<input  type='checkbox' maxlength='30'  id='diyBtn_"+treeNode.id+"' name='diyBtn' />级联下级)"
		aObj.after(editStr);
		var btn = $("#diyBtn_"+treeNode.id);
	//if (btn) btn.bind("click", function(){alert("diy Button for " + treeNode.name);});
}

function ShowDeptData(page,tag,isDiy)
{
	var setting = {
            check: {enable: !tag,chkStyle: "checkbox",chkboxType: { "Y": "", "N": "" }},          
	    async: {
			    enable: true,
			    url: "/iclock/att/getDeptData/?func=department&page="+page,
			    autoParam: ["id"]
		    }
	};
	if(isDiy){
			setting.view={
				addDiyDom: addDiyDom
			}
		
	}
	$.fn.zTree.init($("#showTree_"+page), setting,null);	
	$("#id_cascadecheck_"+page).click(function(){
		var check=$("#id_cascadecheck_"+page).prop("checked")
		cascadecheckchange(page,check)
	})
	if(tag){
		var zTree = $.fn.zTree.getZTreeObj("showTree_"+page);
		zTree.setting.check.enable = false;
		$("#searchbydept_"+page).hide()
		zTree.setting.callback.onClick = function onClick(e, treeId, treeNode){
			showgridbydept(page)
		}
	}
}

function ShowZoneData(page,tag,isDiy,url)
{
	var urlstr="/acc/getData/?func=zonetree"
	if(url){
		urlstr=url
	}
	var setting = {
            check: {enable: !tag,chkStyle: "checkbox",chkboxType: { "Y": "", "N": "" }},          
	    async: {
			    enable: true,
			    url: urlstr,
			    autoParam: ["id"]
		    }
	};
	if(isDiy){
			setting.view={
				addDiyDom: addDiyDom
			}
		
	}
	$.fn.zTree.init($("#showTree_"+page), setting,null);	
	$("#id_cascadecheck_"+page).click(function(){
		var check=$("#id_cascadecheck_"+page).prop("checked")
		cascadecheckchange(page,check)
	})
	if(tag){
		var zTree = $.fn.zTree.getZTreeObj("showTree_"+page);
		zTree.setting.check.enable = false;
		$("#searchbydept_"+page).hide()
		zTree.setting.callback.onClick = function onClick(e, treeId, treeNode){
			showgridbydept(page)
		}
	}
}

function dlgdestroy(page){
	$('#dlg_for_query_'+page).dialog("destroy");
}

function createDlgdeptfor(page,tag){//生成部门人员框
	createQueryDlgbypage(page,tag);
	$("#dlg_for_query_"+page).dialog({dialogClass: "",width:'862',height:'540'})
	$("#dlg_other_"+page).css('display','block')
	$("#dlg_emp_"+page).css('display','block')
	$("#dlg_for_query_"+page).css('padding','6px')
	$("#dlg_other_"+page).html()
	$("#dlg_other_"+page).css("width","850px")
	$("#dlg_other_"+page).css("height","50px")
	$("#dlg_emp_"+page).css("width","575px")
	$("#dlg_emp_title_"+page).addClass("cascadecheck")
	$("#dlg_emp_"+page).addClass("dlgempdiv")
	var height=$("#dlg_dept_"+page).height()
	$("#dlg_emp_"+page).css("height",height)
	$("#dlg_dept_"+page).css("width","250px")
	$("#dlg_emp_"+page).position({
		  my: "left top",
		  at: "right top",
		  of: "#dlg_dept_"+page
		});
	$("#dlg_other_"+page).position({
		  my: "left top",
		  at: "left bottom",
		  of: "#dlg_dept_"+page
		});
}


function showgridbydept(pagename){
	var dept_ids=getSelected_dept("showTree_"+pagename)
	if(dept_ids==''){
		alert(gettext("请选择部门"))
		return false;
	}
	var ischecked=0;
	if($("#id_cascadecheck_"+pagename).prop("checked"))
		ischecked=1;
	var jqOptions2=copyObj(jq_Options);
	if(pagename=='allowance_add')
	{
		url_caption="/iclock/att/getColModel/?dataModel=employeeForIssueCard"
		var url="/iclock/data/employee/?e=0&OffDuty=0&DelTag=0&deptIDs="+dept_ids+"&isvalidcard=1&isContainChild="+ischecked;	  
	}
	else
	{
		url_caption="/iclock/att/getColModel/?dataModel=employee"
		var url="/iclock/data/employee/?e=0&t=employee_dept.js&OffDuty=0&DelTag=0&deptIDs="+dept_ids+"&isContainChild="+ischecked;
	}
	
	$.ajax({
	   type:"GET",
	   url:url_caption,
	   dataType:"json",
	   data:'',
	   success:function(json){
		   jqOptions2.colModel=json['colModel']
		   jqOptions2.sortname="DeptID,PIN";
		   jqOptions2.sortorder="";
		   jqOptions2.url=url
		   jqOptions2.height=$('#dlg_dept_body_'+pagename).height()-60
		   jqOptions2.gridComplete=''
		jqOptions2.pager="#id_pager_"+pagename;
		renderGridData(pagename,jqOptions2)
	   }
	});
}

function showgridsearch(pagename){
	var v=$("#search_"+pagename).val()
	var jqOptions2=copyObj(jq_Options);
	$.ajax({
	   type:"GET",
	   url:"/iclock/att/getColModel/?dataModel=employee",
	   dataType:"json",
	   data:'',
	   success:function(json){
		   jqOptions2.colModel=json['colModel']
		   jqOptions2.sortname="DeptID,PIN";
		   jqOptions2.sortorder="";
		   jqOptions2.url="/iclock/data/employee/?q="+escape(v)
		   jqOptions2.height=$('#dlg_dept_body_'+pagename).height()-60
		   jqOptions2.gridComplete=''
		jqOptions2.pager="#id_pager_"+pagename;
		renderGridData(pagename,jqOptions2)
	   }
	});
}

function getDeptEmpData(page,height,tag){
	if(height==undefined){
		height=355
	}
	var zTree = $.fn.zTree.getZTreeObj("showTree_"+page);
	zTree.setting.check.enable = false;
	$("#searchbydept_"+page).hide()
	zTree.setting.callback.onClick = function onClick(e, treeId, treeNode){
		var deptID=treeNode.id;
		var deptName=treeNode.name;
		$.cookie("dept_ids",deptID, { expires: 7 });
		$("#hidden_selDept").val(deptID);
		$("#hidden_depts").val(deptID);
		$("#hidden_deptsName").val(deptName)
		var ischecked=0;
		if($("#id_cascadecheck_"+page).prop("checked"))
			ischecked=1;
		urlStr="/iclock/data/employee/?e=0&t=employee_dept.js&deptIDs="+deptID+"&isContainChild="+ischecked+'&OffDuty=0'
		savecookie("search_urlstr",urlStr);
		var jqOptions2=copyObj(jq_Options);
		$.ajax({
			type:"GET",
			url:"/iclock/att/getColModel/?dataModel=employee",
			dataType:"json",
			data:'',
			success:function(json){
				jqOptions2.colModel=json['colModel']
				jqOptions2.height=height
				if(tag){
					jqOptions2.multiselect=false
				}
				jqOptions2.url=urlStr
				jqOptions2.sortname='PIN'
				jqOptions2.pager="#id_pager_"+page;
				renderGridData(page,jqOptions2)
			}
		});
	}
}

function createQueryDlgbypage10(page,tag,isDiy)//生成部门框
{

	if(page==undefined){
		page=''
	}
	var html="<div id='dlg_for_query_"+page+"' style='overflow:hidden;'>"
		     +"<div id='dlg_dept_"+page+"' class='dlgdiv'>"
			     +"<div id='dlg_dept_title_"+page+"' class='cascadecheck'><input type='checkbox' id='id_cascadecheck_"+page+"'/>"+gettext('级联下级单位')+"</div>"
			     +"<div id='dlg_dept_body_"+page+"' style='overflow:hidden;'>"
				     +"<ul id='showTree_"+page+"' class='ztree' style='height:300px;overflow:auto;'></ul>"
			     +"</div>"
		     +"</div>"
		     +"<div id='dlg_emp_"+page+"' style='display:none'>"
		     +"<div id='dlg_emp_title_"+page+"'>"
		     +"<div style='float:left;width:100px;text-align:left;height: 20px;;'><input type='button' value='"+gettext("查询")+"' id='searchbydept_"+page+"' title='"+gettext("根据单位查询人员")+"'  onclick='showgridbydept10(\""+page+"\")' ></div><input id='search_"+page+"' style='height: 18px; position: relative; top: -7px;'/><img src='/media/img/filter.gif' style='height:24px;' title='"+gettext('默认查询所有部门')+"' onclick='showgridsearch10(\""+page+"\")'></div>"
		     +"<div id='dlg_emp_body_"+page+"'>"
		     +"<table id='id_grid_"+page+"' ></table><div id='id_pager_"+page+"'></div>"
		     +"</div>"
		     +"</div>"
		     +"<div id='dlg_emp_sel_"+page+"' style='display:none'>"
		     +"<div id='dlg_emp_sel_title_"+page+"'>"
		     +"<div style='float:left;width:100px;text-align:left;height: 20px;'>"+gettext("已选人员")+"</div></div>"
		     +"<div id='dlg_emp_sel_body_"+page+"'>"
		     +"<table id='id_grid_sel_"+page+"' ></table><div id='id_pager_sel_"+page+"'></div>"
		     +"</div>"
		     +"</div>"
		     +"<div id='dlg_other_"+page+"' style='display:none'>"
			     +"<div id='dlg_other_title_"+page+"'></div>"
			     +"<div id='dlg_other_body_"+page+"'>"
				     +"<span id='id_error' style='display:none;float:right'></span>"
			     +"</div>"
		     +"</div>"
	+"</div>"

	$(html).dialog({modal:true,resizable:false,
			dialogClass: "no-close",
			width: 820,
			height:430,
                        position: { my: "center", at: "center"},
						  buttons:[{id:"btnShowOK",text:gettext('确定'),
								  click:function(){save_hideDeptments(page);}},
								 {id:"btnShowCancel",text:gettext('Return'),click:function(){$(this).dialog("destroy"); }
								}],
                                                  open:function(){ShowDeptData10(page,tag,isDiy);},
						  close:function(){$(this).dialog("destroy"); } 		
						})
}

function createDlgdeptfor10(page,tag){//生成部门人员框
	createQueryDlgbypage10(page,tag);
	$("#dlg_for_query_"+page).dialog({dialogClass: "",width:'1028',height:'500'})
	$("#dlg_emp_"+page).css('display','block')
	$("#dlg_emp_sel_"+page).css('display','block')
	$("#dlg_for_query_"+page).css('padding','6px')
	$("#dlg_emp_"+page).css("width","430px")
	$("#dlg_emp_title_"+page).addClass("cascadecheck")
	$("#dlg_emp_"+page).addClass("dlgempdiv")
	$("#dlg_emp_sel_"+page).css("width","330px")
	$("#dlg_emp_sel_title_"+page).addClass("cascadecheck")
	$("#dlg_emp_sel_"+page).addClass("dlgempdiv")
	var height=$("#dlg_dept_"+page).height()
	$("#dlg_emp_"+page).css("height",height)
	$("#dlg_emp_sel_"+page).css("height",height)
	$("#dlg_dept_"+page).css("width","250px")
	$("#dlg_emp_"+page).position({
		  my: "left top",
		  at: "right top",
		  of: "#dlg_dept_"+page
		});
	$("#dlg_emp_sel_"+page).position({
		  my: "left top",
		  at: "right top",
		  of: "#dlg_emp_"+page
		});
	
}

function ShowDeptData10(page,tag,isDiy)
{
	var setting = {
            check: {enable: !tag,chkStyle: "checkbox",chkboxType: { "Y": "", "N": "" }},          
	    async: {
			    enable: true,
			    url: "/iclock/att/getDeptData/?func=department",
			    autoParam: ["id"]
		    }
	};
	if(isDiy){
			setting.view={
				addDiyDom: addDiyDom
			}
		
	}
	$.fn.zTree.init($("#showTree_"+page), setting,null);	
	$("#id_cascadecheck_"+page).click(function(){
		var check=$("#id_cascadecheck_"+page).prop("checked")
		cascadecheckchange(page,check)
	})
	if(tag){
		var zTree = $.fn.zTree.getZTreeObj("showTree_"+page);
		zTree.setting.check.enable = false;
		$("#searchbydept_"+page).hide()
		zTree.setting.callback.onClick = function onClick(e, treeId, treeNode){
			showgridbydept10(page)
		}
	}
}


function showgridbydept10(pagename,other){
	var dept_ids=getSelected_dept("showTree_"+pagename)
	if(dept_ids==''){
		alert(gettext("请选择部门"))
		return false;
	}
	var ischecked=0;
	if($("#id_cascadecheck_"+pagename).prop("checked"))
		ischecked=1;
	var jqOptions2=copyObj(jq_Options);
	var jqOptions3=copyObj(jq_Options);
	var url="/iclock/data/employee/?e=0&t=employee_dept.js&deptIDs="+dept_ids+"&isContainChild="+ischecked;
	if(other){
		url+="&"+other
	}else{
		url+="&OffDuty=0"
	}
	$.ajax({
	   type:"GET",
	   url:"/iclock/att/getColModel/?dataModel=employee",
	   dataType:"json",
	   data:'',
	   success:function(json){
		   jqOptions2.colModel=json['colModel']
		   jqOptions2.sortname="DeptID,PIN";
		   jqOptions2.sortorder="";
		   jqOptions2.url=url
		   jqOptions2.height=$('#dlg_dept_body_'+pagename).height()-60
		   jqOptions2.gridComplete=''
		jqOptions2.pager="#id_pager_"+pagename;
		jqOptions2.onSelectRow=function(id){
			var slt = $("#id_grid_"+pagename).jqGrid('getGridParam','selarrrow');
			var selslt = $("#id_grid_sel_"+pagename).jqGrid('getGridParam','selarrrow');
			var rows=$("#id_grid_"+pagename).jqGrid("getCol",1,true)
			for(var i=0;i < rows.length;i++)
			{
				var rowid=rows[i].id
				if (searchemp(rowid,slt,selslt)==1){
					var dataRow=$("#id_grid_"+pagename).jqGrid("getRowData",rowid);
					$("#id_grid_sel_"+pagename).jqGrid("addRowData", rowid, dataRow, "first");
					$("#id_grid_sel_"+pagename).setSelection(rowid, true); 
				}
				if(searchemp(rowid,slt,selslt)==0){
					$("#id_grid_sel_"+pagename).jqGrid("delRowData", rowid)
				}
			}
		}
		jqOptions2.onSelectAll=function(id){
			var slt = $("#id_grid_"+pagename).jqGrid('getGridParam','selarrrow');
			var selslt = $("#id_grid_sel_"+pagename).jqGrid('getGridParam','selarrrow');
			var rows=$("#id_grid_"+pagename).jqGrid("getCol",1,true)
			for(var i=0;i < rows.length;i++)
			{
				var rowid=rows[i].id
				if (searchemp(rowid,slt,selslt)==1){
					var dataRow=$("#id_grid_"+pagename).jqGrid("getRowData",rowid);
					$("#id_grid_sel_"+pagename).jqGrid("addRowData", rowid, dataRow, "first");
					$("#id_grid_sel_"+pagename).setSelection(rowid, true); 
				}
				if(searchemp(rowid,slt,selslt)==0){
					$("#id_grid_sel_"+pagename).jqGrid("delRowData", rowid)
				}
			}
		}	    
			
		renderGridData(pagename,jqOptions2)
		jqOptions3.colModel=[
			{'name':'id','hidden':true},
			{'name':'PIN','index':'PIN','width':60,'label':gettext("PIN"),'frozen':true},
			{'name':'EName','width':60,'label':gettext("name"),'frozen': true},
			{'name':'DeptName','index':'DeptID__DeptName','width':150,'label':gettext("department name")},
	        ]
		   jqOptions3.sortname="DeptID,PIN";
		   jqOptions3.sortorder="";
		   jqOptions3.url=""
		   jqOptions3.datatype='local'
		   jqOptions3.height=$('#dlg_dept_body_'+pagename).height()-60
		   jqOptions3.gridComplete=''
		   jqOptions3.pgbuttons =false
		   jqOptions3.pginput =false
		   
		jqOptions3.pager="#id_pager_sel_"+pagename;
		$("#id_grid_sel_"+pagename).jqGrid(jqOptions3);
	   }
	});
}

function showgridsearch10(pagename){
	var v=$("#search_"+pagename).val()
	var jqOptions2=copyObj(jq_Options);
	$.ajax({
	   type:"GET",
	   url:"/iclock/att/getColModel/?dataModel=employee",
	   dataType:"json",
	   data:'',
	   success:function(json){
		   jqOptions2.colModel=json['colModel']
		   jqOptions2.sortname="DeptID,PIN";
		   jqOptions2.sortorder="";
		   jqOptions2.url="/iclock/data/employee/?e=0&t=employee_dept.js&q="+escape(v);
		   jqOptions2.height=$('#dlg_dept_body_'+pagename).height()-60
		   jqOptions2.gridComplete=''
		jqOptions2.pager="#id_pager_"+pagename;
		renderGridData(pagename,jqOptions2)
	   }
	});
}

function searchemp(rowid,slt,selslt){
	var tag=0
	if(slt){
		for(var i=0;i<slt.length;i++){
			if(rowid==slt[i]){
				tag=1
			}
		}
	}
	if(tag&&selslt){
		for(var i=0;i<selslt.length;i++){
			if(rowid==selslt[i]){
				tag=2
			}
		}
	}
	return tag
}