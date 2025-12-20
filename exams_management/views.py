from django.shortcuts import render
from . import models
from . import serializers
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from teachers_users2_management.models import Teacher
from users.models import Profile

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



