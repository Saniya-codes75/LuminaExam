



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import datetime # Changed to import datetime to handle isoformat conversion
from .models import Exam, Question, Result, UserAnswer

def home(request):
    return render(request, 'exam/home.html')

@login_required
def dashboard(request):
    # 1. Fetch all exams from the database
    exams = Exam.objects.all()
    
    # 2. Fetch results for the logged-in user
    results = Result.objects.filter(user=request.user)

    # 3. Map results to exams
    result_map = {}
    for result in results:
        result_map[result.exam.id] = result

    # 4. Prepare data for the HTML template
    exam_data = []
    for exam in exams:
        exam_data.append({
            'exam': exam,
            'result': result_map.get(exam.id)
        })
    return render(request, 'exam/dashboard.html', {
    'exam_data': exam_data,
    'profile': getattr(request.user, 'profile', None) 
    })
   



@login_required
def start_exam(request, exam_id):
    # Check if the user has already submitted this exam
    existing_result = Result.objects.filter(user=request.user, exam_id=exam_id).exists()
    if existing_result:
        return redirect('result_view', exam_id=exam_id) 

    exam = Exam.objects.get(id=exam_id)
    questions = Question.objects.filter(exam=exam)

    # 1. Check if already attempted
    existing_result = Result.objects.filter(user=request.user, exam=exam).first()
    if existing_result:
        user_answers = UserAnswer.objects.filter(result=existing_result)
        return render(request, 'exam/result.html', {
            'exam': exam,
            'result': existing_result,
            'score': existing_result.score,
            'total': existing_result.total_questions,
            'percentage': existing_result.percentage,
            'passed': existing_result.status == "Pass", 
            'user_answers': user_answers
        })

    # 2. Show the Exam (GET) with Anti-Refresh Timer
    if request.method == "GET":
        session_key = f"exam_start_{exam.id}"
        
        if session_key not in request.session:
            request.session[session_key] = timezone.now().isoformat()
        
        start_time_str = request.session[session_key]
        start_time = datetime.datetime.fromisoformat(start_time_str)
        elapsed_time = (timezone.now() - start_time).total_seconds()
        
        remaining_time = max(0, int((exam.duration * 60) - elapsed_time))
        
        context = {
            'exam': exam,
            'questions': questions,
            'remaining_time': remaining_time 
        }
        return render(request, 'exam/start_exam.html', context)
        # 3. Save the Result (POST) - 
    if request.method == "POST":
        total_score_obtained = 0
        correct_count = 0
        total_q_count = questions.count()
        
        #  Result record
        result = Result.objects.create(
            user=request.user, 
            exam=exam, 
            total_questions=total_q_count,
            score=0, 
            percentage=0, 
            status="Fail"
        )

        for q in questions:
            ans_val = request.POST.get(f'question_{q.id}')
            selected_int = int(ans_val) if ans_val and ans_val.isdigit() else None
            is_correct = False

            if selected_int is not None and selected_int == q.correct_option:
                is_correct = True
                correct_count += 1
                
                total_score_obtained += q.marks 

            UserAnswer.objects.create(
                result=result, 
                question=q,
                selected_option=selected_int, 
                is_correct=is_correct
            )

        # Final Calculations
        max_marks = exam.total_marks if exam.total_marks > 0 else 1
        percent = round((total_score_obtained / max_marks) * 100, 2)
        
        result.score = total_score_obtained
        result.correct_answers = correct_count
        result.wrong_answers = total_q_count - correct_count
        result.percentage = percent
        
        # Determine status based on percentage
        passing_threshold = getattr(exam, 'passing_marks', 40)
        result.status = "Pass" if percent >= passing_threshold else "Fail"
        result.save()

        # session timer
        request.session.pop(f"exam_start_{exam.id}", None)

        return render(request, 'exam/result.html', {
            'exam': exam,
            'result': result,
            'score': result.score,
            'total': total_q_count,
            'percentage': percent,
            'passed': result.status == "Pass",
            'user_answers': UserAnswer.objects.filter(result=result)
        })
       


  
@login_required
def result_view(request, exam_id):
   
    result = Result.objects.filter(exam_id=exam_id, user=request.user).last()
    
    result = Result.objects.get(user=request.user, exam_id=exam_id)
    user_answers = UserAnswer.objects.filter(result=result)

    context = {
        'result': result,
        'exam': result.exam,
        'total': result.total_questions,
        'correct': result.correct_answers,
        'wrong': result.wrong_answers,
        'percentage': result.percentage,
        'passed': result.status == "Pass",
        'user_answers': user_answers
    }
   
    return render(request, 'exam/result.html', context)

@login_required
def leaderboard(request, exam_id):
    exam = Exam.objects.get(id=exam_id)
    results = Result.objects.filter(exam=exam).order_by('-score')
    leaderboard_data = []
    rank = 1

    for result in results:
        leaderboard_data.append({
            'rank': rank,
            'user': result.user.username,
            'score': result.score,
            'percentage': result.percentage
        })
        rank += 1

    return render(request, 'exam/leaderboard.html', {
        'exam': exam,
        'leaderboard_data': leaderboard_data
    })
@login_required
def profile(request):
    # Safe fetch
    user_profile = getattr(request.user, 'profile', None)
    
    return render(request, 'exam/profile.html', {
        'profile': user_profile,
        'role': getattr(user_profile, 'role', 'student') # Default student
    })

@login_required
def edit_profile(request):
    user_profile = request.user.profile
    if request.method == 'POST':
       
        user_profile.address = request.POST.get('address')
        user_profile.roll_no = request.POST.get('roll_no')
        # Profile pic update logic 
        if request.FILES.get('profile_pic'):
            user_profile.profile_pic = request.FILES.get('profile_pic')
        
        user_profile.save()
        return redirect('profile')
    
    return render(request, 'exam/edit_profile.html', {'profile': user_profile})




@login_required
def exam_instructions(request, exam_id):
    exam = Exam.objects.get(id=exam_id)
    existing_result = Result.objects.filter(user=request.user, exam=exam).first()
    if existing_result:
        return redirect('result_view', exam_id=exam.id)

    return render(request, 'exam/instructions.html', {'exam': exam})


    
@login_required
def generate_marksheet(request, exam_id):
    result = Result.objects.get(user=request.user, exam_id=exam_id)
    
    # SAFETY CHECK: If profile doesn't exist, create an empty one or handle it
    try:
        profile = request.user.profile
    except:
        # This prevents the "RelatedObjectDoesNotExist" error
        profile = None 

    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=Verify-{result.id}"

    context = {
        'result': result,
        'profile': profile,
        'exam': result.exam,
        'qr_url': qr_url,
        'today': timezone.now().date(),
    }
    return render(request, 'exam/marksheet_template.html', context)
@login_required
def home_redirect(request):
    try:
        role = request.user.profile.role
    except Exception:
        role = 'student'

    # Admin goes to the standard Django admin panel
    if role == 'admin' or request.user.is_superuser:
        return redirect('/admin/') 
    
    # Faculty goes to their custom dashboard
    elif role == 'faculty':
        return redirect('faculty_dashboard')
    
    # Students go to their exam list
    else:
        return redirect('dashboard')





from django.shortcuts import render
from .models import Exam  
from django.contrib.auth.models import User

@login_required
def faculty_dashboard(request):
    
    exams_list = Exam.objects.all() 
    
    
    student_count = User.objects.filter(is_staff=False).count()
    context = {
    'exams': exams_list,
    'student_count': student_count,
    'profile': getattr(request.user, 'profile', None), 
    }
   
    return render(request, 'exam/faculty_dashboard.html', context)



@login_required
def admin_view_results(request, exam_id):
    
    if request.user.profile.role not in ['admin', 'faculty']:
        return redirect('dashboard')
        
    exam = Exam.objects.get(id=exam_id)
    results = Result.objects.filter(exam=exam)
    return render(request, 'exam/admin_view_results.html', {
        'exam': exam,
        'results': results
    })
from django.shortcuts import render, redirect, get_object_or_404
from .models import Exam, Question


@login_required
def add_question(request, exam_id):
    if request.user.profile.role not in ['faculty', 'admin']:
        return redirect('home_redirect')

    exam = get_object_or_404(Exam, id=exam_id)

    if request.method == 'POST':
       
        Question.objects.create(
            exam=exam,
            question_text=request.POST.get('text'), 
            option1=request.POST.get('op1'),
            option2=request.POST.get('op2'),
            option3=request.POST.get('op3'),
            option4=request.POST.get('op4'),
            correct_option=request.POST.get('correct'),
        )
        return redirect('faculty_dashboard')

    return render(request, 'exam/add_question.html', {'exam': exam})







@login_required
def view_exam_results(request, exam_id):

    if request.user.profile.role != 'faculty':
        return redirect('dashboard')
        
    exam = get_object_or_404(Exam, id=exam_id)
    
    results = Result.objects.filter(exam=exam).select_related('user')
    
    return render(request, 'exam/faculty_view_results.html', {
        'exam': exam,
        'results': results
    })
