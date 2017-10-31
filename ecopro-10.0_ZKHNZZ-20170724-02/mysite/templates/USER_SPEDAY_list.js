{% load i18n %}
{% load iclock_tags %}
{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"PIN":"{% if can_change %}{% ifequal item.State 0 %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.employee.PIN }}</a>{% else %}{% ifequal item.State 6 %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.employee.PIN }}</a>{% else %}{{ item.employee.PIN }}{% endifequal %}{% endifequal %}{% else %}{{ item.employee.PIN }}{%endif%}",
"UserID":"{{ item.UserID.id }}",
"DeptID":"{% if item.employee.bstate is 0%}{{ item.UserID_id|getborrowdatas:'deptid' }}{% else %}{% endif %}",
"DeptName":"{% if item.employee.bstate is 0%}{{ item.UserID_id|getborrowdatas:'deptname'}}{% else %}{% endif %}",
"Workcode":"{{ item.employee.Workcode|trim }}",
"EName":"{{ item.employee.EName|trim }}",
"Title":"{% if item.employee.bstate is 0%}{{ item.UserID_id|getborrowdatas:'title' }}{% else %}{% endif %}",
"bstate":"{{ item.employee.bstate|empborrowState }}",
"file":"{{ item|getFileUrl }}",
"StartSpecDay":"{{ item.StartSpecDay }}" ,
"EndSpecDay":"{{ item.EndSpecDay }}",
"DateID":"{{ item.DateID|Leave }}",
"process":"{{ item|showprocess }}",
"operate":"&nbsp;<a  title='查看审批详情' onclick='getProcessLog(\"{{ item.id }}\")'style='color:green;'>详情</a>&nbsp;",
"YUANYING":"{{ item.YUANYING|filteryuanyin }}",
"Place":"{{ item.USER_SPEDAY_DETAILS.Place|filteryuanyin|default:'' }}",
"mobile":"{{ item.USER_SPEDAY_DETAILS.mobile|default:'' }}",
"successor":"{{ item.USER_SPEDAY_DETAILS.successor|default:'' }}",
"remarks":"{{ item.USER_SPEDAY_DETAILS.remarks|filteryuanyin|default:'' }}",
"ApplyDate":"{{ item.ApplyDate }}",
"empid":"{{ item.employee.id|GetAnnualleaves_ex:item.StartSpecDay }}",
"empids":"{{ item.employee.id|GetUsedAnnualleaves:item.DateID }}",
"State":"{{ item.get_State_display|get_State_State }}",
"jiezhuang":"{{ item.get_jiezhuang_display|default:"" }}",
"tianshu":"{{ item.tianshu }}",
"jiezhuangDay":"{{ item.jiezhuangDay |default:'' }}",
"jieYUANYING":"{{ item.jieYUANYING |default:'' }}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
