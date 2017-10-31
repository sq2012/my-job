{% autoescape off %}
{% load iclock_tags %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"PIN":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.PIN }}</a>{% else %}{{ item.PIN }}{% endif %}",
"Workcode":"{{ item.Workcode|trim }}",
"EName":"{{ item.EName|trim }}",
"DeptID":"{{ item.Dept.DeptNumber }}",
"DeptName":"{{  item.Dept.DeptLongName  }}",
"BorrowTag":"{{  item.BorrowDept|default:''  }}",
"BorrowDept":"{{  item.BorrowDept|default:''  }}",
"Gender":"{{ item.get_Gender_display|default:"" }}" ,
"Birthday":"{{ item.Birthday|shortDate4 }}",
"National":"{{ item.National|default:"" }}",
"Privilege":"{{ item.get_Privilege_display|default:"" }}" ,
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
"OffDuty":"{{item.OffDuty|isYesNo}}",
"OffPosition":"{{item.OffPosition|isYesNo}}",
"bstate":"{{item.bstate|empborrowState}}",
"OffPositionDate":"{{ item.OffPositionDate |default:'' }}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}