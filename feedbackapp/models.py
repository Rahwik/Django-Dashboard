from django.db import models

class AcademicPhase(models.Model):
    PHASE_CHOICES = (
        ('early', 'Early Semester'),
        ('mid', 'Mid-Semester'),
        ('post-mid', 'Post Mid-Semester'),
        ('final', 'Final Semester'),
    )
    name = models.CharField(max_length=20, choices=PHASE_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., HOD, Teacher, Student

    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Evaluation(models.Model):
    academic_phase = models.ForeignKey(AcademicPhase, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    evaluator_name = models.CharField(max_length=100)
    employee_code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    grade_level = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.evaluator_name} - {self.role} - {self.academic_phase}"

class RatingCategory(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)  # e.g., Record Keeping, Punctuality

    def __str__(self):
        return f"{self.name} - {self.evaluation}"

class Rating(models.Model):
    category = models.ForeignKey(RatingCategory, on_delete=models.CASCADE, related_name='ratings')
    criterion = models.CharField(max_length=200)
    score = models.IntegerField(choices=[(i, str(i)) for i in range(1, 5)])

    def __str__(self):
        return f"{self.criterion} - {self.score}"

    class Meta:
        unique_together = ('category', 'criterion')