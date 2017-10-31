{% autoescape off %}
{% load iclock_tags %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"workcode":"{% if can_change and item.state == 0 %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.userID|getemppin }}</a>{% else %}{{ item.userID|getemppin }}{% endif %}",
"PIN":"{{ item.userID|getempworkcode|trim }}",
"EName":"{{ item.userID|getempname|trim }}",
"fromDeptID":"{{ item.fromDept|getempdeptid|default:'' }}",
"fromDeptName":"{{ item.fromDept|getempdeptname|default:'' }}",
"toDeptID":"{{  item.toDept|getempdeptid|default:'' }}",
"toDeptName":"{{  item.toDept|getempdeptname|default:'' }}",
"fromTitle":"{{ item.fromTitle|default:"" }}" ,
"toTitle":"{{ item.toTitle|default:"" }}",
"fromDate":"{{ item.fromDate|default:"" }}",
"toDate":"{{ item.toDate|default:"" }}" ,
"reason":"{{ item.reason|default:"" }}",
"operate":"{{ item.operate|default:"" }}",
"remark":"{{ item.remark|default:"" }}",
"OpTime":"{{ item.OpTime|default:""}}",
"state":"{{ item.state|empborrowState}}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}