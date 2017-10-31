{% autoescape off %}
{% load iclock_tags %}

[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"username":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.username }}</a>{% else %}{{ item.username }}{% endif %}",
"email":"{{ item.email }}",
"last_name":"{{ item.last_name }}",
"first_name":"{{ item.first_name }}",
"last_login":"{{ item.last_login }}",
"emp_pin":"{{ item.emp_pin|default:'' }}",
"Tele":"{{ item.Tele|default:'' }}",
"logincount":"{{ item.logincount|default:0 }}",
"date_joined":"{{ item.date_joined }}",
"is_staff":"<img alt='True' src='media/img/icon-{% if item.is_staff %}yes{% else %}no{% endif %}.gif'/>" ,
"is_superuser":"<img alt='True' src='media/img/icon-{% if item.is_superuser %}yes{% else %}no{% endif %}.gif'/>",
"deptadmin_set":"<a title='授权部门明细' onclick='getdpts_user(\"{{ item.id }}\",\"{{ item.username }}\")' style='color:green;'>{{ item|dept_related }}</a>",
"iclock_set":"{% if item.is_superuser %} {% else %}<a title='授权设备' onclick='getdevicebyuser(\"{{ item.id }}\",\"{{ item.username }}\")' style='color:green;'>查看</a>{% endif %}",
"groups":"{% if item.is_superuser %} {% else %}{{ item.groups.values|PackList:'name' }}{% endif %}",
"Creator":"{{ item|getUserCreator}}",
"TimeDept":"{{ item|getTimeDept}}",
"Userroles":"{{ item.userrole_set.select_related|role_related }}"
}{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
