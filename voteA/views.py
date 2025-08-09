from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from.models import *
from datetime import datetime
import logging
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponse
from django.db.models import Count, Window, F
from django.db.models.functions import Rank
import hashlib
from Blockchain import Blockchain


def get_vote_results():
    blockchain = Blockchain()  # this will load from file now
    results = {}

    for block in blockchain.chain:
        for vote in block.get('votes', []):
            candidate = vote['candidate']
            results[candidate] = results.get(candidate, 0) + 1

    return results



def result_view(request):
    # Get the current vote results from the blockchain
    results = get_vote_results()

    if not results:
        return render(request, 'results.html', {'message': "No votes have been cast yet."})

    return render(request, 'results.html', {'results': results})


def campusvote(request):
    blockchain = Blockchain()
    candidates = TopCandidate.objects.all()


    if request.method == 'POST':
        student_id = request.session.get('student_id')
        student = Student.objects.get(id=student_id)
        ad_no = student.ad_no
        voter_id = ad_no
        candidate_id1 = request.POST['candidate']
        voter_hash = hashlib.sha256(str(voter_id).encode()).hexdigest()

        if VoterRecord.objects.filter(voter_hash=voter_hash).exists():
            messages.error(request, 'You have already voted!')
            return redirect('campusvote')

        selected_candidate = Student.objects.get(id=candidate_id1)
        blockchain.new_vote(voter_id, selected_candidate.name)
        last_proof = blockchain.last_block['proof']
        proof = blockchain.proof_of_work(last_proof)
        blockchain.new_block(proof)

        VoterRecord.objects.create(voter_hash=voter_hash)
        messages.success(request, 'Vote submitted successfully.')
        return redirect('campusvote')

    return render(request, 'vote.html', {'candidates': candidates})


def update_top_candidates(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # Clear old results
    TopCandidate.objects.all().delete()

    # Get top 2 candidates per department
    top_candidates = Student.objects.annotate(
        vote_count=Count('votes_received'),
        rank_in_dept=Window(
            expression=Rank(),
            partition_by=[F('department')],
            order_by=F('vote_count').desc()
        )
    ).filter(rank_in_dept__lte=2)

    # Store them in TopCandidate table
    for student in top_candidates:
        TopCandidate.objects.create(
            candidate=student,
            department=student.department,
            vote_count=student.vote_count,
            rank_in_dept=student.rank_in_dept
        )

    return render(request, 'admin_home.html')


def top_candidates_view(request):
    top_candidates = Student.objects.annotate(
    vote_count=Count('votes_received'),
    rank_in_dept=Window(
        expression=Rank(),
        partition_by=[F('department')],
        order_by=F('vote_count').desc()
    )
    ).filter(rank_in_dept__lte=2)

    return render(request, 'top_candidates.html', {'top_candidates': top_candidates})


def newvote(request):
    Student.objects.filter(type='CANDIDATE').update(type='STUDENT')
    Vote.objects.all().delete()
    VoterRecord.objects.all().delete()
    TopCandidate.objects.all().delete()
    import json

    # Load the blockchain data from the file
    with open('blockchain.json', 'r') as f:
        blockchain = json.load(f)

    # Remove the votes from each block
    for block in blockchain:
        block['votes'] = []

    # Save the updated blockchain data to the file
    with open('blockchain.json', 'w') as f:
        json.dump(blockchain, f, indent=4)
        
    return redirect('admin_home')


def start_vote(request):
    VotingSession.objects.all().delete()
    session = VotingSession.objects.create(start_time=timezone.now(), is_active=True)
    messages.success(request, "Vote has been started successfully!")
    return redirect('admin_home')


def index(request):
    if request.method == 'POST':
        name = request.POST.get("tname")
        email = request.POST.get("temail")
        feedback = request.POST.get("tfeed")
        
        if name and email and feedback:
            Out_Feed.objects.create(
                name=name,
                email=email,
                feedback=feedback,
            )
            messages.success(request, 'Your feedback has been sent successfully!')
            return redirect('index')
        else:
            messages.error(request, 'Please fill in all fields.')
    return render(request, 'index.html')


def right(request):
    return render(request, 'right.html')


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            student = Student.objects.get(email=email, status='ACCEPTED')
            request.session['student_id'] = student.id
            if student.password == password:
                if student.type == 'CANDIDATE':
                    try:
                        top_candidate = TopCandidate.objects.get(candidate=student)
                        if top_candidate.rank_in_dept == 1 or top_candidate.rank_in_dept == 2 :
                            return redirect('classrep')
                        else:
                            return redirect('candidate_home')
                    except TopCandidate.DoesNotExist:
                        return redirect('candidate_home')
                else:
                    return redirect('student_home')
        except Student.DoesNotExist:
            pass
        
        try:
            staff_data = Staff.objects.get(email=email, status='ACCEPTED')
            request.session['staff_id'] = staff_data.id
            if staff_data.password == password:
                if staff_data.designation == 'HOD':
                    return redirect('staff_home')
                else:
                    return redirect('staff2_home')
        except Staff.DoesNotExist:
            pass

        try:
            admin_data = admin_log.objects.get(email=email)
            if admin_data.password == password:
                return redirect('admin_home')
        except admin_log.DoesNotExist:
            pass

    return render(request, 'login.html')


def classrep(request):
    student_id = request.session.get('student_id')
    if not student_id:
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('login')  # Or any login page or error page

    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        feedback = request.POST.get('thm', '').strip()
        student_id = request.session.get('student_id')

        if not student_id:
            messages.error(request, 'Student ID is not set in the session.')
            return redirect('classrep')

        student = get_object_or_404(Student, id=student_id)

        if feedback:
            Student_feed.objects.create(
                feedback=feedback,
                student=student,
            )
            messages.success(request, 'Your feedback has been sent successfully!')
            return redirect('classrep')
        else:
            messages.error(request, 'Please fill in all fields.')
            
    blogs = Blog.objects.all()
    return render(request, 'classrep.html', {'blogs': blogs})


def election2(request):
    candidates = TopCandidate.objects.all()
    context = {
        'candidates': candidates
    }
    return render(request, 'election2.html',context)


def election(request):
    student_id = request.session.get('student_id')
    std = Student.objects.get(id=student_id)
    candidates = Student.objects.filter(department=std.department, type='CANDIDATE')

    session = VotingSession.objects.last()
    voting_active = session and session.is_active and not session.has_expired()
    time_remaining = session.time_remaining() if voting_active else 0

    return render(request, 'election.html', {
        'candidates': candidates,
        'voting_active': voting_active,
        'time_remaining': time_remaining
    })


def vote(request, candidate_id):
    student_id = request.session.get('student_id')
    
    if not student_id:
        messages.error(request, "You must be logged in to vote.")
        return redirect('login')

    voter = get_object_or_404(Student, id=student_id)
    candidate = get_object_or_404(Student, id=candidate_id, type='CANDIDATE')

    if Vote.objects.filter(voter=voter).exists():
        messages.error(request, "You have already voted.")
        return redirect('election')

    Vote.objects.create(voter=voter, candidate=candidate)
    messages.success(request, f"You have successfully voted for {candidate.name}.")
    return redirect('election')


def blog(request):
    blog_data = Blog.objects.all()
    
    if request.method == 'POST':
        student_id = request.session.get('student_id')
        
        if student_id:
            try:
                student = Student.objects.get(id=student_id)
            except Student.DoesNotExist:

                return redirect('error_page')
            
            img = request.FILES.get('imgu')
            Blog.objects.create(
                title=request.POST.get("tit"),
                student=student,
                img=img,
                contend=request.POST.get("con"),
                date=datetime.now(),
            )
            return redirect('candidate_home')
        else:
            return redirect('login_page') 
    else:
        return render(request, 'blog.html', {'blog_data': blog_data})


def view_blog(request):
    blogs = Blog.objects.all()
    return render(request, 'student_home.html', {'blogs': blogs})


def result(request):
    return render(request,'result.html')


def result(request):
    candidatesBCA = Student.objects.filter(type='CANDIDATE', department='BCA').annotate(vote_count=Count('votes_received')).order_by('-vote_count')
    candidatesBCOM = Student.objects.filter(type='CANDIDATE', department='BCOM').annotate(vote_count=Count('votes_received')).order_by('-vote_count')
    candidatesBBA = Student.objects.filter(type='CANDIDATE', department='BBA').annotate(vote_count=Count('votes_received')).order_by('-vote_count')
    candidatesMSW = Student.objects.filter(type='CANDIDATE', department='MSW').annotate(vote_count=Count('votes_received')).order_by('-vote_count')
    candidatesMBA = Student.objects.filter(type='CANDIDATE', department='MBA').annotate(vote_count=Count('votes_received')).order_by('-vote_count')
    candidatesMCA = Student.objects.filter(type='CANDIDATE', department='MCA').annotate(vote_count=Count('votes_received')).order_by('-vote_count')
    return render(request, 'result.html', {'candidatesBCA': candidatesBCA, 'candidatesBCOM': candidatesBCOM, 'candidatesBBA': candidatesBBA, 'candidatesMSW': candidatesMSW, 'candidatesMBA': candidatesMBA, 'candidatesMCA': candidatesMCA})


def result1(request):
    student_id = request.session.get('student_id')
    staff_id = request.session.get('staff_id')
    std = Student.objects.get(id=student_id)
    std_staff = Staff.objects.get(id=staff_id)
    staff_dep =Staff.objects.filter(department=std_staff.department)
    dep = Student.objects.filter(department=std.department)
    result = Student.objects.filter(type='CANDIDATE', department=std.department or std_staff.department).annotate(vote_count=Count('votes_received')).order_by('-vote_count')
    return render(request, 'result1.html', {'result': result})
    

def admin_home(request):
    feed_out = Out_Feed.objects.all()
    feed_staff = Feed.objects.select_related('staff').all()
    feed_student =Student_feed.objects.select_related('student').all()
    return render(request, 'admin_home.html', {'feed_out': feed_out, 'feed_staff': feed_staff, 'feed_student': feed_student})


def staff_register(request):
    staff_Data = Staff.objects.all()
    if request.method == 'POST':
        Staff.objects.create(
            name=request.POST.get("txtname"),
            id_no=request.POST.get("txtidno"),
            mob=request.POST.get("txtmobno"),
            email=request.POST.get("txtemail"),
            department=request.POST.get("txtdepartment"),
            designation=request.POST.get("txtdesignation"),
            password=request.POST.get("txtpassword"),
        )
        return redirect('index')
    else:
        return render(request, 'staff_register.html')
    

def staff_home(request):
    if request.method == 'POST':
        feedback = request.POST.get('tmessage')
        staff = request.session.get('staff_id')


        try:
            staff = Staff.objects.get(id=staff)
        except Staff.DoesNotExist:
            messages.error(request, 'Invalid staff ID. Please try again.')
            return redirect('staff_home')
        
        if feedback:
            Feed.objects.create(
                feedback=feedback,
                staff=staff,
            )
            messages.success(request, 'Your feedback has been sent successfully!')
            return redirect('staff_home')
        else:
            messages.error(request, 'Please fill in all fields.')
    blogs = Blog.objects.all()    
    return render(request, 'staff_home.html', {'blogs': blogs})


def staff2_home(request):
    if request.method == 'POST':
        feedback = request.POST.get('tmessage')
        staff = request.session.get('staff_id')

        try:
            staff = Staff.objects.get(id=staff)
        except Staff.DoesNotExist:
            messages.error(request, 'Invalid staff ID. Please try again.')
            return redirect('staff2_home')
        
        if feedback:
            Feed.objects.create(
                feedback=feedback,
                staff=staff,
            )
            messages.success(request, 'Your feedback has been sent successfully!')
            return redirect('staff2_home')
        else:
            messages.error(request, 'Please fill in all fields.')

    blogs = Blog.objects.all()        
    return render(request, 'staff2_home.html', {'blogs': blogs})


def manage_staff(request):
    staffs = Staff.objects.all()
    return render(request, 'manage_staff.html', {'staffs': staffs})


def accept_staff(request, staff_id):
    staff = Staff.objects.get(id = staff_id)
    staff.status = 'ACCEPTED'
    staff.save()
    return redirect('manage_staff')


def reject_staff(request, staff_id):
    staff = Staff.objects.get(id = staff_id)
    staff.status = 'REJECTED'
    staff.save()
    return redirect('manage_staff')


def student_home(request):
    if request.method == 'POST':
        feedback = request.POST.get('thmess')
        student_id = request.session.get('student_id')

        if not student_id:
            messages.error(request, 'Student ID is not set in the session.')
            return redirect('student_home')

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            messages.error(request, 'Invalid student ID. Please try again.')
            return redirect('student_home')

        if feedback:
            Student_feed.objects.create(
                feedback=feedback,
                student=student,
            )
            messages.success(request, 'Your feedback has been sent successfully!')
            return redirect('student_home')
        else:
            messages.error(request, 'Please fill in all fields.')

    blogs = Blog.objects.all()

    return render(request, 'student_home.html', {'blogs': blogs})


def manage_student(request):
    students = Student.objects.all()
    return render(request, 'manage_student.html', {'students': students})


def manage_studentStaff(request):
    staff_id = request.session.get('staff_id')
    std = Staff.objects.get(id=staff_id)
    dep = Student.objects.filter(department=std.department)
    studentStaff = Student.objects.filter(department=std.department)
    return render(request, 'manage_studentStaff.html', {'studentStaff': studentStaff, 'staff_id': staff_id})


def view_students(request):
    staff_id = request.session.get('staff_id')
    std = Staff.objects.get(id=staff_id)
    dep = Student.objects.filter(department=std.department)
    students = Student.objects.filter(department=std.department)
    return render(request, 'view_students.html', {'students': students})

def student_profile(request):
    # view logic here
    return render(request, 'student_profile.html')

def accept_student(request, student_id):
    student = Student.objects.get(id = student_id)
    student.status = 'ACCEPTED'
    student.save()
    return redirect('manage_student')


def reject_student(request, student_id):
    student = Student.objects.get(id = student_id)
    student.status = 'REJECTED'
    student.save()
    return redirect('manage_student')


def student_registration(request):
    if request.method == 'POST':
        name = request.POST.get("txtname")
        ad_no = request.POST.get("txtadno")
        mob = request.POST.get("txtmobno")
        email = request.POST.get("txtemail")
        department = request.POST.get("txtdepartment")
        sex = request.POST.get("txtsex")
        raw_password = request.POST.get("txtpassword")
        if len(request.FILES)!=0:
         image = request.FILES.get("txtimage")
        else:
            return HttpResponse("Image not loaded")
        
        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'student_register.html', {'error': 'Invalid email address.'})
        
        if Student.objects.filter(email=email).exists():
            return render(request, 'student_register.html', {'error': 'Email already registered.'})
        
        if Student.objects.filter(ad_no=ad_no).exists():
            return render(request, 'student_register.html', {'error': 'Admission number already exists.'})
        
        student = Student.objects.create(
            name=name,
            ad_no=ad_no,
            mob=mob,
            img=image,  
            email=email,
            department=department,
            sex=sex,
            password=raw_password,
            type='STUDENT',
        )

        return redirect('index')

    else:
        return render(request, 'student_register.html')
    

def get_student_details(request):
    admission_no = request.GET.get('admission_no')
    if not admission_no:
        return JsonResponse({'error': 'Admission number is required'}, status=400)

    try:
        student = Student.objects.get(ad_no=admission_no)
    except Student.DoesNotExist:
        logging.error(f"Student not found with admission number {admission_no}")
        return JsonResponse({'error': 'Student not found'}, status=404)

    student_details = {
        'name': student.name,
        'email': student.email,
        'Department': student.department,
        'admission_no': student.ad_no,
        'phone': student.mob,
    }

    return JsonResponse(student_details)


def student_details_view(request):
    try:
        return render(request, 'student_details.html')
    except Exception as e:
        logging.error(f"Error rendering template: {e}")
        return JsonResponse({'error': 'Error rendering template'}, status=500)
    

def manage_candidate(request):
    staff_id = request.session.get('staff_id')
    std = Staff.objects.get(id=staff_id)
    dep = Student.objects.filter(department=std.department)
    candidate = Student.objects.filter(type='CANDIDATE', department=std.department)
    return render(request, 'manage_candidate.html', {'candidate': candidate})


def view_candidates(request):
    staff_id = request.session.get('staff_id')
    std = Staff.objects.get(id=staff_id)
    dep = Student.objects.filter(department=std.department)
    candidate = Student.objects.filter(type='CANDIDATE',department=std.department)
    return render(request, 'view_candidates.html', {'candidate': candidate})


def reject_candidate(request, student_id):
    candidate = Student.objects.get(id = student_id)
    candidate.type = 'STUDENT'
    candidate.save()
    return redirect('manage_candidate')


def candidate_registration(request):
    students = Student.objects.all()
    return render(request, 'candidate_registration.html', {'students': students})
    

def accept_candidate(request, students_ad_no):
    students = Student.objects.get(ad_no=students_ad_no)
    students.type = 'CANDIDATE'
    students.save()
    return redirect('candidate_registration')


def candidate_home(request):
        if request.method == 'POST':
            feedback = request.POST.get('thm', '').strip()
            student_id = request.session.get('student_id')

            if not student_id:
                messages.error(request, 'Student ID is not set in the session.')
                return redirect('candidate_home')

            student = get_object_or_404(Student, id=student_id)

            if feedback:
                Student_feed.objects.create(
                    feedback=feedback,
                    student=student,
                )
                messages.success(request, 'Your feedback has been sent successfully!')
                return redirect('candidate_home')
            else:
                messages.error(request, 'Please fill in all fields.')

        blogs = Blog.objects.all()
        return render(request, 'candidate_home.html', {'blogs': blogs})


def candidate_profile(request):
    return render(request,'candidate_profile.html')

import json
from django.http import JsonResponse

def chatbot_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '').lower()  # Case-insensitive

        # E-voting related chatbot responses
        if "hello" in message:
            reply = "Hi there! How can I help you with the E-voting system?"
        elif "how are you" in message:
            reply = "I'm doing well, thanks for asking!"
        elif "your name" in message:
            reply = "I'm DjangoBot, your E-voting assistant!"
        elif "bye" in message:
            reply = "Goodbye! Feel free to reach out anytime."

        # E-voting specific responses
        elif "how does voting work" in message or "how to vote" in message:
            reply = "To vote, log in using your credentials and select your preferred candidate. Then submit your vote securely."
        elif "is my vote confidential?" in message or "security" in message:
            reply = "Yes, the E-voting system is secure and uses blockchain to ensure transparency and tamper-proof records."
        elif "blockchain" in message:
            reply = "Blockchain technology helps record votes in a decentralized and immutable ledger, ensuring fairness and integrity."
        elif "who can participate?" in message or "who can vote" in message:
            reply = "Only registered students are eligible to vote in this system."
        elif "results" in message or "who won" in message:
            reply = "The results will be displayed after the voting period ends. Stay tuned!"
        elif "vote again" in message:
            reply = "Sorry, each user is allowed to vote only once to ensure fairness."
        elif "admin" in message or "panel" in message:
            reply = "Admins can access the dashboard to manage candidates and monitor the voting process."

        else:
            reply = "Sorry, I didn't understand that. Can you please ask something else about the E-voting system?"

        return JsonResponse({'reply': reply})

