{% autoescape off %}
{% load i18n %}

[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"PIN":"{{ item.PIN }}",
"EName":"{{ item.EName|trim }}",
"DeptID":"{{ item.Dept.DeptID }}",
"Title":"{{ item.Title|default:"" }}",
"DeptName":"{{  item.Dept.DeptName  }}",
"Shift":"{{ item.id|getEmpShift:0 }}" ,
"shift_detail":"<a href='#' onclick='showWorkTime({{item.id}});'><img title='{%trans '显示班次详情' %}'  src='../media/img/Calendar.png' /></a>",
"tmpShift":"{{ item.id|getEmpShift:1 }}" 

}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}