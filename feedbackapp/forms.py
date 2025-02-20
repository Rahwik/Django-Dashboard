from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = [
            "respondent_name", "role", "department", "feedback_date",
            "strengths", "improvement", "impact_instance", "additional_comments",
            "overall_rating", "recommendation", "development_suggestions"
        ]
        widgets = {
            'feedback_date': forms.DateInput(attrs={'type': 'date'}),
            'strengths': forms.Textarea(attrs={'rows': 3}),
            'improvement': forms.Textarea(attrs={'rows': 3}),
            'impact_instance': forms.Textarea(attrs={'rows': 3}),
            'additional_comments': forms.Textarea(attrs={'rows': 3}),
            'development_suggestions': forms.Textarea(attrs={'rows': 3}),
        }
