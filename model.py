from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.template.defaultfilters import date
from django.utils.encoding import smart_unicode
from django.utils import timezone
from separatedvaluesfield.models import SeparatedValuesField
#from categories.models import CategoryBase

from django.core import mail
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.template import Context

VERBOSE_NAME = ('English Evaluation Tool')

class Evaluator(models.Model):
    xHOURS = (
    (9, "9 am"),
    (10, "10 am"),
    (11, "11 am"),
    (12, "12 pm"),
    (13, "1 pm"),
    (14, "2 pm"),
    (15, "3 pm"),
    (16, "4 pm"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Evaluator",)
#    user = models.OneToOneField(User, blank=True, null=True, verbose_name="Evaluator",)
    phone = models.CharField(db_column='Phone', max_length=20, blank=True, null=True)  # Field name made lowercase.
    skypeid = models.CharField(db_column='SkypeID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    maxevals = models.IntegerField(db_column='MaxEvals', blank=True, null=True, verbose_name="Maximum Evaluations",)
    hours = SeparatedValuesField(max_length=150, cast=int, token=',', choices=xHOURS, blank=True, null=True)
    def __unicode__(self):
        return '%s' % (self.user)

def create_evaluator(sender, instance, created, **kwargs):
    if created:
       profile, created = Evaluator.objects.get_or_create(user=instance)

post_save.connect(create_evaluator, sender=User)


class Question(models.Model):
    bankno = models.IntegerField(db_column='BankNo',null=False)
    questionno = models.IntegerField(db_column='QuestionNo',null=False)
    question = models.TextField(db_column='Question', blank=True, null=True)  # Field name made lowercase.
    grammar = models.CharField(db_column='Grammar', max_length=30, blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=20, blank=False, null=False, default=User)  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='DateCreated', default=timezone.now)  # Field name made lowercase.
    ordering = ['questionno']
    def __str__(self):
        return (self.question)


class Candidate(models.Model):
    xGENDER = (
        ("M","Male"),
        ("F","Female"),
    )

    name = models.CharField(db_column='Candidate Name', max_length=60, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    sso = models.CharField(db_column='SSO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=60, blank=True, null=True)  # Field name made lowercase.
    phone1 = models.CharField(db_column='Phone1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    phone2 = models.CharField(db_column='Phone2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    gender = models.CharField(db_column='Gender', max_length=1, choices=xGENDER, blank=True, null=True)  # Field name made lowercase.
    skypeid = models.CharField(db_column='SkypeID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=20, blank=False, null=False, default=User)  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='DateCreated', default=timezone.now)  # Field name made lowercase.
    ordering = ['name']
    class Meta:
        verbose_name_plural = 'Candidates'
        verbose_name = 'Candidate'

    def __unicode__(self):
        return smart_unicode(self.name)


class Evaluation(models.Model):
    xLEVEL = (
       ("BASIC", "BASIC"),
       ("BEGINNERS", "BEGINNERS"),
       ("INTERMEDIATES", "INTERMEDIATES"),
       ("ADVANCED", "ADVANCED"),
    )

    xPASSFAIL = (
       ("P", "Pass"),
       ("F", "Fail"),
    )

    xSTATUS = (
       (0, "PENDING"),
       (1, "CONFIRMED"),
       (2, "DONE"),
       (3, "RESCHEDULE"),
    )

    xBANK = (
       (1, "First"),
       (2, "Repeat"),
       (3, "Alternate"),
    )

    xSOURCE = (
       ("I", "Internal"),
       ("E", "External"),
    )

    candidate = models.ForeignKey(Candidate)
    evaluationdate = models.DateTimeField(db_column='EvaluationDate', blank=True, null=True)
    user = models.ForeignKey(Evaluator, verbose_name="Evaluator",)
    bankno = models.IntegerField(db_column='BankNo', choices=xBANK, blank=False, null=False, default=1, verbose_name="Question Set")
    status = models.IntegerField(db_column='Status', choices=xSTATUS, blank=True, null=True)
    levelrequired = models.CharField(db_column='LevelRequired', choices=xLEVEL, max_length=15, blank=True, null=True, verbose_name="Level Required")
    levelobtained = models.CharField(db_column='LevelObtained', choices=xLEVEL, max_length=15, blank=True, null=True, verbose_name="Level Obtained")
    requestedby = models.CharField(db_column='RequestedBy', max_length=20, blank=False, null=False, default='HR', verbose_name="Requested by")
    passfail = models.CharField(db_column='PassFail', choices=xPASSFAIL, max_length=5, blank=True, null=True, verbose_name="Pass / Fail")
    source = models.CharField(db_column='Source', max_length=10, blank=True, null=True)
    createdby = models.CharField(db_column='CreatedBy', max_length=10, blank=False, null=False, default=User)
    datecreated = models.DateTimeField(db_column='DateCreated', default=timezone.now)


# The arguments this function receives are defined by the `pre_save` signal.
def send_task_email(sender, instance, **kwargs):
    # The logic to send the email goes here. e.g.

    plaintext = get_template('eval_confirm.txt')
    htmly     = get_template('eval_confirm.html')

    d = Context({ 'candidate': instance.candidate.name, 'evaluationdate': instance.evaluationdate, 'phone': instance.candidate.phone1 })

    subject, from_email, to = 'Evaluation', "myklmex@gmail.com", 'mykljohn@hotmail.com'
    text_content = plaintext.render(d)
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

pre_save.connect(send_task_email, sender=Evaluation, dispatch_uid="sending_email_uid")


#def create_eval(sender, instance, created, **kwargs):
#    if created:
#       profile, created = Evaluation.objects.get_or_create(user=instance)

#post_save.connect(create_eval, sender=Evaluation)


class Response(models.Model):
    evaluation = models.ForeignKey(Evaluation)
    bankno = models.IntegerField(db_column='BankNo', blank=False, null=False, default=1, verbose_name="Set")
    question = models.ForeignKey(Question)
    response = models.TextField(db_column='Response', blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(db_column='Notes', blank=True, null=True)  # Field name made lowercase.


class EvalGrp(models.Model):
    evalgrp = models.CharField(db_column='EvalGrp', max_length=60)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=20, blank=False, null=False, default=User)  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='DateCreated', default=timezone.now)  # Field name made lowercase.
    ordering = ['id']
    class Meta:
        verbose_name_plural = 'Evaluation Groups'
        verbose_name = 'Evaluation Group'

    def __str__(self):
        return (self.evalgrp)


class ScoreMsg(models.Model):
    scoremsg = models.TextField(db_column='ScoreMsg', blank=True, null=True)  # Field name made lowercase.
    evalgrp = models.ForeignKey(EvalGrp)
    evalgrptxt = models.CharField(db_column='EvalGrp', max_length=50, blank=False, null=False, default='test')
    suggestion = models.TextField(db_column='suggestion', blank=True, null=True)
    createdby = models.CharField(db_column='CreatedBy', max_length=20, blank=False, null=False, default=User)
    datecreated = models.DateTimeField(db_column='DateCreated', default=timezone.now)
    ordering = ['id']
    class Meta:
        verbose_name_plural = 'Score Messages'
        verbose_name = 'Score Message'
    def __unicode__(self):
        return u"%s" % (self.scoremsg)


class EvaluationScore(models.Model):
#    evaluation = models.ForeignKey(Evaluation)
#    scoremsg = models.ForeignKey(ScoreMsg, blank=True, null=True)
#    SCOREMSGS = ScoreMsg.objects.all().values_list('id','scoremsg', flat=True).order_by('id')
#    SCOREMSGS = ScoreMsg.objects.all().values()
    evaluation = models.OneToOneField(Evaluation, on_delete=models.CASCADE, verbose_name="Evaluation",)
#    scoremsg = SeparatedValuesField(db_column='ScoreMessage', choices=SCOREMSGS, max_length=300, token='|', blank=True, null=True)
    scoremsg = SeparatedValuesField(db_column='ScoreMessage', max_length=300, token='|', blank=True, null=True)
    def __unicode__(self):
        return u"%s" % (self.scoremsg)


class EvaluationComment(models.Model):
    evaluation = models.ForeignKey(Evaluation)
    comments = models.TextField(db_column='Comments', blank=True, null=True)  # Field name made lowercase.


#class Category(CategoryBase):
#    categories = models.CharField(max_length=60)
#    """
#    A simple of catgorizing example
#    """

#    class Meta:
#        verbose_name_plural = 'categories'
