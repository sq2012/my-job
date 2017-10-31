{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"visDate":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.visDate|default:"" }}</a>{% else %}{{ item.visDate|default:"" }}{% endif %}",
"visempName":"{{ item.visempName|default:""}}",
"SSN":"{{item.SSN|default:""}}",
"visCompany":"{{ item.visCompany|default:""}}",
"VisitingNum":"{{ item.VisitingNum|default:""}}",
"InterviewedempName":"{{ item.InterviewedempName|default:""}}",
"VisitedCompany":"{{ item.VisitedCompany|default:""}}",
"visReason":"{{ item.visReason|default:""}}",
"remark":"{{ item.remark|default:""}}"
}{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
