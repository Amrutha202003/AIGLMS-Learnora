from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from academics.models import Topic, Concept
from .models import Question, Answer
from games.models import GameSession, StudentResponse, Score
from ai_services.question_generator import AIQuestionGenerator
from django.utils import timezone
import random


class AIGenerateQuestionsView(APIView):
    """
    AI-powered question generation endpoint
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        concept_id    = request.data.get('concept_id')
        num_questions = request.data.get('num_questions', 5)

        if not concept_id:
            return Response({
                'error': 'concept_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            concept  = Concept.objects.get(id=concept_id)
            topic    = concept.topic
            subject  = topic.subject

            ai_generator = AIQuestionGenerator()

            result = ai_generator.generate_questions(
                topic_name      = topic.name,
                concept_name    = concept.name,
                subject_name    = subject.name,
                grade           = subject.grade,
                difficulty_level= topic.difficulty_level,
                num_questions   = num_questions
            )

            if not result['success']:
                return Response({
                    'error': result.get('error',
                        'Failed to generate questions')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            saved_questions = []

            for q_data in result['questions']:
                question = Question.objects.create(
                    topic            = topic,
                    concept          = concept,
                    question_text    = q_data['question_text'],
                    question_type    = 'MCQ',
                    difficulty_level = q_data.get(
                        'difficulty', topic.difficulty_level),
                    marks            = q_data.get('marks', 2),
                    created_by       = request.user
                )

                for option in q_data['options']:
                    Answer.objects.create(
                        question    = question,
                        answer_text = option['text'],
                        is_correct  = option['is_correct'],
                        explanation = q_data.get('explanation', '')
                    )

                saved_questions.append({
                    'id':            question.id,
                    'question_text': question.question_text,
                    'marks':         question.marks
                })

            return Response({
                'message':   f'Generated {len(saved_questions)} questions',
                'questions': saved_questions,
                'concept':   concept.name,
                'topic':     topic.name,
                'subject':   subject.name
            }, status=status.HTTP_201_CREATED)

        except Concept.DoesNotExist:
            return Response({
                'error': 'Concept not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BulkGenerateQuestionsView(APIView):
    """
    Generate questions for all concepts in a topic
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        topic_id             = request.data.get('topic_id')
        questions_per_concept = request.data.get(
            'questions_per_concept', 3)

        if not topic_id:
            return Response({
                'error': 'topic_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            topic    = Topic.objects.get(id=topic_id)
            concepts = Concept.objects.filter(topic=topic)

            if not concepts.exists():
                return Response({
                    'error': 'No concepts found for this topic'
                }, status=status.HTTP_404_NOT_FOUND)

            ai_generator    = AIQuestionGenerator()
            total_generated = 0
            results         = []

            for concept in concepts:
                result = ai_generator.generate_questions(
                    topic_name       = topic.name,
                    concept_name     = concept.name,
                    subject_name     = topic.subject.name,
                    grade            = topic.subject.grade,
                    difficulty_level = topic.difficulty_level,
                    num_questions    = questions_per_concept
                )

                if result['success']:
                    concept_questions = []

                    for q_data in result['questions']:
                        question = Question.objects.create(
                            topic            = topic,
                            concept          = concept,
                            question_text    = q_data['question_text'],
                            question_type    = 'MCQ',
                            difficulty_level = q_data.get(
                                'difficulty', topic.difficulty_level),
                            marks            = q_data.get('marks', 2),
                            created_by       = request.user
                        )

                        for option in q_data['options']:
                            Answer.objects.create(
                                question    = question,
                                answer_text = option['text'],
                                is_correct  = option['is_correct'],
                                explanation = q_data.get('explanation', '')
                            )

                        concept_questions.append(question.id)
                        total_generated += 1

                    results.append({
                        'concept':             concept.name,
                        'questions_generated': len(concept_questions),
                        'question_ids':        concept_questions
                    })

            return Response({
                'message':            f'Generated {total_generated} questions',
                'topic':              topic.name,
                'concepts_processed': len(results),
                'results':            results
            }, status=status.HTTP_201_CREATED)

        except Topic.DoesNotExist:
            return Response({
                'error': 'Topic not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetQuestionsForGameView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            topic_id      = request.query_params.get('topic_id')
            concept_id    = request.query_params.get('concept_id')
            difficulty    = request.query_params.get('difficulty', None)
            num_questions = int(request.query_params.get('num', 10))

            if concept_id:
                questions  = Question.objects.filter(
                    concept_id    = concept_id,
                    question_type = 'MCQ'
                )
                debug_name = f"concept {concept_id}"
            elif topic_id:
                questions  = Question.objects.filter(
                    topic_id      = topic_id,
                    question_type = 'MCQ'
                )
                debug_name = f"topic {topic_id}"
            else:
                return Response({
                    'error': 'topic_id or concept_id is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            if difficulty:
                questions = questions.filter(
                    difficulty_level=difficulty)

            questions = list(questions)
            random.shuffle(questions)
            questions = questions[:num_questions]

            if not questions:
                return Response({
                    'questions': [],
                    'total':     0,
                    'message':   f'No MCQ questions for {debug_name}'
                }, status=status.HTTP_200_OK)

            result = []
            for q in questions:
                answers     = Answer.objects.filter(question=q)
                answer_list = [{
                    'id':          a.id,
                    'answer_text': a.answer_text,
                    'is_correct':  a.is_correct
                } for a in answers]

                result.append({
                    'id':               q.id,
                    'question_text':    q.question_text,
                    'difficulty_level': q.difficulty_level,
                    'marks':            q.marks,
                    'answers':          answer_list
                })

            return Response({
                'questions': result,
                'total':     len(result)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubmitAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            session_id     = request.data.get('session_id')
            question_id    = request.data.get('question_id')
            student_answer = request.data.get('student_answer')
            is_correct     = request.data.get('is_correct', False)
            time_taken     = request.data.get('time_taken', 0)

            if not session_id or not question_id:
                return Response({
                    'error': 'session_id and question_id are required'
                }, status=status.HTTP_400_BAD_REQUEST)

            game_session = GameSession.objects.get(id=session_id)
            question     = Question.objects.get(id=question_id)

            StudentResponse.objects.create(
                game_session   = game_session,
                question       = question,
                student_answer = student_answer,
                is_correct     = is_correct,
                time_taken     = time_taken
            )

            game_session.questions_attempted += 1
            game_session.save()

            return Response({
                'message':    'Answer submitted!',
                'is_correct': is_correct
            }, status=status.HTTP_200_OK)

        except GameSession.DoesNotExist:
            return Response({
                'error': 'Game session not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

            # Save score
            max_possible = game_session.total_questions * 10
            percentage   = (float(total_score) /
                max(max_possible, 1)) * 100

            Score.objects.update_or_create(
                game_session=game_session,
                defaults={
                    'student':           game_session.student,
                    'total_score':       total_score,
                    'max_possible_score':max_possible,
                    'percentage':        round(percentage, 2)
                }
            )

            return Response({
                'message':     'Game session ended!',
                'total_score': total_score,
                'percentage':  round(percentage, 2),
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