from django.urls import path
from .views import AITypingPrompt, CreateGameResults

urlpatterns = [
    path('ai-typing/prompt/', AITypingPrompt.as_view(), name='ai-typing-prompt'),
    path('results/create/', CreateGameResults.as_view(), name='generate-game-results')
]
