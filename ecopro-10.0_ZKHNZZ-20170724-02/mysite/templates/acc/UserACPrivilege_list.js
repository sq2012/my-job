{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.employee.id }}",
"PIN":"{{ item.employee.PIN }}",
"EName":"{{ item.employee.EName }}",
"Name":"{{ item.acgroup.GroupID }}({{ item.acgroup.Name }})",

"IsUseGroup":"{{ item.get_IsUseGroup_display|default:0 }}",
"TimeZone1":"{{ item.TimeZone1|default:''}}",
"TimeZone2":"{{ item.TimeZone2|default:'' }}",
"TimeZone3":"{{ item.TimeZone3|default:'' }}",

"SN":""
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
