import anthropic
import os
import json
from django.db.models import Avg, Count, Sum
from django.utils import timezone
from datetime import timedelta
from games.models import GameSession, StudentResponse, Score
from questions.models import Question
from academics.models import Topic, Concept
try:
    import google.generativeai as genai
except ImportError:
    import google.genai as genai
class AdaptiveLearningAI:
    """
    AI-powered adaptive learning system with detailed feedback
    """
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash') 
        api_key=os.getenv('ANTHROPIC_API_KEY')
    
    
    def analyze_student_performance(self, student_profile):
        """
        Deep analysis of student's performance with specific insights
        """
        completed_sessions = GameSession.objects.filter(
            student=student_profile,
            status='COMPLETED'
        )
        
        if not completed_sessions.exists():
            return {
                'performance_level': 'BEGINNER',
                'average_score': 0,
                'total_sessions': 0,
                'strong_topics': [],
                'weak_topics': [],
                'average_time_per_question': 0,
                'accuracy_trend': 'STABLE',
                'speed_analysis': 'NO_DATA',
                'recommendations': ['Start playing games to build your profile']
            }
        
        # Calculate metrics
        scores = Score.objects.filter(student=student_profile)
        avg_score = scores.aggregate(Avg('percentage'))['avg'] or 0
        
        # Analyze response times
        all_responses = StudentResponse.objects.filter(
            game_session__student=student_profile
        )
        
        if all_responses.exists():
            avg_time_result = responses.aggregate(Avg('time_taken'))
            avg_time = avg_time_result.get('time_taken__avg') or 0
            
            # Analyze accuracy vs speed
            fast_responses = all_responses.filter(time_taken__lt=10)  # < 10 seconds
            slow_responses = all_responses.filter(time_taken__gte=10)
            
            fast_accuracy = (fast_responses.filter(is_correct=True).count() / 
                           fast_responses.count() * 100) if fast_responses.exists() else 0
            slow_accuracy = (slow_responses.filter(is_correct=True).count() / 
                           slow_responses.count() * 100) if slow_responses.exists() else 0
            
            # Determine speed analysis
            if fast_accuracy > slow_accuracy + 10:
                speed_analysis = "RUSHING"  # Making mistakes when going fast
            elif slow_accuracy > fast_accuracy + 10:
                speed_analysis = "TOO_SLOW"  # Better when taking time
            else:
                speed_analysis = "BALANCED"
        else:
            avg_time = 0
            speed_analysis = "NO_DATA"
            fast_accuracy = 0
            slow_accuracy = 0
        
        # Topic-wise performance
        topic_performance = {}
        concept_performance = {}
        
        for session in completed_sessions:
            topic_id = session.topic.id
            topic_name = session.topic.name
            
            if topic_id not in topic_performance:
                topic_performance[topic_id] = {
                    'name': topic_name,
                    'sessions': 0,
                    'correct': 0,
                    'total': 0,
                    'avg_time': 0,
                    'times': []
                }
            
            responses = StudentResponse.objects.filter(game_session=session)
            correct = responses.filter(is_correct=True).count()
            total = responses.count()
            
            topic_performance[topic_id]['sessions'] += 1
            topic_performance[topic_id]['correct'] += correct
            topic_performance[topic_id]['total'] += total
            topic_performance[topic_id]['times'].extend(
                list(responses.values_list('time_taken', flat=True))
            )
            
            # Concept-wise analysis
            for response in responses:
                concept_id = response.question.concept.id
                concept_name = response.question.concept.name
                
                if concept_id not in concept_performance:
                    concept_performance[concept_id] = {
                        'name': concept_name,
                        'topic': topic_name,
                        'correct': 0,
                        'total': 0
                    }
                
                concept_performance[concept_id]['total'] += 1
                if response.is_correct:
                    concept_performance[concept_id]['correct'] += 1
        
        # Calculate percentages
        strong_topics = []
        weak_topics = []
        strong_concepts = []
        weak_concepts = []
        
        for topic_id, data in topic_performance.items():
            if data['total'] > 0:
                percentage = (data['correct'] / data['total']) * 100
                data['percentage'] = percentage
                
                if data['times']:
                    data['avg_time'] = sum(data['times']) / len(data['times'])
                
                if percentage >= 75:
                    strong_topics.append({
                        'topic_id': topic_id,
                        'name': data['name'],
                        'percentage': round(percentage, 2),
                        'avg_time': round(data['avg_time'], 1)
                    })
                elif percentage < 50:
                    weak_topics.append({
                        'topic_id': topic_id,
                        'name': data['name'],
                        'percentage': round(percentage, 2),
                        'avg_time': round(data['avg_time'], 1)
                    })
        
        for concept_id, data in concept_performance.items():
            if data['total'] > 0:
                percentage = (data['correct'] / data['total']) * 100
                
                if percentage >= 80:
                    strong_concepts.append({
                        'concept_id': concept_id,
                        'name': data['name'],
                        'topic': data['topic'],
                        'percentage': round(percentage, 2)
                    })
                elif percentage < 40:
                    weak_concepts.append({
                        'concept_id': concept_id,
                        'name': data['name'],
                        'topic': data['topic'],
                        'percentage': round(percentage, 2)
                    })
        
        # Analyze accuracy trend (last 5 sessions vs previous 5)
        recent_sessions = completed_sessions.order_by('-session_start')[:5]
        older_sessions = completed_sessions.order_by('-session_start')[5:10]
        
        if recent_sessions.exists() and older_sessions.exists():
            recent_avg = Score.objects.filter(
                game_session__in=recent_sessions
            ).aggregate(Avg('percentage'))['avg'] or 0
            
            older_avg = Score.objects.filter(
                game_session__in=older_sessions
            ).aggregate(Avg('percentage'))['avg'] or 0
            
            if recent_avg > older_avg + 5:
                accuracy_trend = "IMPROVING"
            elif recent_avg < older_avg - 5:
                accuracy_trend = "DECLINING"
            else:
                accuracy_trend = "STABLE"
        else:
            accuracy_trend = "INSUFFICIENT_DATA"
        
        # Determine performance level
        if avg_score >= 75:
            performance_level = 'ADVANCED'
        elif avg_score >= 50:
            performance_level = 'INTERMEDIATE'
        else:
            performance_level = 'BEGINNER'
        
        return {
            'performance_level': performance_level,
            'average_score': round(avg_score, 2),
            'total_sessions': completed_sessions.count(),
            'strong_topics': sorted(strong_topics, key=lambda x: x['percentage'], reverse=True),
            'weak_topics': sorted(weak_topics, key=lambda x: x['percentage']),
            'strong_concepts': sorted(strong_concepts, key=lambda x: x['percentage'], reverse=True)[:5],
            'weak_concepts': sorted(weak_concepts, key=lambda x: x['percentage'])[:5],
            'average_time_per_question': round(avg_time, 1),
            'accuracy_trend': accuracy_trend,
            'speed_analysis': speed_analysis,
            'fast_accuracy': round(fast_accuracy, 2),
            'slow_accuracy': round(slow_accuracy, 2),
            'topic_performance': topic_performance,
            'concept_performance': concept_performance
        }
    
    def generate_detailed_feedback(self, student_profile, game_session):
        """
        Generate highly specific, actionable feedback using Claude AI
        """
        # Get session data
        responses = StudentResponse.objects.filter(game_session=game_session)
        correct_count = responses.filter(is_correct=True).count()
        total_count = responses.count()
        
        if total_count == 0:
            return {
                'success': False,
                'error': 'No responses found for this session'
            }
        
        percentage = (correct_count / total_count) * 100
        avg_time = responses.aggregate(Avg('time_taken'))['avg'] or 0
        
        # Get overall analysis
        analysis = self.analyze_student_performance(student_profile)
        
        # Prepare detailed response data
        incorrect_details = []
        for response in responses.filter(is_correct=False):
            question = response.question
            correct_answer = question.answers.filter(is_correct=True).first()
            
            incorrect_details.append({
                'question': question.question_text,
                'student_answer': response.student_answer,
                'correct_answer': correct_answer.answer_text if correct_answer else 'N/A',
                'topic': question.topic.name,
                'concept': question.concept.name,
                'difficulty': question.difficulty_level,
                'time_taken': response.time_taken
            })
        
        correct_details = []
        for response in responses.filter(is_correct=True):
            correct_details.append({
                'concept': response.question.concept.name,
                'difficulty': response.question.difficulty_level,
                'time_taken': response.time_taken
            })
        
        # Create comprehensive AI prompt
        prompt = f"""You are an expert educational AI tutor. Provide HIGHLY SPECIFIC and ACTIONABLE feedback for this student.

STUDENT PROFILE:
- Name: {student_profile.full_name}
- Grade: {student_profile.grade}
- Board: {student_profile.board}
- Overall Level: {analysis['performance_level']}
- Overall Average: {analysis['average_score']:.1f}%
- Accuracy Trend: {analysis['accuracy_trend']}
- Speed Analysis: {analysis['speed_analysis']}

CURRENT SESSION PERFORMANCE:
- Topic: {game_session.topic.name}
- Subject: {game_session.subject.name}
- Score: {correct_count}/{total_count} ({percentage:.1f}%)
- Average Time per Question: {avg_time:.1f} seconds

STRONG AREAS:
{json.dumps(analysis['strong_topics'][:3], indent=2)}

WEAK AREAS:
{json.dumps(analysis['weak_topics'][:3], indent=2)}

CONCEPTS MASTERED:
{json.dumps(analysis['strong_concepts'][:3], indent=2)}

CONCEPTS NEEDING WORK:
{json.dumps(analysis['weak_concepts'][:3], indent=2)}

INCORRECT ANSWERS (with details):
{json.dumps(incorrect_details[:5], indent=2)}

CORRECT ANSWERS PATTERN:
{json.dumps(correct_details[:3], indent=2)}

SPEED METRICS:
- Fast answers (< 10s) accuracy: {analysis['fast_accuracy']:.1f}%
- Slow answers (≥ 10s) accuracy: {analysis['slow_accuracy']:.1f}%

Provide feedback in JSON format:
{{
    "overall_assessment": "2-3 sentences about current performance with specific numbers",
    "strengths": [
        "Specific strength with example: 'Excellent accuracy (85%) on Algebra problems'",
        "Another specific strength with data"
    ],
    "weaknesses": [
        "Specific weakness: 'Struggling with Geometry (40% accuracy) - particularly with angle calculations'",
        "Another specific weakness with concept names"
    ],
    "speed_feedback": "Specific advice about speed vs accuracy balance with numbers",
    "concept_specific_advice": [
        {{
            "concept": "Concept name",
            "issue": "Specific problem observed",
            "solution": "Exact steps to improve",
            "practice_tip": "Specific practice recommendation"
        }}
    ],
    "immediate_actions": [
        "Action 1: Practice [specific concept] using [specific method] for [specific duration]",
        "Action 2: Review [specific topic] focusing on [specific aspect]",
        "Action 3: Complete [specific number] practice questions on [specific concept]"
    ],
    "study_plan": {{
        "today": "Specific task for today",
        "this_week": "Specific goals for this week",
        "practice_schedule": "Recommended practice frequency"
    }},
    "motivational_message": "Personalized, encouraging message mentioning specific achievements",
    "difficulty_recommendation": "Should student try EASIER, SAME, or HARDER difficulty next time? Why?",
    "estimated_improvement_time": "Realistic estimate: 'With daily practice, expect 15-20% improvement in 2 weeks'",
    "red_flags": ["Any concerning patterns like: rushing, consistently missing concept X, time management issues"]
}}

BE ULTRA-SPECIFIC. Use actual concept names, percentages, time data. Avoid generic advice. Make it actionable and personalized for grade {student_profile.grade}."""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            feedback_data = json.loads(response_text)
            
            return {
                'success': True,
                'feedback': feedback_data,
                'session_score': percentage,
                'performance_level': analysis['performance_level'],
                'analysis_summary': {
                    'accuracy_trend': analysis['accuracy_trend'],
                    'speed_analysis': analysis['speed_analysis'],
                    'average_time': avg_time
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_adaptive_questions(self, student_profile, topic, num_questions=10):
        """
        Get personalized question set based on comprehensive analysis
        """
        analysis = self.analyze_student_performance(student_profile)
        performance_level = analysis['performance_level']
        weak_concepts = analysis['weak_concepts']
        
        # Adjust difficulty based on trend
        if analysis['accuracy_trend'] == 'IMPROVING':
            # Student is improving - challenge them more
            if performance_level == 'BEGINNER':
                difficulty_mix = {'EASY': 4, 'MEDIUM': 5, 'HARD': 1}
            elif performance_level == 'INTERMEDIATE':
                difficulty_mix = {'EASY': 2, 'MEDIUM': 4, 'HARD': 4}
            else:  # ADVANCED
                difficulty_mix = {'EASY': 1, 'MEDIUM': 3, 'HARD': 6}
                
        elif analysis['accuracy_trend'] == 'DECLINING':
            # Student struggling - make it easier
            if performance_level == 'ADVANCED':
                difficulty_mix = {'EASY': 2, 'MEDIUM': 5, 'HARD': 3}
            elif performance_level == 'INTERMEDIATE':
                difficulty_mix = {'EASY': 4, 'MEDIUM': 4, 'HARD': 2}
            else:  # BEGINNER
                difficulty_mix = {'EASY': 7, 'MEDIUM': 2, 'HARD': 1}
        else:
            # Standard mix
            if performance_level == 'ADVANCED':
                difficulty_mix = {'EASY': 1, 'MEDIUM': 2, 'HARD': 7}
            elif performance_level == 'INTERMEDIATE':
                difficulty_mix = {'EASY': 3, 'MEDIUM': 4, 'HARD': 3}
            else:  # BEGINNER
                difficulty_mix = {'EASY': 6, 'MEDIUM': 3, 'HARD': 1}
        
        selected_questions = []
        
        # Prioritize weak concepts (30% of questions)
        if weak_concepts:
            weak_concept_ids = [c['concept_id'] for c in weak_concepts[:2]]
            weak_questions = Question.objects.filter(
                topic=topic,
                concept_id__in=weak_concept_ids
            ).order_by('?')[:int(num_questions * 0.3)]
            selected_questions.extend(weak_questions)
        
        # Fill remaining with difficulty mix
        remaining = num_questions - len(selected_questions)
        exclude_ids = [q.id for q in selected_questions]
        
        for difficulty, count in difficulty_mix.items():
            if count > 0 and remaining > 0:
                take = min(count, remaining)
                questions = Question.objects.filter(
                    topic=topic,
                    difficulty_level=difficulty
                ).exclude(
                    id__in=exclude_ids
                ).order_by('?')[:take]
                
                selected_questions.extend(questions)
                exclude_ids.extend([q.id for q in questions])
                remaining -= len(questions)
        
        return {
            'questions': selected_questions[:num_questions],
            'difficulty_mix': difficulty_mix,
            'performance_level': performance_level,
            'personalization_reason': self._get_detailed_reason(
                performance_level, 
                analysis['accuracy_trend'],
                analysis['average_score']
            ),
            'weak_concepts_targeted': len([q for q in selected_questions if q.concept_id in [c['concept_id'] for c in weak_concepts[:2]]]) if weak_concepts else 0
        }
    
    def _get_detailed_reason(self, performance_level, trend, avg_score):
        """
        Generate detailed explanation for question selection
        """
        reasons = []
        
        if performance_level == 'ADVANCED':
            reasons.append(f"You're performing excellently ({avg_score:.1f}% average)!")
        elif performance_level == 'INTERMEDIATE':
            reasons.append(f"You're making good progress ({avg_score:.1f}% average).")
        else:
            reasons.append(f"Building your foundation (currently {avg_score:.1f}%).")
        
        if trend == 'IMPROVING':
            reasons.append("Since you're improving, we're adding more challenging questions.")
        elif trend == 'DECLINING':
            reasons.append("We're adjusting difficulty to help rebuild your confidence.")
        
        reasons.append("Questions target your weak concepts to maximize improvement.")
        
        return " ".join(reasons)