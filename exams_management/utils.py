from . import models
def calculate_score(attempt):
    """Calculate student's score for a test attempt"""
    total_marks = 0
    earned_marks = 0
    
    # Get all answers for this attempt
    answers = models.StudentAnswer.objects.filter(attempt=attempt)
    
    for answer in answers:
        question = answer.question
        total_marks += question.marks
        
        if question.question_type == "single":
            # Single choice - check if selected choice is correct
            if answer.selected_choice and answer.selected_choice.is_correct:
                earned_marks += question.marks
        elif question.question_type == "multiple":
            # Multiple choice - need to check all correct choices are selected
            # and no incorrect choices are selected
            correct_choices = question.choices.filter(is_correct=True)
            selected_choices = answer.selected_choice.all()  # For multiple choice, you might need a ManyToMany field
            
            # This is simplified - you'll need to adjust based on your model structure
            # For now, let's assume StudentAnswer has a ManyToManyField for multiple choices
            all_correct_selected = True
            for correct_choice in correct_choices:
                if correct_choice not in selected_choices:
                    all_correct_selected = False
                    break
            
            no_incorrect_selected = True
            selected_choices = answer.selected_choice.all()
            for selected in selected_choices:
                if not selected.is_correct:
                    no_incorrect_selected = False
                    break
            
            if all_correct_selected and no_incorrect_selected:
                earned_marks += question.marks
    
    # Update the attempt with scores
    attempt.total_score = total_marks
    attempt.earned_score = earned_marks
    attempt.percentage = (earned_marks / total_marks * 100) if total_marks > 0 else 0
    attempt.save()
    
    return attempt.percentage