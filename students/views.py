from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import StudentProfile
from .serializers import StudentProfileSerializer, StudentProfileCreateSerializer

from academics.models import Subject, StudentSubject
from academics.serializers import SubjectListSerializer, StudentSubjectSerializer


class StudentProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update student profile
    """
    permission_classes = [IsAuthenticated]
    serializer_class = StudentProfileSerializer

    def get_object(self):
        profile, created = StudentProfile.objects.get_or_create(user=self.request.user)
        return profile


class StudentProfileCreateView(generics.CreateAPIView):
    """
    Create student profile (board, grade, etc.)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = StudentProfileCreateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AvailableSubjectsView(APIView):
    """
    Get subjects available for student's board and grade
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = StudentProfile.objects.get(user=request.user)

            subjects = Subject.objects.filter(
                board=profile.board,
                grade=profile.grade,
                is_active=True
            )

            serializer = SubjectListSerializer(subjects, many=True)

            return Response(serializer.data)

        except StudentProfile.DoesNotExist:
            return Response(
                {'error': 'Please complete your profile first'},
                status=status.HTTP_400_BAD_REQUEST
            )


class EnrollSubjectView(APIView):
    """
    Enroll student in a subject
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            print("Enrollment request data:", request.data)
            print("User:", request.user)

            subject_id = request.data.get('subject_id')

            profile = StudentProfile.objects.get(user=request.user)
            subject = Subject.objects.get(id=subject_id)

            # Check if already enrolled
            enrollment, created = StudentSubject.objects.get_or_create(
                student=profile,
                subject=subject
            )

            if created:
                return Response({
                    'message': f'Successfully enrolled in {subject.name}',
                    'enrollment': StudentSubjectSerializer(enrollment).data
                }, status=status.HTTP_201_CREATED)

            else:
                return Response({
                    'message': 'Already enrolled in this subject',
                    'enrollment': StudentSubjectSerializer(enrollment).data
                })

        except StudentProfile.DoesNotExist:
            return Response({
                'error': 'Please complete your profile first'
            }, status=status.HTTP_400_BAD_REQUEST)

        except Subject.DoesNotExist:
            return Response({
                'error': 'Subject not found'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print("Enrollment error:", str(e))
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EnrolledSubjectsView(APIView):
    """
    Get all subjects student is enrolled in
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = StudentProfile.objects.get(user=request.user)

            enrollments = StudentSubject.objects.filter(
                student=profile,
                is_active=True
            )

            serializer = StudentSubjectSerializer(enrollments, many=True)

            return Response(serializer.data)

        except StudentProfile.DoesNotExist:
            return Response({
                'error': 'Please complete your profile first'
            }, status=status.HTTP_400_BAD_REQUEST)