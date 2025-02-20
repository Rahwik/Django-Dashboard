from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from .models import AcademicPhase, Role, Department, Evaluation, RatingCategory, Rating
from django.contrib import messages

@login_required
def feedback(request):
    if request.method == "POST":
        try:
            # Extract basic form data
            academic_phase = request.POST.get('academicPhase')
            role = request.POST.get('userRole')
            
            if not academic_phase or not role:
                messages.error(request, "Academic Phase and Role are required.")
                return redirect('feedback')

            # Get or create related objects
            phase_obj, _ = AcademicPhase.objects.get_or_create(name=academic_phase)
            role_obj, _ = Role.objects.get_or_create(name=role.capitalize())

            # Create Evaluation instance
            evaluation = Evaluation(
                academic_phase=phase_obj,
                role=role_obj,
                evaluator_name=request.POST.get(f'{role}_name', request.user.get_full_name()),
                employee_code=request.POST.get('employee_code') or request.POST.get('hod_code'),
                submitted_by=request.user
            )

            # Handle additional fields based on role
            if role.lower() == 'hod':
                dept = request.POST.get('department')
                if dept:
                    dept_obj, _ = Department.objects.get_or_create(name=dept)
                    evaluation.department = dept_obj
            elif role.lower() in ['teacher', 'principal', 'peer']:
                evaluation.grade_level = request.POST.get('grade')
            elif role.lower() == 'student':
                evaluation.grade_level = request.POST.get('grade')
                # Handle student-specific fields if needed
            elif role.lower() == 'parent':
                evaluation.child_name = request.POST.get('child_name')

            evaluation.save()

            # Process rating sections
            sections = {
                'record-keeping': ['timely_submission_yearly_plan', 'timely_submission_weekly_plan', ...],  # Add all fields
                'punctuality': ['morning_reporting', 'assembly', ...],  # Add all fields
                # Add other sections based on your form structure
            }

            for section_name, fields in sections.items():
                category = RatingCategory.objects.create(
                    evaluation=evaluation,
                    name=section_name.replace('-', ' ').title()
                )
                
                for field in fields:
                    score = request.POST.get(field)
                    if score and score.isdigit() and 1 <= int(score) <= 4:
                        Rating.objects.create(
                            category=category,
                            criterion=field.replace('_', ' ').title(),
                            score=int(score)
                        )

            messages.success(request, "Feedback submitted successfully!")
            return redirect('success')

        except Exception as e:
            messages.error(request, f"Error submitting feedback: {str(e)}")
            return redirect('feedback')

    # GET request handling
    context = {
        'academic_phases': AcademicPhase.objects.all(),
        'roles': Role.objects.all(),
        'departments': Department.objects.all(),
        'grade_levels': [
            ('K', 'Kindergarten'),
            ('1-5', 'Elementary (1-5)'),
            ('6-8', 'Middle School (6-8)'),
            ('9-12', 'High School (9-12)')
        ]
    }
    return render(request, r'E:\Data Analysis Dashboard\MainDir\feedbackapp\templates\form.html', context)

@login_required
def success(request):
    return render(request, r'E:\Data Analysis Dashboard\MainDir\feedbackapp\templates\success.html', {
        'message': 'Your feedback has been successfully submitted!'
    })