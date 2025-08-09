from django.contrib import admin
from .models import Student
from .models import Staff
from .models import Blog
from .models import Feed
from .models import Out_Feed
from .models import Student_feed
from .models import admin_log
from .models import Vote
from .models import VotingSession
from .models import TopCandidate
from .models import VoterRecord


class VotingSessionAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'is_active')

class VoterRecordAdmin(admin.ModelAdmin):
    list_display = ('voter_hash',)

class StudentAdmin(admin.ModelAdmin):
    list_display = ('id','type', 'name', 'img', 'email', 'ad_no','mob','department','sex','password','status')

class StaffAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'id_no','mob','department','designation','password','status')

class Out_FeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'feedback')

class FeedAdmin(admin.ModelAdmin):
    list_display = ('id','feedback')

class Student_feedAdmin(admin.ModelAdmin):
    list_display = ('id','feedback')

class admin_logAdmin(admin.ModelAdmin):
    list_display = ('email','password')

class BlogAdmin(admin.ModelAdmin):
    list_display = ('id','title','img','date','contend')

class VoteAdmin(admin.ModelAdmin):
    list_display = ('timestamp','voter','candidate')

class TopCandidateAdmin(admin.ModelAdmin):
    list_display = ('candidate','department','vote_count','rank_in_dept')


admin.site.register(VoterRecord, VoterRecordAdmin)
admin.site.register(VotingSession,VotingSessionAdmin)
admin.site.register(admin_log,admin_logAdmin)
admin.site.register(Student,StudentAdmin)
admin.site.register(Staff,StaffAdmin)
admin.site.register(Feed,FeedAdmin)
admin.site.register(Blog,BlogAdmin)
admin.site.register(Out_Feed,Out_FeedAdmin)
admin.site.register(Student_feed,Student_feedAdmin)
admin.site.register(Vote,VoteAdmin)
admin.site.register(TopCandidate,TopCandidateAdmin)

