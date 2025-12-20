from django.shortcuts import render
from . import models
from . import serializers
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from teachers_users2_management.models import Teacher
from users.models import Profile
from .utils import calculate_score
from django.utils import timezone

def ensure_teacher(request):
  try:
    profile = Profile.objects.get(user=request.user)
  except Profile.DoesNotExist:
    messages.error(request, "Profile not found.")
    return False

  if profile.role != "teacher":
    messages.error(request, "Unauthorized action")
    return False
  return True



@login_required
def test_create(request):
  if request.method == "POST":
    if not ensure_teacher(request):
      return redirect("profile")

    subject = request.POST.get("subject", "").strip()
    description = request.POST.get("description", "").strip()
    time_limit = request.POST.get("time_limit", 60)

    if not subject or len(subject) < 4:
      messages.error(request, "Subject must be at least 2 characters.")
      return redirect("test_create")
    
    teacher = Teacher.objects.get(user=request.user)
    if teacher.subject != subject:
      messages.error(request, f"Your subject is {teacher.subject} not {subject}")
      return redirect("test_create")
    
    try:
      time_limit = int(time_limit)
      if time_limit < 1 or time_limit > 480:
        raise ValueError()
    except ValueError:
      messages.error(request, "Time limit must be between 1 and 480 minutes.")
      return redirect("test_create")
    
    test = models.Test.objects.create(
      subject=subject,
      description=description,
      time_limit=time_limit,
      teacher=request.user
    )
    messages.success(request, "Test created successfully!")
    return redirect("test_list")
  return render(request, "create_test.html")


@login_required
def test_update(request, test_id):

  if not ensure_teacher(request):
    return redirect("profile")
  
  test = get_object_or_404(models.Test, id=test_id, teacher=request.user)


  if test.is_published:
    messages.error(request, "Published tests cannot be edited.")
    return redirect("test_list")

  if request.method == "POST":
    subject = request.POST.get("subject", "").strip()
    description = request.POST.get("description", "").strip()
    time_limit = request.POST.get("time_limit", test.time_limit)

    if not subject or len(subject) < 2:
      messages.error(request, "Subject must be at least 2 characters.")
      return render(request, "create_test.html", {"test": test})

    try:
      time_limit = int(time_limit)
      if time_limit < 1 or time_limit > 480:
        raise ValueError()
    except ValueError:
      messages.error(request, "Time limit must be between 1 and 480 minutes.")
      return render(request, "create_test.html", {"test": test})

    test.subject = subject
    test.description = description
    test.time_limit = time_limit
    test.save()
    messages.success(request, "Test updated successfully!")
    return redirect("test_list")
  return render(request, "create_test.html", {"test": test})


@login_required
def test_delete(request, test_id):
  if not ensure_teacher(request):
    return redirect("profile")
  
  test = get_object_or_404(models.Test, id=test_id, teacher=request.user)

  if request.method == "POST":
    test.delete()
    messages.success(request, "Test deleted successfully!")
    return redirect("test_list")

  return render(request, "test_confirm_delete.html", {"test": test})


@login_required
def test_publish(request, test_id):
  if not ensure_teacher(request):
    return redirect("profile")

  test = get_object_or_404(models.Test, id=test_id, teacher=request.user)

  if test.questions.count() == 0:
    messages.error(request, "Cannot publish a test with no questions.")
    return redirect("test_list")

  test.is_published = not test.is_published
  test.save(update_fields=["is_published"])
  messages.success(request, f"Test is now {'Published' if test.is_published else 'Draft'}")
  return redirect("test_list")
  
@login_required
def test_list(request):
  tests = models.Test.objects.filter(teacher=request.user).order_by("-date_added")
  return render(request, "test_list.html", {"tests": tests})

# Questions Management 

@login_required
def question_list(request, test_id):
  test = get_object_or_404(models.Test, id=test_id, teacher=request.user)
  questions = test.questions.all()

  return render(request, "question_list.html", {
   "test": test,
    "questions": questions
  })


@login_required
def question_create(request, test_id):
  if not ensure_teacher(request):
    return redirect("profile")

  test = get_object_or_404(models.Test, id=test_id, teacher=request.user)

  if test.is_published:
    messages.error(request, "You cannot add questions to a published test.")
    return redirect("question_list", test_id=test.id)

  if request.method == "POST":
    question_text = request.POST.get("question_text", "").strip()
    question_type = request.POST.get("question_type", "single")
    marks = request.POST.get("marks", 1)
    explanation = request.POST.get("explanation", "").strip()

    if question_type not in ["single", "multiple"]:
      messages.error(request, "Invalid question type.")
      return render(request, "create_question.html", {
        "test": test,
        "question": None
      })

    if not question_text:
      messages.error(request, "Question text is required.")
      return render(request, "create_question.html", {
        "test": test,
        "question": None
      })

    try:
      marks = int(marks)
      if marks < 1:
        raise ValueError()
    except ValueError:
      messages.error(request, "Marks must be a positive number.")
      return render(request, "create_question.html", {
        "test": test,
        "question": None
      })

    models.Questions.objects.create(
      test=test,
      question_text=question_text,
      question_type=question_type,
      marks=marks,
      explanation=explanation,
      order=test.questions.count() + 1
    )

    messages.success(request, "Question added successfully.")
    return redirect("question_list", test_id=test.id)

  return render(request, "create_question.html", {
    "test": test,
    "question": None
  })


@login_required
def question_update(request, question_id):
  if not ensure_teacher(request):
    return redirect("profile")
  
  question = get_object_or_404(
    models.Questions,
    id=question_id,
    test__teacher=request.user
  )

  if question.test.is_published:
    messages.error(request, "You cannot edit questions in a published test.")
    return redirect("question_list", test_id=question.test.id)

  if request.method == "POST":
    question_text = request.POST.get("question_text", "").strip()
    question_type = request.POST.get("question_type", question.question_type)
    marks = request.POST.get("marks", question.marks)
    explanation = request.POST.get("explanation", "").strip()

    if question_type not in ["single", "multiple"]:
      messages.error(request, "Invalid question type.")
      return render(request, "create_question.html", {"question": question})

    if not question_text:
      messages.error(request, "Question text is required.")
      return render(request, "create_question.html", {"question": question})

    question.question_text = question_text
    question.question_type = question_type
    question.marks = int(marks)
    question.explanation = explanation
    question.save()

    messages.success(request, "Question updated successfully.")
    return redirect("question_list", test_id=question.test.id)

  return render(request, "create_question.html", {"question": question})

@login_required
def question_delete(request, question_id):
  if not ensure_teacher(request):
    return redirect("profile")
  question = get_object_or_404(
    models.Questions,
    id=question_id,
    test__teacher=request.user
  )

  if request.method == "POST":
    test_id = question.test.id
    question.delete()
    messages.success(request, "Question deleted.")
    return redirect("question_list", test_id=test_id)
  return render(request, "question_confirm_delete.html", {"question": question})

# Choice creation

@login_required
def choice_list(request, question_id):
  # if not ensure_teacher(request):
  #   return redirect("profile")
  
  question = get_object_or_404(
    models.Questions,
    id=question_id,
    test__teacher=request.user
  )

  choices = question.choices.all()
  return render(request, "choice_list.html", {
    "question": question,
    "choices": choices
  })

@login_required
def choice_create(request, question_id):
  if not ensure_teacher(request):
    return redirect("profile")
  question = get_object_or_404(
    models.Questions,
    id=question_id,
    test__teacher=request.user
  )

  if question.test.is_published:
    messages.error(request, "You cannot add choices to a published test.")
    return redirect("choice_list", question_id=question.id)

  if request.method == "POST":
    choice_text = request.POST.get("choice_text", "").strip()
    is_correct = request.POST.get("is_correct") == "on"

    if not choice_text:
      messages.error(request, "Choice text is required.")
      return render(request, "create_choice.html", {"question": question})

    # Enforce single correct choice
    if question.question_type == "single" and is_correct:
      question.choices.update(is_correct=False)

    models.Choice.objects.create(
      question=question,
      choice_text=choice_text,
      is_correct=is_correct,
      order=question.choices.count() + 1
    )

    messages.success(request, "Choice added successfully.")
    return redirect("choice_list", question_id=question.id)

  return render(request, "create_choice.html", {"question": question})


@login_required
def choice_update(request, choice_id):
  if not ensure_teacher(request):
    return redirect("profile")
  choice = get_object_or_404(
    models.Choice,
      id=choice_id,
      question__test__teacher=request.user
    )

  question = choice.question
  if question.test.is_published:
    messages.error(request, "You cannot edit choices in a published test.")
    return redirect("choice_list", question_id=question.id)

  if request.method == "POST":
    choice_text = request.POST.get("choice_text", "").strip()
    is_correct = request.POST.get("is_correct") == "on"

    if not choice_text:
      messages.error(request, "Choice text is required.")
      return render(request, "create_choice.html", {"choice": choice})

    if question.question_type == "single" and is_correct:
      question.choices.update(is_correct=False)

    choice.choice_text = choice_text
    choice.is_correct = is_correct
    choice.save()

    messages.success(request, "Choice updated successfully.")
    return redirect("choice_list", question_id=question.id)

  return render(request, "create_choice.html", {"choice": choice})


@login_required
def choice_delete(request, choice_id):
  if not ensure_teacher(request):
    return redirect("profile")
  choice = get_object_or_404(
    models.Choice,
    id=choice_id,
    question__test__teacher=request.user
  )

  if request.method == "POST":
    question_id = choice.question.id
    choice.delete()
    messages.success(request, "Choice deleted.")
    return redirect("choice_list", question_id=question_id)

  return render(request, "choice_confirm_delete.html", {"choice": choice})


# Add to exams_management/views.py

@login_required
def student_test_list(request):
    """View all published tests available for students"""
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect("profile")
        
    if profile.role != "student":
        messages.error(request, "Only students can view tests.")
        return redirect("profile")
        
    published_tests = models.Test.objects.filter(is_published=True)
    
    # Get completed attempts for this student
    completed_attempts = models.StudentTestAttempt.objects.filter(
        student=request.user,
        is_completed=True
    )
    
    # Create a list of tests with attempt info
    tests_with_info = []
    for test in published_tests:
        # Find if this test has been completed by the student
        attempt = completed_attempts.filter(test=test).first()
        
        tests_with_info.append({
            'test': test,
            'has_attempt': attempt is not None,
            'attempt_id': attempt.id if attempt else None
        })
    
    return render(request, "student_test_list.html", {
        "tests_with_info": tests_with_info,
    })




# Take test

@login_required
def take_test(request, test_id):
    """Student takes a test"""
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect("profile")
    
    # Only students can take tests
    if profile.role != "student":
        messages.error(request, "Only students can take tests.")
        return redirect("profile")
    
    # Get the test
    test = get_object_or_404(models.Test, id=test_id, is_published=True)
    
    # Check if student has already taken this test
    existing_attempt = models.StudentTestAttempt.objects.filter(
        student=request.user,
        test=test
    ).first()
    
    if existing_attempt and existing_attempt.is_completed:
        messages.info(request, "You have already completed this test.")
        return redirect("test_results", attempt_id=existing_attempt.id)
    
    # Get all questions with their choices
    questions = test.questions.all().order_by('order')
    
    # If this is a fresh attempt, create one
    if not existing_attempt:
        existing_attempt = models.StudentTestAttempt.objects.create(
            student=request.user,
            test=test,
            start_time=timezone.now()
        )
    
    # Handle form submission
    if request.method == "POST":
        # Process student answers
        for question in questions:
            if question.question_type == "single":
                # Single choice - get selected choice ID
                selected_choice_id = request.POST.get(f"question_{question.id}")
                if selected_choice_id:
                    choice = get_object_or_404(models.Choice, id=selected_choice_id)
                    # Save or update student answer
                    models.StudentAnswer.objects.update_or_create(
                        attempt=existing_attempt,
                        question=question,
                        defaults={'selected_choice': choice}
                    )
            elif question.question_type == "multiple":
                # Multiple choice - get list of selected choice IDs
                selected_choice_ids = request.POST.getlist(f"question_{question.id}")
                # First, clear existing answers for this question
                models.StudentAnswer.objects.filter(
                    attempt=existing_attempt,
                    question=question
                ).delete()
                # Then save new selections
                for choice_id in selected_choice_ids:
                    choice = get_object_or_404(models.Choice, id=choice_id)
                    models.StudentAnswer.objects.create(
                        attempt=existing_attempt,
                        question=question,
                        selected_choice=choice
                    )
        
        # Check if student is submitting for grading
        if 'submit_test' in request.POST:
            existing_attempt.is_completed = True
            existing_attempt.end_time = timezone.now()
            existing_attempt.save()
            
            # Calculate score
            calculate_score(existing_attempt)
            
            messages.success(request, "Test submitted successfully!")
            return redirect("test_results", attempt_id=existing_attempt.id)
        else:
            # Save progress
            messages.success(request, "Progress saved!")
            return redirect("take_test", test_id=test_id)
    
    # For GET request, render the test
    return render(request, "take_test.html", {
        "test": test,
        "questions": questions,
        "attempt": existing_attempt
    })


# Test result


@login_required
def test_results(request, attempt_id):
    """Show student's test results"""
    attempt = get_object_or_404(
        models.StudentTestAttempt,
        id=attempt_id,
        student=request.user
    )
    
    # Get all questions with student's answers
    questions = attempt.test.questions.all().order_by('order')
    
    # Prepare question details with student answers and calculate score
    question_details = []
    total_score = 0
    score_obtained = 0
    
    for question in questions:
        student_answer = models.StudentAnswer.objects.filter(
            attempt=attempt,
            question=question
        ).first()
        
        # Check if answer is correct
        is_correct = False
        if student_answer:
            if question.question_type == "single":
                # Single choice - check if selected choice is correct
                is_correct = student_answer.selected_choice.is_correct if student_answer.selected_choice else False
            elif question.question_type == "multiple":
                # Multiple choice - need to check all selections
                student_choices = models.StudentAnswer.objects.filter(
                    attempt=attempt,
                    question=question
                ).values_list('selected_choice_id', flat=True)
                
                correct_choice_ids = question.choices.filter(is_correct=True).values_list('id', flat=True)
                
                # Check if all correct choices are selected and no incorrect ones are selected
                is_correct = set(student_choices) == set(correct_choice_ids)
        
        # Calculate score for this question
        question_score = 0
        if is_correct:
            question_score = question.marks
            score_obtained += question.marks
        
        total_score += question.marks
        
        question_details.append({
            'question': question,
            'student_answer': student_answer,
            'correct_choices': question.choices.filter(is_correct=True),
            'is_correct': is_correct,
            'question_score': question_score,
            'max_score': question.marks
        })
    
    # Calculate percentage
    percentage = 0
    if total_score > 0:
        percentage = (score_obtained / total_score) * 100
    
    # Determine if passed (using 60% as passing threshold)
    is_passed = percentage >= 60
    
    # Get teacher name - use first_name and last_name or email
    teacher_name = "Unknown"
    if attempt.test.teacher:
        teacher = attempt.test.teacher
        if teacher.first_name and teacher.last_name:
            teacher_name = f"{teacher.first_name} {teacher.last_name}"
        elif teacher.first_name:
            teacher_name = teacher.first_name
        elif teacher.email:
            teacher_name = teacher.email
        else:
            teacher_name = "Teacher"
    
    # Prepare context with all needed data
    context = {
        "attempt": attempt,
        "question_details": question_details,
        "student": {
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "full_name": f"{request.user.first_name} {request.user.last_name}" if request.user.first_name and request.user.last_name else "Student",
            "email": request.user.email
        },
        "score_details": {
            "score_obtained": score_obtained,
            "total_score": total_score,
            "percentage": percentage,
            "is_passed": is_passed,
            "passing_threshold": 60
        },
        "test": {
            "subject": attempt.test.subject,
            "description": attempt.test.description,
            "time_limit": attempt.test.time_limit,
            "teacher": teacher_name,  # Use the formatted teacher name
            "questions_count": questions.count()
        }
    }
    
    return render(request, "test_results.html", context)