# Generated by Django 5.1.5 on 2025-02-21 14:53

import django.core.validators
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AcademicPhase",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        choices=[
                            ("early", "Early Semester"),
                            ("mid", "Mid-Semester"),
                            ("post-mid", "Post Mid-Semester"),
                            ("final", "Final Semester"),
                        ],
                        max_length=20,
                        unique=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Academic Phase",
                "verbose_name_plural": "Academic Phases",
            },
        ),
        migrations.CreateModel(
            name="Department",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "code",
                    models.CharField(blank=True, max_length=10, null=True, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Department",
                "verbose_name_plural": "Departments",
            },
        ),
        migrations.CreateModel(
            name="Role",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        choices=[
                            ("HOD", "Head of Department"),
                            ("Teacher", "Teacher"),
                            ("Student", "Student"),
                            ("Peer", "Peer"),
                            ("Principal", "Principal"),
                            ("Parent", "Parent"),
                        ],
                        max_length=20,
                        unique=True,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Role",
                "verbose_name_plural": "Roles",
            },
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "applicable_phases",
                    models.ManyToManyField(blank=True, to="feedbackapp.academicphase"),
                ),
                (
                    "applicable_roles",
                    models.ManyToManyField(blank=True, to="feedbackapp.role"),
                ),
            ],
            options={
                "verbose_name": "Category",
                "verbose_name_plural": "Categories",
            },
        ),
        migrations.CreateModel(
            name="Evaluation",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("evaluator_name", models.CharField(max_length=255)),
                (
                    "employee_code",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "grade_level",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("K", "Kindergarten"),
                            ("1-5", "Elementary (1-5)"),
                            ("6-8", "Middle School (6-8)"),
                            ("9-12", "High School (9-12)"),
                            ("K-2", "K-2"),
                            ("3-12", "III-XII"),
                        ],
                        max_length=10,
                        null=True,
                    ),
                ),
                ("child_name", models.CharField(blank=True, max_length=255, null=True)),
                ("submission_date", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("comments", models.TextField(blank=True)),
                (
                    "academic_phase",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="feedbackapp.academicphase",
                    ),
                ),
                (
                    "department",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="feedbackapp.department",
                    ),
                ),
                (
                    "submitted_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submitted_evaluations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="feedbackapp.role",
                    ),
                ),
            ],
            options={
                "verbose_name": "Evaluation",
                "verbose_name_plural": "Evaluations",
            },
        ),
        migrations.CreateModel(
            name="EvaluationCriteria",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("description", models.CharField(max_length=255)),
                (
                    "weight",
                    models.FloatField(
                        default=1.0,
                        validators=[django.core.validators.MinValueValidator(0.1)],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="criteria",
                        to="feedbackapp.category",
                    ),
                ),
            ],
            options={
                "verbose_name": "Evaluation Criteria",
                "verbose_name_plural": "Evaluation Criteria",
            },
        ),
        migrations.CreateModel(
            name="Score",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "score",
                    models.FloatField(
                        help_text="Score between 1.0 and 4.0",
                        validators=[
                            django.core.validators.MinValueValidator(1.0),
                            django.core.validators.MaxValueValidator(4.0),
                        ],
                    ),
                ),
                ("comments", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "criteria",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="feedbackapp.evaluationcriteria",
                    ),
                ),
                (
                    "evaluation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="scores",
                        to="feedbackapp.evaluation",
                    ),
                ),
            ],
            options={
                "verbose_name": "Score",
                "verbose_name_plural": "Scores",
            },
        ),
        migrations.CreateModel(
            name="AverageScore",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "average_score",
                    models.FloatField(
                        help_text="Average score between 1.0 and 4.0",
                        validators=[
                            django.core.validators.MinValueValidator(1.0),
                            django.core.validators.MaxValueValidator(4.0),
                        ],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="feedbackapp.category",
                    ),
                ),
                (
                    "evaluation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="average_scores",
                        to="feedbackapp.evaluation",
                    ),
                ),
            ],
            options={
                "verbose_name": "Average Score",
                "verbose_name_plural": "Average Scores",
                "unique_together": {("evaluation", "category")},
            },
        ),
        migrations.AddIndex(
            model_name="evaluation",
            index=models.Index(
                fields=["academic_phase", "role"], name="feedbackapp_academi_ed5b94_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="evaluation",
            index=models.Index(
                fields=["submission_date"], name="feedbackapp_submiss_ce9d2c_idx"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="score",
            unique_together={("evaluation", "criteria")},
        ),
    ]
