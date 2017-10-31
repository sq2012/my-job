{% autoescape off %}
{% load iclock_tags %}
{% load i18n %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"DeptID":"{{ item.employee.Dept.DeptNumber }}",
"DeptName":"{{ item.employee.Dept.DeptName }}",
"PIN":"{{ item.employee.PIN }}",
"Card":"{{ item.employee.Card }}",
"EName":"{{ item.employee.EName|trim }}",
"Workcode":"{{ item.employee.Workcode|default:"" }}",
"TTime":"{{ item.TTime|stdTime }}",
"State":"{{ item.State|getRecordState }}",
"Verify":"{{ item.getComVerifys|default:"" }}",
"Device":"{{ item.Device.SN }}({{item.Device.Alias|default:""}})",
"valid":"{{ item|IsValidLog:'att' }}",

"photo":"{{ item.UserID|thumbnailUrl }}",
"thumbnailUrl":"{{ item|trans_thumbnailUrl:user|safe }}"

}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
