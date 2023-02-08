{% for part_of_speech, values in entries.items %}
[{{ part_of_speech }}] {% for value in values %}{{ value }}{% if not forloop.last %}, {% endif %}{% endfor %}
{% endfor %}
