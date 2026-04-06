from django import template

register = template.Library()

@register.filter
def get_answer(answers, question_id):
    for a in answers:
        if a.question.id == question_id:
            return a
    return None