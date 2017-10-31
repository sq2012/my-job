{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"PIN":"{% if can_change %}{% ifequal item.State 0 %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.employee.PIN }}</a>{% else %}{% ifequal item.State 6 %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.employee.PIN }}</a>{% else %}{{ item.employee.PIN }}{% endifequal %}{% endifequal %}{% else %}{{ item.employee.PIN }}{%endif%}",
"DeptID":"{{ item.employee.Dept.DeptNumber }}",
"DeptName":"{{ item.employee.Dept.DeptName }}",
"EName":"{{ item.employee.EName|trim }}",
"Workcode":"{{ item.employee.Workcode|trim }}",
"StartOTDay":"{{ item.StartOTDay }}" ,
"EndOTDay":"{{ item.EndOTDay }}",
"process":"{{ item|showprocess }}",
"AsMinute":"{{ item.AsMinute|default:0 }}",
"YUANYING":"{{ item.YUANYING|filteryuanyin }}",
"ApplyDate":"{{ item.ApplyDate }}",
"State":"{{ item.get_State_display|get_State_State }}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
