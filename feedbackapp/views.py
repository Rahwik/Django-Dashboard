import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from .models import AcademicPhase, Role, Department, Evaluation, Category, Score, AverageScore, EvaluationCriteria

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@login_required
def feedback(request):
    """
    Handles the feedback form submission and rendering.
    """
    if request.method == "POST":
        logger.debug("Received POST request: %s", request.POST)
        try:
            with transaction.atomic():
                # Extract basic form data
                academic_phase = request.POST.get('academicPhase')
                role = request.POST.get('userRole')

                if not academic_phase or not role:
                    logger.error("Missing required fields: academic_phase=%s, role=%s", academic_phase, role)
                    messages.error(request, "Academic Phase and Role are required.")
                    return redirect('feedback')

                # Get or create related objects
                phase_obj, _ = AcademicPhase.objects.get_or_create(
                    name=academic_phase.lower(),
                    defaults={'description': f"{academic_phase.capitalize()} phase"}
                )
                role_obj, _ = Role.objects.get_or_create(
                    name=role.capitalize(),
                    defaults={'description': f"Role: {role.capitalize()}"}
                )
                dept_name = request.POST.get('department') or request.POST.get('hod_department')

                evaluator_name = (
                    request.POST.get(f'{role}_full_name') or
                    request.POST.get(f'{role}Name') or
                    request.POST.get('studentName') or
                    request.POST.get('parentName') or
                    request.user.get_full_name()
                )
                employee_code = (
                    request.POST.get('employeeCode') or
                    request.POST.get(f'{role}_employee_id') or
                    request.POST.get('rollNumber') or
                    request.POST.get('roll_number') or
                    ''
                )

                logger.debug("Creating Evaluation: phase=%s, role=%s, evaluator=%s, employee_code=%s",
                           academic_phase, role, evaluator_name, employee_code)

                # Create Evaluation instance
                evaluation = Evaluation(
                    academic_phase=phase_obj,
                    role=role_obj,
                    evaluator_name=evaluator_name,
                    employee_code=employee_code,
                    submitted_by=request.user,
                    comments=request.POST.get('comments', ''),
                    status='submitted',
                    submitted_at=timezone.now()
                )

                # Handle role-specific fields
                if role.lower() == 'hod' and dept_name:
                    dept_obj, _ = Department.objects.get_or_create(
                        name=dept_name,
                        defaults={'code': dept_name[:3].upper() + str(uuid.uuid4())[:4]}
                    )
                    evaluation.department = dept_obj
                elif role.lower() in ['teacher', 'principal', 'peer']:
                    grade_level = request.POST.get('gradeLevel') or request.POST.get('grade_level')
                    if grade_level:
                        evaluation.grade_level = grade_level
                elif role.lower() == 'student':
                    grade_level = request.POST.get('gradeLevel')
                    if grade_level:
                        evaluation.grade_level = grade_level
                elif role.lower() == 'parent':
                    evaluation.child_name = request.POST.get('childName', '')

                evaluation.save()
                logger.info("Evaluation saved: %s", evaluation)

                # Comprehensive category mapping based on HTML
                category_mappings = {
                    'hod': {
                        'early': {
                            'record_keeping_average': ('Record Keeping', [
                                'record_yearly_plan_submission', 'record_weekly_plan_submission',
                                'record_lesson_plan_submission', 'record_question_papers_submission',
                                'record_answer_scripts_submission', 'record_notebooks_submission',
                                'record_attendance_submission'
                            ]),
                            'punctuality_average': ('Punctuality', [
                                'punctuality_morning_report', 'punctuality_assembly', 'punctuality_classroom',
                                'punctuality_house_meetings', 'punctuality_ptm', 'punctuality_school_events',
                                'punctuality_dining', 'punctuality_evening_classes'
                            ]),
                            'conduct_average': ('Professional Conduct', [
                                'conduct_towards_students', 'conduct_towards_colleagues',
                                'conduct_towards_admin', 'conduct_towards_ground_staff'
                            ]),
                        },
                        'mid': {
                            'lesson_plan_average': ('Lesson Planning', [
                                'lesson_plan_submission', 'lesson_plan_structure', 'lesson_plan_teaching_aids',
                                'lesson_plan_introduction', 'lesson_plan_recap', 'lesson_plan_objectives',
                                'lesson_plan_participation', 'lesson_plan_pacing', 'lesson_plan_outcomes'
                            ]),
                            'classroom_mgmt_average': ('Classroom Management', [
                                'classroom_mgmt_organization', 'classroom_mgmt_instructions',
                                'classroom_mgmt_flexibility', 'classroom_mgmt_attention',
                                'classroom_mgmt_engagement', 'classroom_mgmt_nonverbal',
                                'classroom_mgmt_discipline', 'classroom_mgmt_behavior', 'classroom_mgmt_tasks'
                            ]),
                            # Add other mid-term categories...
                        },
                        # Add post-mid and final as needed
                    },
                    'teacher': {
                        'early': {
                            'policy_average': ('School Policies', [
                                'policy_equal_opportunity', 'policy_transparency', 'policy_communication_channels'
                            ]),
                            'support_average': ('HOD Support', [
                                'support_hod_feedback', 'support_feedback_effectiveness'
                            ]),
                            'substitution_average': ('Substitution Classes', [
                                'substitution_class_count', 'substitution_comfort_level'
                            ]),
                            'relationship_average': ('Professional Relationships', [
                                'relationship_leadership_involvement', 'relationship_fair_treatment',
                                'relationship_staff_caring', 'relationship_staff_ownership',
                                'relationship_collaborative_solving', 'relationship_value_commitment',
                                'relationship_task_fairness', 'relationship_classroom_sincerity',
                                'relationship_staff_connection'
                            ]),
                        },
                        # Add other phases...
                    },
                    'student': {
                        'early': {
                            'k2_average': ('K-2 Early Semester Review', [
                                'k2_school_enjoyment', 'k2_class_attention', 'k2_teacher_help', 'k2_teacher_kindness'
                            ], 'K'),
                            'grade3_12_average': ('III-XII Early Semester Review', [
                                'grade3_12_clarity', 'grade3_12_safety', 'grade3_12_teacher_care',
                                'grade3_12_school_enjoyment'
                            ], '3-12'),
                        },
                        'final': {
                            'k2_average': ('K-2 Final Semester Review', [
                                'learning', 'improvement', 'teacherLikability', 'safety', 'funLearning'
                            ], 'K'),
                            'grade3_12_average': ('III-XII Final Semester Review', [
                                'examPrep', 'encouragement', 'skillImprovement', 'fairness', 'timeUse', 'enjoyment'
                            ], '3-12'),
                        },
                    },
                    # Add mappings for Peer, Principal, Parent, etc.
                }

                # Process scores and averages
                phase = academic_phase.lower()
                role_key = role.lower()
                if role_key in category_mappings and phase in category_mappings[role_key]:
                    for avg_field, (cat_name, criteria_fields, *grade_filter) in category_mappings[role_key][phase].items():
                        # Apply grade filter for student forms
                        if role_key == 'student' and grade_filter:
                            if evaluation.grade_level != grade_filter[0]:
                                continue

                        category, _ = Category.objects.get_or_create(
                            name=cat_name,
                            defaults={'description': f"Category for {cat_name}"}
                        )
                        logger.debug("Processing category: %s", cat_name)

                        total_score = 0
                        valid_scores = 0
                        for field in criteria_fields:
                            score_value = request.POST.get(field)
                            logger.debug("Field %s: %s", field, score_value)
                            if score_value:
                                try:
                                    score = float(score_value)
                                    if field == 'substitution_class_count':  # Handle non-rated fields
                                        if score >= 0:
                                            criteria, _ = EvaluationCriteria.objects.get_or_create(
                                                category=category,
                                                description=field.replace('_', ' ').title()
                                            )
                                            score_obj = Score(
                                                evaluation=evaluation,
                                                criteria=criteria,
                                                score=score
                                            )
                                            score_obj.save()
                                            logger.info("Score saved: %s", score_obj)
                                    elif 1.0 <= score <= 4.0:
                                        criteria, _ = EvaluationCriteria.objects.get_or_create(
                                            category=category,
                                            description=field.replace('_', ' ').title()
                                        )
                                        score_obj = Score(
                                            evaluation=evaluation,
                                            criteria=criteria,
                                            score=score
                                        )
                                        score_obj.save()
                                        logger.info("Score saved: %s", score_obj)
                                        total_score += score
                                        valid_scores += 1
                                    else:
                                        logger.warning("Score out of range: %s for %s", score, field)
                                        messages.warning(request, f"Score {score} for {field} out of range (1-4).")
                                except ValueError:
                                    logger.warning("Invalid score format: %s for %s", score_value, field)
                                    messages.warning(request, f"Invalid score format for {field}.")

                        # Save average score
                        if valid_scores > 0:
                            avg = total_score / valid_scores
                            avg_score_obj = AverageScore(
                                evaluation=evaluation,
                                category=category,
                                average_score=avg
                            )
                            avg_score_obj.save()
                            logger.info("AverageScore saved: %s", avg_score_obj)
                        else:
                            logger.warning("No valid scores for category: %s", cat_name)

                messages.success(request, "Feedback submitted successfully!")
                return redirect('success')

        except Exception as e:
            logger.exception("Error in feedback submission: %s", str(e))
            messages.error(request, f"Error submitting feedback: {str(e)}")
            return redirect('feedback')

    # GET request handling
    context = {
        'academic_phases': AcademicPhase.objects.all(),
        'roles': Role.objects.all(),
        'departments': Department.objects.all(),
        'grade_levels': Evaluation.GRADE_LEVEL_CHOICES,
        'guidelines_url': reverse('guidelines'),
        'current_date': timezone.now().strftime('%Y-%m-%d'),
    }
    return render(request, 'form.html', context)


@login_required
def success(request):
    """
    Renders the success page after successful submission.
    """
    context = {
        'message': 'Your feedback has been successfully submitted!',
        'guidelines_url': reverse('guidelines'),
        'feedback_url': reverse('feedback'),
    }
    logger.info("Rendering success page for user: %s", request.user)
    return render(request, 'success.html', context)


@login_required
def guidelines(request):
    """
    Renders the guidelines page.
    """
    context = {
        'feedback_url': reverse('feedback'),
        'success_url': reverse('success'),
    }
    logger.info("Rendering guidelines page for user: %s", request.user)
    return render(request, 'guidelines.html', context)