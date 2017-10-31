{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"PIN":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.PIN }}</a>{% else %}{{ item.PIN }}{% endif %}",
"EName":"{{ item.EName|trim }}",
"Workcode":"{{ item.Workcode|trim }}",
"DeptID":"{{ item.Dept.DeptNumber }}",
"DeptName":"{{  item.Dept.DeptLongName  }}",
"Gender":"{{ item.get_Gender_display|default:"" }}" ,
"Privilege":"{{ item.get_Privilege_display|default:"" }}" ,
"Birthday":"{{ item.Birthday|shortDate4 }}",
"National":"{{ item.National|default:"" }}",
"Title":"{{ item.Title|showTitle|default:"" }}",
"Tele":"{{ item.Tele|default:"" }}",
"Mobile":"{{ item.Mobile|default:"" }}",
"Hiredday":"{{ item.Hiredday|shortDate4 }}",
"Card":"{{ item.Card|default:""}}",
"SSN":"{{ item.SSN|default:""}}",
"emptype":"{{ item.get_Employeetype_display|default:""}}",
"photo":"{{ item|thumbnailUrl }}",
"email":"{{ item.email|default:"" }}",
"OpStamp":"{{ item.OpStamp|default:"" }}",
"fingers":"{{ item.fpCount }}",
"faces":"{{ item.faceCount }}",
"OffDuty":"{{item.OffDuty|isYesNo}}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}