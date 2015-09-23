from django import forms
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.forms import ModelMultipleChoiceField
from itertools import groupby
from operator import attrgetter


from .models import Evaluator, Candidate, Question, EvalGrp, ScoreMsg, Evaluation, EvaluationHR, EvaluationScore, EvaluationComment, Response


class Evaluatorfrm(forms.ModelForm):

#    hours = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(choices=), )

#    hours = forms.MultiSelectFormField(choices=Evaluation.xSTATUS, required=True)
#    hours = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=Evaluator.xHOURS, initial="1")
#    hours = forms.CharField(required=False, max_length=30, widget=forms.CheckboxSelectMultiple(choices=Evaluator.xHOURS),)
#    hours= forms.MultipleChoiceField(widget=forms.SelectMultiple, choices=Evaluator.xHOURS, initial="1")
#    print hours
#    def clean_hours(self):
#      field = ""
#      for data in self.cleaned_data['hours']:
#        field += data+","
#        print field
#      return field.rstrip(",")

    class Meta:
        model = Evaluator
        fields = ('phone', 'skypeid', 'maxevals', 'hours')

class Candidatefrm(forms.ModelForm):

    gender = forms.CharField(widget=forms.RadioSelect(
                 choices=Candidate.xGENDER),)

    class Meta:
        model = Candidate
        fields = ('name', 'sso', 'email', 'phone1', 'phone2', 'gender', 'skypeid', 'createdby', 'datecreated', )


class Evaluationfrm(forms.ModelForm):

    status = forms.IntegerField(widget=forms.RadioSelect(choices=Evaluation.xSTATUS),)
    bankno = forms.IntegerField(widget=forms.RadioSelect(choices=Evaluation.xBANK),)
    levelrequired = forms.CharField(widget=forms.RadioSelect(choices=Evaluation.xLEVEL), required=False, label="Level Required")
    levelobtained = forms.CharField(widget=forms.RadioSelect(choices=Evaluation.xLEVEL), required=False, label="Level Obtained")
    passfail = forms.CharField(widget=forms.RadioSelect(choices=Evaluation.xPASSFAIL), required=False, label="Pass / Fail")
    source = forms.CharField(widget=forms.RadioSelect(choices=Evaluation.xSOURCE), required=False, )
    user = forms.ModelChoiceField(queryset=Evaluator.objects.filter(maxevals__gt=0), required=False, empty_label="Unassigned")

    class Meta:
        model = Evaluation
        fields = ('evaluationdate', 'user', 'status', 'bankno', 'requestedby', 'levelrequired', 'levelobtained', 'passfail', 'source',)


class ScoreMsgChoiceField(ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        super(ScoreMsgChoiceField, self).__init__(*args, **kwargs)
        groups = groupby(kwargs['queryset'], attrgetter('evalgrp'))
        self.choices = [(evalgrp, [(c.id, self.label_from_instance(c)) for c in scoremsgs])
                        for evalgrp, scoremsgs in groups]


class EvaluationScorefrm(forms.ModelForm):
    scoremsg = ScoreMsgChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'size':'300'}), queryset=ScoreMsg.objects.all(), required=False)
    def __init__(self, *args, **kwargs):
        current_scoremsg = kwargs.pop('scoremsg', None)
        initial = kwargs.get('initial', {})
        if current_scoremsg:
            initial.update({'scoremsgs': current_scoremsg.scoremsgs.all()})
        kwargs['initial'] = initial
        super(EvaluationScorefrm, self).__init__(*args, **kwargs)
    class Meta:
        fields = '__all__'
        model = EvaluationScore



