try:
    import google.generativeai as genai
except ImportError:
    import google.genai as genai
import os
import json

class AIQuestionGenerator:
    """
    AI-powered question generator using Google Gemini
    """
    
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise Exception("GOOGLE_API_KEY not found")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')  # ✅ NEW (Free & Fast)
    
    def generate_questions(self, topic_name, concept_name, subject_name, grade, difficulty_level, num_questions=5):
        """
        Generate questions using Gemini
        """
        prompt = f"""Generate {num_questions} multiple choice questions.

Subject: {subject_name}, Grade: {grade}
Topic: {topic_name}, Concept: {concept_name}
Difficulty: {difficulty_level}

Return ONLY this JSON format (no markdown):
[
  {{
    "question_text": "Question?",
    "difficulty": "{difficulty_level}",
    "marks": 2,
    "options": [
      {{"text": "A", "is_correct": false}},
      {{"text": "B", "is_correct": true}},
      {{"text": "C", "is_correct": false}},
      {{"text": "D", "is_correct": false}}
    ],
    "explanation": "Why B is correct"
  }}
]"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Clean markdown
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            questions = json.loads(response_text.strip())
            
            return {
                'success': True,
                'questions': questions,
                'count': len(questions)
            }
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'questions': []
            }
    
    def generate_question_for_concept(self, concept_id):
        """
        Generate questions for a concept
        """
        from academics.models import Concept
        
        try:
            concept = Concept.objects.get(id=concept_id)
            topic = concept.topic
            subject = topic.subject
            
            return self.generate_questions(
                topic_name=topic.name,
                concept_name=concept.name,
                subject_name=subject.name,
                grade=subject.grade,
                difficulty_level=topic.difficulty_level,
                num_questions=5
            )
            
        except Concept.DoesNotExist:
            return {
                'success': False,
                'error': 'Concept not found',
                'questions': []
            }