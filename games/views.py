from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai
from .models import TypingPrompt, GameResults

# Handles AI-based prompt generation for typing practice
class AITypingPrompt(APIView):

    def post(self, request): 
        # Extract difficulty level and total time from POST request
        difficulty = request.data.get('difficulty')
        total_time = request.data.get('total_time')

        # Return error if required fields are missing
        if not difficulty or not total_time:
            return Response({'error': 'Missing difficulty or total_time'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the AI prompt for Gemini based on inputs
        prompt = (
            f"Generate a typing test paragraph for a {difficulty} mode. "
            f"The total length should reflect about {total_time} seconds of typing. "
            "The paragraph should be grammatically correct, engaging, and suitable for a typing test."
        )

        try:
            # Configure Gemini API
            genai.configure(api_key=settings.GOOGLE_API_KEY)

            # Use the Gemini model to generate content
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            generated_text = response.text.strip()  # Clean up any whitespace

            # Save generated prompt to database
            typing_prompt = TypingPrompt.objects.create(
                difficulty=difficulty,
                text=generated_text,
                total_time=total_time
            )

            # Return success response with prompt data
            return Response({
                "id": typing_prompt.id,
                "text": typing_prompt.text,
                "difficulty": typing_prompt.difficulty,
                "total_time": typing_prompt.total_time
            }, status=status.HTTP_201_CREATED)

        # Handle any unexpected errors from API or DB
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Handles saving game results (WPM, accuracy, etc.) to the backend
class CreateGameResults(APIView):

    def post(self, request):
        try:
            # Extract data from request, convert to integers
            correct_words = int(request.data.get('correct_words'))
            total_words = int(request.data.get('total_words'))
            time_taken = int(request.data.get('time_taken', 60))  # Default to 60s if not provided

            # Basic validation
            if time_taken <= 0 or total_words == 0:
                return Response({'error': 'Invalid time_taken or total_words'}, status=status.HTTP_400_BAD_REQUEST)

            # Calculate WPM and accuracy based on input
            wpm = (correct_words / time_taken) * 60
            accuracy = (correct_words / total_words) * 100

            # Save result to the database, associate with user if logged in
            game_result = GameResults.objects.create(
                player=request.user if request.user.is_authenticated else None,
                wpm=wpm,
                accuracy=accuracy,
                correct_words=correct_words,
                total_words=total_words,
                time_taken=time_taken
            )

            # Return created game result info
            return Response({
                "id": game_result.id,
                "wpm": round(game_result.wpm, 2),
                "accuracy": round(game_result.accuracy, 2),
                "correct_words": game_result.correct_words,
                "total_words": game_result.total_words,
                "time_taken": game_result.time_taken,
                "player": str(game_result.player) if game_result.player else "Anonymous",
                "played_at": game_result.played_at,
            }, status=status.HTTP_201_CREATED)

        # Catch and return any exceptions
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
