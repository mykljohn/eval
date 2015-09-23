from django.contrib import admin
from django.contrib import messages
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives

#from django.db.models.signals import pre_save

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group

from django.db import models
from django.forms import TextInput, Textarea
from .models import Evaluator, Candidate, Question, EvalGrp, ScoreMsg, Evaluation, EvaluationScore, EvaluationComment, Response

from .forms import Candidatefrm, Evaluatorfrm, Evaluationfrm, EvaluationScorefrm

from django.utils.safestring import mark_safe
#from categories.admin import CategoryBaseAdmin

# Globally disable delete selected
admin.site.disable_action('delete_selected')

def confirm_eval(self, request, queryset):
#    if request.user.username.upper() == 'ADMIN':
#        queryset = queryset.objects.exclude(status!=0)

        queryset = queryset.filter(status=0)
        queryset.update(status=1)
confirm_eval.short_description = "Change Status of checked evaluations to CONFIRMED"

class EvaluatorInline(admin.TabularInline):
    model = Evaluator
    form = Evaluatorfrm
    can_delete = False
    verbose_name_plural = 'Additional Info'
    class Media:
      css = { "all" : ("/static/css/hide_admin_original.css",) }


# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (EvaluatorInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class EvaluationInline(admin.TabularInline):
    model = Evaluation
    fields = ('evaluationdate', 'user', 'status', 'bankno', 'levelrequired', 'levelobtained', 'passfail', 'hiremanager', 'business', 'position', 'band', 'source', 'costcenter')
    exclude = ('createdby', 'datecreated', )
    ordering = ['evaluationdate']
    form = Evaluationfrm

    # Disable the delete button
    def has_delete_permission(self, request, obj=None):
      return False

    extra = 0
    class Media:
        css = { "all" : ("css/hide_admin_original.css",) }


class CandidateAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Candidate',       {'fields': ('name','sso', 'email', 'phone1', 'phone2', 'gender', 'skypeid' )}),
#        ('Candidate',       {'fields': ('name','sso', 'email', 'phone1', 'phone2', 'skypeid' )}),
#        ('Activity Log',    {'fields': ('createdby','datecreated'),'classes': ('collapse')}),
    ]
    class Media:
       css = { "all" : ("/static/css/hide_admin_original.css",) }
#       js = ('/static/admin/js/timepopup.js',)


    inlines = [EvaluationInline]
    ordering = ['name']
#    list_display = ('name', 'sso', 'email', 'phone1', 'phone2', 'gender', 'skypeid')
    list_display = ('name', 'sso', 'email', 'phone1', 'phone2', 'skypeid')
    search_fields = ['name', 'email']
    form = Candidatefrm

admin.site.register(Candidate, CandidateAdmin)


class EvaluatorAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Contact Info',    {'fields': ('phone', 'skypeid' )}),
        ('Schedule',        {'fields': ('maxevals', 'hours')}),
    ]

    list_display = ('phone', 'skypeid' , 'hours', 'maxevals')
    form = Evaluatorfrm

#admin.site.register(Evaluator, EvaluatorAdmin)



class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Question',               {'fields': ['question']}),
        ('BankNo',               {'fields': ['bankno']}),
        ('Grammar',               {'fields': ['grammar']}),
    ]
    ordering = ['bankno','questionno']
    list_display = ('question', 'bankno', 'grammar')
admin.site.register(Question, QuestionAdmin)


class ScoreMsgInline(admin.TabularInline):
    model = ScoreMsg
    fields = ('evalgrp', 'scoremsg', 'suggestion')
    formfield_overrides = {
        models.TextField: {'widget': Textarea(
                           attrs={'rows': 3,
                                  'cols': 70,
                                  'style': 'height: 3em;'})},
    }

    class Media:
      css = { "all" : ("/static/css/hide_admin_original.css",) }
    list_display = ('evalgrp', 'scoremsg', 'suggestion')
    max_num=0
    extra = 0

class EvalGrpAdmin(admin.ModelAdmin):
    fieldsets = [
        ('EvalGrp',               {'fields': ['evalgrp']}),
#        ('Activity Log',    {'fields': ('createdby','datecreated')}),
    ]

    readonly_fields = ['createdby','datecreated', 'evalgrp',]
    inlines = [ScoreMsgInline]
    fieldsets_and_inlines_order = ('f', 'i', 'f')

    class Media:
      css = { "all" : ("/static/css/hide_admin_original.css",) }

    ordering = ['id']
    list_display = ('evalgrp', 'createdby', 'datecreated')

admin.site.register(EvalGrp, EvalGrpAdmin)


class ScoreMsgAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Grammar Category',{'fields': ['evalgrp']}),
        ('Message',         {'fields': ['scoremsg']}),
        ('Suggestion',      {'fields': ['suggestion']}),
        ('Activity Log',    {'fields': ['createdby','datecreated']}),
    ]
    # Disable the add button
    def has_add_permission(self, request):
      return False

    # Disable the delete button
    def has_delete_permission(self, request, obj=None):
      return False

    readonly_fields = ['createdby','datecreated', ]
    ordering = ['id']
    list_display = ('scoremsg', 'evalgrp',)
    list_filter = (
        ('evalgrp', admin.RelatedOnlyFieldListFilter),
    )
admin.site.register(ScoreMsg, ScoreMsgAdmin)


class EvalResponseInline(admin.TabularInline):
    model = Response
    fieldsets = [
        ('Question',               {'fields': ['question']}),
        ('Response',               {'fields': ['response']}),
        ('Notes',               {'fields': ['notes']}),
    ]
    formfield_overrides = {
        models.TextField: {'widget': Textarea( attrs={'rows':'6', 'cols': '300'})},
    }
    # Disable the add button
    def has_add_permission(self, request):
        return False

#    # Disable the change button
#    def has_change_permission(self, request, obj=None):
#      return False

    # Disable the delete button
    def has_delete_permission(self, request, obj=None):
        return False
    readonly_fields = ['question',]
    list_display = ['question', 'response']
    extra = 0


class EvalCommentInline(admin.TabularInline):
    model = EvaluationComment
    extra = 0


class EvalScoreInline(admin.TabularInline):
    model = EvaluationScore
    fields = ('scoremsg',)
    formfield_overrides = {
        models.TextField: {'widget': Textarea(
                           attrs={'rows': 3,
                                  'cols': 70,
                                  'style': 'height: 3em;'})},
    }

    # Disable the delete button
    def has_delete_permission(self, request, obj=None):
        return False
    form = EvaluationScorefrm
    max_num=1
    extra = 1


class EvaluationAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Scheduling Info',    {'fields': [('candidate', ), ('evaluationdate', 'user', 'status', 'bankno')]}),
        ('HR Info', {'fields': [('requestedby', 'levelrequired', 'levelobtained', 'passfail')]}),
    ]
    actions = [confirm_eval]
    inlines = [EvalResponseInline, EvalScoreInline, EvalCommentInline]

    class Media:
       css = { "all" : ("/static/css/hide_admin_original.css",) }
#       js = ('/static/admin/js/timepopup.js',)

    ordering = ['evaluationdate']
#    list_display = ('candidate', 'evaluationdate', 'requestedby' , 'leveltested', 'onlineexam', 'user', 'levelevaluated')
    list_display = ('candidate', 'evaluationdate', 'user', 'status')
    list_filter = ('status',)
    readonly_fields = ('candidate', 'evaluationdate', 'user', )
    form = Evaluationfrm


class EvaluatorEvaluation(Evaluation):
    class Meta:
        proxy = True

class EvaluatorEvaluationAdmin(EvaluationAdmin):

    def get_queryset(self, request):
        qs = super(EvaluatorEvaluationAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            # It is mine, all mine. Just return everything.
            return qs
        return qs.filter(user=request.user.id)

admin.site.register(EvaluatorEvaluation, EvaluatorEvaluationAdmin)

admin.site.register(Evaluation, EvaluationAdmin)


class ScoreMsgInline(admin.TabularInline):
    model = ScoreMsg
    extra = 0
