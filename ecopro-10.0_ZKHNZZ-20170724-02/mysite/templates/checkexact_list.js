{% autoescape off %}
{% load iclock_tags %}

[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"PIN":"{% if can_change %}{% ifequal item.State 0 %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.employee.PIN }}</a>{% else %}{% ifequal item.State 6 %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.employee.PIN }}</a>{% else %}{{ item.employee.PIN }}{% endifequal %}{% endifequal %}{% else %}{{ item.employee.PIN }}{%endif%}",
"Workcode":"{{ item.employee.Workcode|default:'' }}",
"EName":"{{ item.employee.EName|default:'' }}",
"DeptName":"{{ item.employee.Dept.DeptName }}",
"CHECKTIME":"{{ item.CHECKTIME }}",
"CHECKTYPE":"{{ item.CHECKTYPE|getRecordState }}" ,
"process":"{{ item|showprocess }}",
"YUYIN":"{{ item.YUYIN|filteryuanyin }}",
"MODIFYBY":"{{ item.MODIFYBY }}",
"State":"{{ item.get_State_display}}",
"ApplyDate":"{{ item.ApplyDate }}",
"Device":"{{ item.Device|default:"" }}",
"SaveStamp":"{{ item.SaveStamp|default:"" }}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
