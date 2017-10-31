{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"aux_no":"{{ item.aux_no }}",
"aux_name":"<a class='can_edit'  href='#' onclick='javascript:editclick(\"{{item.id}}\",\"/acc/data/AuxIn/\");'>{{ item.aux_name }}</a>",
"device":"{{ item.device.Alias|default:'' }}",
"printer_name":"{{ item.printer_name }}",
"remark":"{{ item.remark|default:'' }}",
"details":""}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
