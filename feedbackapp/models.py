from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
import uuid


class AcademicPhase(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Academic Phase"
        verbose_name_plural = "Academic Phases"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name.capitalize()


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    applicable_roles = models.ManyToManyField('Role', blank=True)
    applicable_phases = models.ManyToManyField('AcademicPhase', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class EvaluationCriteria(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name="criteria")
    description = models.CharField(max_length=255)
    weight = models.FloatField(default=1.0, validators=[MinValueValidator(0.1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Evaluation Criterion"
        verbose_name_plural = "Evaluation Criteria"
        unique_together = ('category', 'description')
        ordering = ['category__name', 'description']

    def __str__(self):
        return f"{self.category.name} - {self.description}"


class Evaluation(models.Model):
    GRADE_LEVEL_CHOICES = [
        ('K', 'Kindergarten (K-2)'),
        ('1-5', 'Elementary (1-5)'),
        ('3-12', 'Grades III-XII'),
        ('6-8', 'Middle School (6-8)'),
        ('9-12', 'High School (9-12)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    academic_phase = models.ForeignKey('AcademicPhase', on_delete=models.CASCADE)
    role = models.ForeignKey('Role', on_delete=models.CASCADE)
    evaluator_name = models.CharField(max_length=255)
    employee_code = models.CharField(max_length=50, blank=True)  # Remains as-is; migration will handle NULLs
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    grade_level = models.CharField(max_length=10, choices=GRADE_LEVEL_CHOICES, blank=True)
    child_name = models.CharField(max_length=255, blank=True, null=True)
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="evaluations")
    comments = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('reviewed', 'Reviewed')],
        default='draft'
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Evaluation"
        verbose_name_plural = "Evaluations"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.evaluator_name} ({self.role.name}) - {self.academic_phase.name}"


class Score(models.Model):
    evaluation = models.ForeignKey('Evaluation', on_delete=models.CASCADE, related_name="scores")
    criteria = models.ForeignKey('EvaluationCriteria', on_delete=models.CASCADE, related_name="scores")
    score = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(4.0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Score"
        verbose_name_plural = "Scores"
        unique_together = ('evaluation', 'criteria')
        ordering = ['evaluation', 'criteria__description']

    def __str__(self):
        return f"{self.evaluation} - {self.criteria.description}: {self.score}"


class AverageScore(models.Model):
    evaluation = models.ForeignKey('Evaluation', on_delete=models.CASCADE, related_name="average_scores")
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name="average_scores")
    average_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(4.0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Average Score"
        verbose_name_plural = "Average Scores"
        unique_together = ('evaluation', 'category')
        ordering = ['evaluation', 'category__name']

    def __str__(self):
        return f"{self.evaluation} - {self.category.name}: {self.average_score}"