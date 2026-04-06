from django.contrib import admin
from .models import Exam, Question, Result, UserAnswer

# --- BLOCKS FOR THE EXAM PAGE ---

class QuestionInline(admin.StackedInline): # 'Stacked' makes it look like big cards
    model = Question
    extra = 0
    fieldsets = (
        (None, {'fields': ('question_text',)}),
        ('Options', {'fields': (('option1', 'option2'), ('option3', 'option4'), 'correct_option')}),
    )

class ResultInline(admin.TabularInline): # 'Tabular' is better for scores
    model = Result
    extra = 0
    readonly_fields = ('user', 'score', 'percentage', 'status', 'submitted_at')
    can_delete = False

# --- THE MAIN DASHBOARD VIEW ---

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    # This makes the main Exam list look professional
    list_display = ('title', 'total_marks', 'duration_display')
    
    # This organizes the individual Exam page into "Blocks"
    fieldsets = (
        ('EXAM SETTINGS', {
            'fields': ('title', 'duration', 'total_marks'),
            'description': 'Configure the basic settings for this test.'
        }),
    )
    
    inlines = [QuestionInline, ResultInline]

    def duration_display(self, obj):
        return f"{obj.duration} Minutes"
    duration_display.short_description = 'Duration'

# --- THE RESULT LIST VIEW ---

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'score_progress', 'status_badge', 'submitted_at')
    list_filter = ('exam', 'status')
    search_fields = ('user__username', 'exam__title')

    # Making the status look like a badge
    def status_badge(self, obj):
        from django.utils.html import format_html
        color = 'green' if obj.status == 'Pass' else 'red'
        return format_html('<b style="color: {}; text-transform: uppercase;">{}</b>', color, obj.status)
    status_badge.short_description = 'Result Status'

    def score_progress(self, obj):
        return f"{obj.score} Marks ({obj.percentage}%)"

admin.site.register(UserAnswer)


from django.contrib import admin
from .models import Profile  




# --- PROFILE ADMIN SECTION ---


# 2. Sirf Decorator use karein (Ye zyada professional hai)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # Ye columns Admin Panel ki list mein dikhenge
    list_display = ('user', 'roll_no', 'role', 'address')
    # Admin search bar se in details ko dhoond sakega
    search_fields = ('user__username', 'roll_no', 'address')