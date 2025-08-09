from django.db import models
from django.utils import timezone

class VoterRecord(models.Model):
    voter_hash = models.CharField(max_length=64, unique=True)

    def _str_(self):
        return f'Voter {self.voter_hash[:10]}...'
    
    
class TopCandidate(models.Model):
    candidate = models.ForeignKey('voteA.Student', on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    vote_count = models.IntegerField()
    rank_in_dept = models.IntegerField()

    class Meta:
        unique_together = ('candidate', 'department')

    def _str_(self):
        return f"{self.candidate.name} - {self.department} (Rank: {self.rank_in_dept}, Votes: {self.vote_count})"


class VotingSession(models.Model):
    start_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    def has_expired(self):
        if not self.start_time:
            return False
        return timezone.now() > self.start_time + timezone.timedelta(minutes=10)

    def time_remaining(self): 
        if not self.start_time:
            return 0
        delta = (self.start_time + timezone.timedelta(minutes=1)) - timezone.now()
        return max(0, int(delta.total_seconds()))
    

    
class Student(models.Model):
    name = models.CharField(max_length=100,null=True)
    ad_no = models.IntegerField(null=True)
    mob = models.IntegerField(null=True)
    email = models.EmailField(max_length=100,null=True)
    department = models.CharField(max_length=10,null=True)
    sex = models.CharField(max_length=10,null=True)
    password = models.CharField(max_length=10,null=True)
    status = models.CharField(max_length=10,null=True)
    type = models.CharField(max_length=10,null=True)
    img = models.ImageField(upload_to='student_images/',null=True, blank=True)

class Vote(models.Model):
    voter = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='votes_cast')
    candidate = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='votes_received')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('voter',)  # Ensures one vote per student

    def __str__(self):
        return f"{self.voter.name} voted for {self.candidate.name}"

class Staff(models.Model):
    name = models.CharField(max_length=100,null=True)
    id_no = models.IntegerField(null=True)
    mob = models.IntegerField(null=True)
    email = models.EmailField(max_length=100,null=True)
    department = models.CharField(max_length=10,null=True)
    designation = models.CharField(max_length=10,null=True)
    password = models.CharField(max_length=10,null=True)
    status = models.CharField(max_length=10,null=True)
    
class admin_log(models.Model):
    email = models.EmailField(max_length=100,null=True)
    password = models.CharField(max_length=10,null=True) 

class Blog(models.Model):
    title = models.CharField(max_length=200,null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    img = models.ImageField(upload_to='blog_img/')
    date = models.DateField(null=True)
    contend = models.TextField(null=True)

class Feed(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.TextField(null=True)

class Student_feed(models.Model):
    feedback = models.TextField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

class Out_Feed(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField()
    feedback = models.TextField()