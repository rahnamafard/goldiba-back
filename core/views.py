from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework.response import Response

from core.models import User
from core.serializers import UserSerializer
from . import serializers


# LOGGING
import logging
logger = logging.getLogger(__name__)


class RequestVerificationCodeAPIView(APIView):
    @staticmethod
    def post(request):
        try:
            json_body = json.loads(request.body)
            mobile = json_body['mobile']

            if User.objects.filter(mobile=mobile).exclude(pk=request.user.pk).exists():
                return Response({
                    'type': 'error',
                    'message': 'این شماره قبلا ثبت شده.'
                }, status=status.HTTP_406_NOT_ACCEPTABLE)

            # TODO Generate & Send SMS for VERIFICATION_CODE & Save it together with mobile-number anywhere

            return JsonResponse({
                'type': 'ok',
                'message': 'کد تایید پیامک شد.'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(e)
            return Response({
                'type': 'error',
                'status': 'خطا از سمت سرور.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyMobileNumberAPIView(APIView):
    @staticmethod
    def post(request):
        try:
            json_body = json.loads(request.body)
            verification_code = json_body['verification']

            # TODO Check verification code

            if verification_code != '1234':
                return JsonResponse({
                    'type': 'error',
                    'message': 'کد تایید معتبر نیست.'
                }, status=status.HTTP_200_OK)

            # TODO Create User

            return JsonResponse({
                'type': 'ok',
                'message': 'کد تایید اعتبارسنجی شد.'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(e)
            return Response({
                'type': 'error',
                'status': 'خطا از سمت سرور.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateUserAPIView(APIView):
    @staticmethod
    def post(request):
        try:
            serialized = serializers.UserSerializer(data=request.data)
            if serialized.is_valid():
                mobile = serialized.data.get('mobile')
                first_name = serialized.data.get('first_name')
                last_name = serialized.data.get('last_name')
                password = serialized.data.get('password')
            else:
                return Response({
                    'type': 'error',
                    'message': 'Bad Request.'
                }, status=status.HTTP_400_BAD_REQUEST)

            new_user = User()
            new_user.mobile = mobile
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.set_password(password)
            new_user.is_superuser = 0
            new_user.is_active = 1
            new_user.is_staff = 0
            new_user.email_subscription = 0
            new_user.sms_subscription = 0
            new_user.save()

            return Response({
                "type": "ok",
                "message": "ثبث نام انجام شد."
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(e)
            return Response({
                'type': 'error',
                'status': 'خطا از سمت سرور.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class UserCreate(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = (AllowAny, )
#
#     def create(self, request, *args, **kwargs):
#         serializer_class = self.get_serializer(data=request.data)
#
#         if not serializer_class.is_valid() :
#             return JsonResponse({"type": "error", "message": "خطا (تکمیل شود)"}, status=status.HTTP_400_BAD_REQUEST)
#
#         self.perform_create(serializer_class)
#         # headers = self.get_success_headers(serializer_class.data)
#         return JsonResponse({"type": "ok", "message": "موفقیت آمیز بود."}, status=status.HTTP_201_CREATED)

