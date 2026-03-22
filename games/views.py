from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.utils import timezone

from .models import Game, GameSession, StudentResponse, Score, Feedback
from .serializers import (
    GameSessionSerializer,
    GameSessionCreateSerializer,
    StudentResponseSerializer,
    ScoreSerializer,
    FeedbackSerializer
)

from students.models import StudentProfile
from questions.models import Question
from questions.serializers import QuestionForGameSerializer
from ai_services.adaptive_learning import AdaptiveLearningAI

import random


# ─────────────────────────────────────────
# START GAME SESSION
# ─────────────────────────────────────────

class StartGameSessionView(APIView):
    """
    Start a new game session with AI-powered adaptive questions
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            profile = StudentProfile.objects.get(user=request.user)

            subject_id = request.data.get('subject_id')
            topic_id = request.data.get('topic_id')
            num_questions = request.data.get('num_questions', 10)
            use_adaptive = request.data.get('use_adaptive', True)

            if not subject_id or not topic_id:
                return Response({
                    'error': 'subject_id and topic_id are required'
                }, status=status.HTTP_400_BAD_REQUEST)

            from academics.models import Topic
            topic = Topic.objects.get(id=topic_id)

            # Create game session
            game_session = GameSession.objects.create(
                student=profile,
                subject_id=subject_id,
                topic_id=topic_id,
                total_questions=num_questions,
                status='IN_PROGRESS'
            )

            # Get questions
            if use_adaptive:
                try:
                    ai_system = AdaptiveLearningAI()

                    result = ai_system.get_adaptive_questions(
                        profile,
                        topic,
                        num_questions
                    )

                    selected_questions = result['questions']

                    personalization_info = {
                        'difficulty_mix': result.get('difficulty_mix', {}),
                        'performance_level': result.get('performance_level', 'BEGINNER'),
                        'reason': result.get('personalization_reason', '')
                    }

                except Exception as e:

                    print(f"Adaptive AI failed: {e}, using random questions")

                    questions = Question.objects.filter(topic_id=topic_id)

                    selected_questions = random.sample(
                        list(questions),
                        min(num_questions, questions.count())
                    )

                    personalization_info = None

            else:

                questions = Question.objects.filter(topic_id=topic_id)

                selected_questions = random.sample(
                    list(questions),
                    min(num_questions, questions.count())
                )

                personalization_info = None

            serializer = QuestionForGameSerializer(selected_questions, many=True)

            return Response({
                "message": "Game session started",
                "session_id": game_session.id,
                "topic": topic.name,
                "questions": serializer.data,
                "personalization": personalization_info
            }, status=status.HTTP_201_CREATED)

        except StudentProfile.DoesNotExist:
            return Response({
                "error": "Student profile not found"
            }, status=status.HTTP_404_NOT_FOUND)

        except Topic.DoesNotExist:
            return Response({
                "error": "Topic not found"
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─────────────────────────────────────────
# SUBMIT ANSWER
# ─────────────────────────────────────────

class SubmitAnswerView(APIView):
    """
    Submit answer for a question in game session
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):

        session_id = request.data.get('session_id')
        question_id = request.data.get('question_id')
        student_answer = request.data.get('student_answer') or request.data.get('answer')
        time_taken = request.data.get('time_taken', 0)

        if not all([session_id, question_id, student_answer]):
            return Response({
                'error': 'session_id, question_id, and answer are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:

            game_session = GameSession.objects.get(id=session_id)
            question = Question.objects.get(id=question_id)

            is_correct = False

            if question.question_type == 'MCQ':
                correct_answer = question.answers.filter(is_correct=True).first()

                if correct_answer and correct_answer.answer_text.strip().lower() == student_answer.strip().lower():
                    is_correct = True

            response = StudentResponse.objects.create(
                game_session=game_session,
                question=question,
                student_answer=student_answer,
                is_correct=is_correct,
                time_taken=time_taken
            )

            game_session.questions_attempted += 1
            game_session.save()

            return Response({
                'is_correct': is_correct,
                'message': 'Answer submitted successfully',
                'response_id': response.id
            }, status=status.HTTP_201_CREATED)

        except GameSession.DoesNotExist:
            return Response({
                'error': 'Game session not found'
            }, status=status.HTTP_404_NOT_FOUND)

        except Question.DoesNotExist:
            return Response({
                'error': 'Question not found'
            }, status=status.HTTP_404_NOT_FOUND)


# ─────────────────────────────────────────
# END GAME SESSION
# ─────────────────────────────────────────

class EndGameSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            session_id   = request.data.get('session_id')
            total_score  = request.data.get('total_score', 0)
            status_value = request.data.get('status', 'COMPLETED')

            if not session_id:
                return Response({
                    'error': 'session_id is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            game_session             = GameSession.objects.get(
                id=session_id)
            game_session.status      = status_value
            game_session.session_end = timezone.now()
            game_session.save()

            # ✅ Use EXACT score from Unity — no recalculation!
            Score.objects.update_or_create(
                game_session=game_session,
                defaults={
                    'student':            game_session.student,
                    'total_score':        total_score,
                    'max_possible_score': 1000,
                    'percentage':         round(
                        (float(total_score) / 1000) * 100, 2)
                }
            )

            return Response({
                'message':     'Game session ended!',
                'total_score': total_score,
                'status':      status_value
            }, status=status.HTTP_200_OK)

        except GameSession.DoesNotExist:
            return Response({
                'error': 'Session not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─────────────────────────────────────────
# CURRENT TOPIC API (USED BY UNITY)
# ─────────────────────────────────────────

class GetCurrentTopicView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:

            profile = StudentProfile.objects.get(user=request.user)

            latest_session = GameSession.objects.filter(
                student=profile,
                status='IN_PROGRESS'
            ).order_by('-session_start').first()

            if not latest_session:
                return Response({
                    'topic': 'No topic selected',
                    'topic_id': None,
                    'subject': 'N/A',
                    'session_id': None
                })

            return Response({
                'topic': latest_session.topic.name,
                'topic_id': latest_session.topic.id,
                'subject': latest_session.subject.name,
                'session_id': latest_session.id
            })

        except StudentProfile.DoesNotExist:

            return Response({
                'error': 'Student profile not found'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:

            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class GameSessionDetailView(generics.RetrieveAPIView):
            permission_classes = [IsAuthenticated]
            serializer_class = GameSessionSerializer
            queryset = GameSession.objects.all()
            
class StudentScoresView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ScoreSerializer

    def get_queryset(self):
        profile = StudentProfile.objects.get(user=self.request.user)
        return Score.objects.filter(
            student=profile).order_by('-created_at')


class StudentProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = StudentProfile.objects.get(user=request.user)
            sessions = GameSession.objects.filter(student=profile)
            completed = sessions.filter(status='COMPLETED')
            scores = Score.objects.filter(student=profile)

            avg_score = 0
            if scores.exists():
                avg_score = sum(
                    float(s.percentage) for s in scores
                ) / scores.count()

            return Response({
                'total_sessions':     sessions.count(),
                'completed_sessions': completed.count(),
                'average_score':      round(avg_score, 2),
                'total_questions':    StudentResponse.objects.filter(
                    game_session__student=profile).count()
            }, status=status.HTTP_200_OK)

        except StudentProfile.DoesNotExist:
            return Response({
                'error': 'Profile not found'
            }, status=status.HTTP_404_NOT_FOUND)


class StudentFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        try:
            profile = StudentProfile.objects.get(user=request.user)
            game_session = GameSession.objects.get(
                id=session_id, student=profile)

            try:
                feedback = Feedback.objects.get(
                    game_session=game_session)
                return Response({
                    'session_id': session_id,
                    'feedback': {
                        'overall':         feedback.ai_feedback,
                        'strengths':       feedback.strengths,
                        'weaknesses':      feedback.weaknesses,
                        'recommendations': feedback.recommendations
                    }
                })
            except Feedback.DoesNotExist:
                return Response({
                    'error': 'No feedback found'
                }, status=status.HTTP_404_NOT_FOUND)

        except StudentProfile.DoesNotExist:
            return Response({
                'error': 'Profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except GameSession.DoesNotExist:
            return Response({
                'error': 'Session not found'
            }, status=status.HTTP_404_NOT_FOUND)
