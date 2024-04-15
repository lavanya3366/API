from itertools import count
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from rest_framework import status
from django.contrib import messages
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from django.db.models import Count
from exam.serializers.editcourseserializers import EditCourseInstanceSerializer, NotificationSerializer
from exam.models.allmodels import (
    ActivityLog,
    Course,
    CourseCompletionStatusPerUser,
    Notification,
    QuizScore,
    UploadVideo,
    UploadReadingMaterial,
    CourseStructure,
    CourseRegisterRecord,
    CourseEnrollment,
    Progress,
    Quiz,
    Question,
    QuizAttemptHistory
    
)
from exam.models.coremodels import Customer, User
from rest_framework.exceptions import NotFound, ValidationError

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
# from exam.models.coremodels import *
from exam.serializers.createcourseserializers import (
    ActivateCourseSerializer,
    CourseSerializer, 
    CourseStructureSerializer,
    CreateChoiceSerializer,
    InActivateCourseSerializer, 
    UploadReadingMaterialSerializer, 
    UploadVideoSerializer, 
    QuizSerializer, 
    CreateCourseSerializer,
    CreateUploadReadingMaterialSerializer,
    CreateUploadVideoSerializer,
    CreateQuizSerializer,
    CreateQuestionSerializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.db.models import Count
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.views import APIView
from rest_framework.response import Response

import pandas as pd
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from custom_authentication.custom_mixins import ClientAdminMixin

import json

# =================================================================
# employee dashboard
# =================================================================

class CreateCourseCompletionStatusPerUserView(APIView):
    """
        allowed for client admin
        POST request
        triggered after course enrollment records creation , similar to that one.
                in request body :
                        list of course_id =[..., ..., ..., ...]
                        list of user_id =[..., ..., ..., ...]
                        each course in list will be mapped for all users in list
        while creating instance :
            enrolled_user = request body
            course = request body
            completion_status = (default=False)
            in_progress_status = (default=False)
            created_at = (auto_now_add=True)
    """
    pass

class CreateQuizScoreView(APIView):
    """
        allowed for client admin
        POST request
        triggered after course enrollment records creation , similar to that one.
                in request body :
                        list of course_id =[..., ..., ..., ...]
                        list of user_id =[..., ..., ..., ...]
                        each course in list will be mapped for all users in list
        while creating instance :
            enrolled_user = request body
            course = request body
            total_quizzes_per_course = calculate in view for course by counting active quizzes in it
            completed_quiz_count = by default 0
            total_score_per_course = (default=0)
    """
    pass

class UpdateCompleteQuizCountView(APIView):
    """
        POST request
        triggered when quiz attempt history for that course, that user have completed =true , if set of quiz, course, user doesn't already have completed = true in table
        while updating instance :
            completed_quiz_count = increment by 1
    """
    pass

class UpdateTotalScorePerCourseView(APIView):
    """
        POST request
        triggered when quiz attempt history for that course, that user have completed =true 
        while updating instance :
            total_score_per_course -> calculate for it 
    """
    pass

class UpdateCourseCompletionStatusPerUserView(APIView):
    """
        POST request
        triggers when 
        total_quizzes_per_course = completed_quiz_count in quiz score for that user in request
        if total_quizzes_per_course == completed_quiz_count:
            completion_status=True and in_progress_status =False
        if total_quizzes_per_course > completed_quiz_count:
            completion_status=False and in_progress_status =True
    """
    pass

class DisplayClientCourseProgressView(APIView):
    """
        GET request
        for user in request, if he have data in course enrollment table
        
        display if user in request have active enrollment for the course
        display:
            completed_quiz_count
    """
    pass

class DisplayClientCourseCompletionStatusView(APIView):
    """
        GET request
        for user in request, if he have data in course enrollment table(active)
        display:
            completion_status or in_progress_status = Based on which is true for the user for thi course
    """
    pass

class CountOfAssignedCoursesView(APIView):
    """
    GET request
    for user in request , count the number of active enrollments he have in course enrollment table
    """
    pass

class CountClientCompletedCourseView(APIView):
    """
        GET request
        for the user filter the CourseCompletionStatusPerUser table
        and count courses for which completion_status= True and in_progress_status = False as completed courses
        and count courses for which completion_status= False and in_progress_status = True as completed courses
    """
    pass

# =================================================================
# employer dashboard
# =================================================================


class ActiveEnrolledUserCountPerCustomerView(ClientAdminMixin, APIView):
    """
    Get API for client admin to count active enrolled users per customer ID.
    """

    def get(self, request):
        try:
            # Extract user information from headers
            user_header = request.headers.get("user")
            if user_header:
                user = json.loads(user_header)
                role_id = user.get("role")
            else:
                # Handle case where user information is not provided
                return JsonResponse({"error": "User information not provided"}, status=400)

            # Check if the user has client admin privileges
            if not self.has_client_admin_privileges(request):
                return JsonResponse({"error": "You do not have permission to access this resource"}, status=403)

            # Retrieve the customer ID from the request query parameters
            customer_id = request.query_params.get('customer_id')

            # Check if customer_id is provided
            if customer_id is None:
                return JsonResponse({"error": "Customer ID is required"}, status=400)

            # Query the User model to count the number of users for the given customer ID
            user_count = User.objects.filter(customer_id=customer_id,status='active').count()

            # Return the count in the response
            return JsonResponse({"user_count": user_count}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class RegisteredCourseCountView(ClientAdminMixin,APIView):
    """
    Get API for client admin to count registered courses per customer ID.
    """

    def get(self, request):
        try:
            user_header = request.headers.get("user")
            if user_header:
                user = json.loads(user_header)
                role_id = user.get("role")
            else:
                # Handle case where user information is not provided
                return JsonResponse({"error": "User information not provided"}, status=400)

            # Check if the user has client admin privileges
            if not self.has_client_admin_privileges(request):
                return JsonResponse({"error": "You do not have permission to access this resource"}, status=403)
            # Extract customer ID from request query parameters
            customer_id = request.query_params.get('customer_id')

            if customer_id is None:
                raise ValueError("Customer ID not provided in request data")

            # Check if the customer exists in the database
            customer_exists = Customer.objects.filter(id=customer_id).exists()

            if not customer_exists:
                raise CourseRegisterRecord.DoesNotExist("Customer does not exist")

            # Grouping course registrations by customer and counting the number of registrations per customer
            registered_course_counts = CourseRegisterRecord.objects.filter(customer__id=customer_id).values('course').distinct().count()
            
            # Constructing response data
            response_data = {
                'customer_id': customer_id,
                'course_count': registered_course_counts
            }
            
            # Return response data
            return Response(response_data)

        except (CourseRegisterRecord.DoesNotExist, ValueError) as e:
            if isinstance(e, CourseRegisterRecord.DoesNotExist):
                status_code = 404
            else:
                status_code = 400

            error_message = str(e)
            return Response({'error': error_message}, status=status_code)



#---------
# graph : (per course)(for a customer) [employeer (client admin) dashboard]
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from django.core.exceptions import ObjectDoesNotExist
# class CountOfCompletionPerRegisteredCourseView(APIView):  #this
#     """
#     API endpoint to get the completion count of each registered course per user count.
#     """

#     def get(self, request):
#         try:
#             # Fetch all registered courses
#             registered_courses = CourseEnrollment.objects.all().values_list('course_id', flat=True).distinct()

#             completion_data = []

#             # Iterate over each registered course
#             for course_id in registered_courses:
#                 # Count the number of users enrolled in the course
#                 user_count = CourseCompletionStatusPerUser.objects.filter(course_id=course_id, completion_status=True).count()
#                 completion_data.append({
#                     'course_id': course_id,
#                     'user_count': user_count,
#                 })

#             return Response(completion_data)
#         except ObjectDoesNotExist:
#             return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# class CountOfInProgressPerRegisteredCourseView(APIView):  #this
#     """
#     API endpoint to get the count of users in progress for each registered course.
#     """

#     def get(self, request):
#         try:
#             # Fetch all registered courses
#             registered_courses = CourseEnrollment.objects.all().values_list('course_id', flat=True).distinct()

#             in_progress_data = []

#             # Iterate over each registered course
#             for course_id in registered_courses:
#                 # Count the number of users enrolled in the course and in progress
#                 user_count = CourseCompletionStatusPerUser.objects.filter(course_id=course_id, in_progress_status=True).count()

#                 # Append course data to the in_progress_data list
#                 in_progress_data.append({
#                     'course_id': course_id,
#                     'user_count': user_count,
#                 })

#             return Response(in_progress_data)
#         except ObjectDoesNotExist:
#             return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# from rest_framework.views import APIView
# from rest_framework.response import Response
# class CountOfNotStartedPerRegisteredCourseView(APIView):  #this
#     """
#     API endpoint to get the count of users who have not started each registered course.
#     """

#     def get(self, request, format=None):
#         try:
#             # Query the CourseCompletionStatusPerUser table to count the number of users
#             # who have not started each registered course
#             not_started_counts = CourseCompletionStatusPerUser.objects.filter(
#                 completion_status=False, in_progress_status=False
#             ).values('course_id').annotate(count=Count('id'))

#             # Format the response data
#             response_data = [{'course_id': item['course_id'], 'count': item['count']} for item in not_started_counts]

#             return Response(response_data)
#         except ObjectDoesNotExist:
#             return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProgressCountView(ClientAdminMixin,APIView):
    """
    API endpoint to get the count of users in different progress states for each registered course.
    """

    def get(self, request):
        try:
            user_header = request.headers.get("user")
            if user_header:
                user = json.loads(user_header)
                role_id = user.get("role")
            else:
                # Handle case where user information is not provided
                return JsonResponse({"error": "User information not provided"}, status=400)

            # Check if the user has client admin privileges
            if not self.has_client_admin_privileges(request):
                return JsonResponse({"error": "You do not have permission to access this resource"}, status=403)
            # Fetch all registered courses
            registered_courses = CourseCompletionStatusPerUser.objects.all().values_list('course_id', flat=True).distinct()

            progress_data = []

            # Iterate over each registered course
            for course_id in registered_courses:
                # Count the number of users in different progress states for each course
                completion_count = CourseCompletionStatusPerUser.objects.filter(
                    course_id=course_id, completion_status=True
                ).count()
                in_progress_count = CourseCompletionStatusPerUser.objects.filter(
                    course_id=course_id, in_progress_status=True, completion_status=False
                ).count()
                not_started_count = CourseCompletionStatusPerUser.objects.filter(
                    course_id=course_id, completion_status=False, in_progress_status=False
                ).count()

                # Append course progress data to the progress_data list
                progress_data.append({
                    'course_id': course_id,
                    'completion_count': completion_count,
                    'in_progress_count': in_progress_count,
                    'not_started_count': not_started_count,
                })

            return Response(progress_data)
        except (ObjectDoesNotExist, Exception) as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#---------

# =================================================================
# super admin dashboard
# =================================================================

class ActiveCourseCountView(APIView):
    """get api
    for super admin
    """
    pass

class InActiveCourseCountView(APIView):
    """get api
    for super admin
    """
    pass

class ActiveRegisteredCustomerCountView(APIView):
    """get api
    for super admin
    """
    pass

# ----
# graph : (only per course) [ (super admin) dashboard]

class CountOfCompletionPerCourseView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    pass

class CountOfInProgressPerCourseView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    pass

class CountOfNotStartedPerCourseView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    pass
# ----

# graph to count registrations per course 
class CountOfActiveRegistrationPerCoure(APIView):
    pass

def dashboard_view(request):
    return render(request, 'employer.html')
