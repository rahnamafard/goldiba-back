from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from core.models import User
from . import serializers

import logging
import secrets
import redis
import requests

logger = logging.getLogger(__name__)
register_user_redis = redis.StrictRedis()
reset_pass_redis = redis.StrictRedis()
sms_api_key = '6E52696C5047566E49714E6973446E5847747676316648664C7579797043434E2B6C5033365978302F72513D'
sms_api_url = "https://api.kavenegar.com/v1/{}/verify/lookup.json".format(sms_api_key)


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

            # Generate Verification Code
            verify_key = "{}{}{}{}".format(secrets.randbelow(10), secrets.randbelow(10), secrets.randbelow(10),
                                           secrets.randbelow(10))

            # Send Verification Code Via SMS for User
            sms_response = requests.get(sms_api_url, {
                "receptor": "09303267032",
                "token": verify_key,
                "template": "goldibaverify",
            })

            # API Call Successful
            if sms_response.ok:
                response_json = sms_response.json()

                # Response Status is 200
                if response_json.get('return').get('status') == 200:
                    # Save in Redis
                    try:
                        register_user_redis.set(mobile, verify_key)
                        register_user_redis.expire(mobile, 60)  # code expires in 60 seconds
                    except Exception as e:
                        logger.error(e)
                        return Response({
                            'type': 'error',
                            'status': 'برخی منابع سرور در دسترس نیست.'
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # Response Status is not 200
                else:
                    return JsonResponse({
                        'type': 'error',
                        'message': 'خطا از سوی سرویس پیامکی.'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            # API Call Failed
            else:
                return JsonResponse({
                    'type': 'error',
                    'message': 'سرویس ارسال پیامک در دسترس نیست.'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            # Everything is OK
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
            actual_verification_key = json_body['verification']
            mobile = json_body['mobile']

            # Check Verification key
            if register_user_redis.exists(mobile):
                expected_verification_key = register_user_redis.get(mobile).decode("utf-8")  # byto to string

                # It is not equal
                if expected_verification_key != actual_verification_key:
                    return JsonResponse({
                        'type': 'error',
                        'message': 'کد تایید معتبر نیست.'
                    }, status=status.HTTP_200_OK)

                # Confirmed
                return JsonResponse({
                    'type': 'ok',
                    'message': 'کد تایید اعتبارسنجی شد.'
                }, status=status.HTTP_200_OK)

            # Invalid Request
            else:
                return JsonResponse({
                    'type': 'error',
                    'message': 'کد منقضی شده است.'
                }, status=status.HTTP_400_BAD_REQUEST)

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
            serialized = serializers.CreateUserSerializer(data=request.data)
            if serialized.is_valid():
                mobile = serialized.data.get('mobile')
                first_name = serialized.data.get('first_name')
                last_name = serialized.data.get('last_name')
                password = serialized.data.get('password')
            else:
                return Response({
                    'type': 'error',
                    'message': 'درخواست نامعتبر'
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
                "message": "ثبت نام انجام شد."
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(e)
            return Response({
                'type': 'error',
                'status': 'خطا از سمت سرور.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutAPIVIew(APIView):
    @staticmethod
    def get(req):
        return Response({}, status=status.HTTP_200_OK)


class RequestResetPasswordCodeAPIView(APIView):
    @staticmethod
    def get(req):
        try:
            mobile = req.GET['mobile']

            # Generate Verification Code
            verify_key = "{}{}{}{}".format(secrets.randbelow(10), secrets.randbelow(10), secrets.randbelow(10),
                                           secrets.randbelow(10))

            # Send Verification Code Via SMS for User
            sms_response = requests.get(sms_api_url, {
                "receptor": mobile,
                "token": verify_key,
                "template": "goldibaverify",
            })

            # API Call Successful
            if sms_response.ok:
                response_json = sms_response.json()

                # Response Status is 200
                if response_json.get('return').get('status') == 200:
                    # Save in Redis
                    try:
                        reset_pass_redis.set(mobile, verify_key)
                        reset_pass_redis.expire(mobile, 60)  # code expires in 60 seconds
                    except Exception as e:
                        logger.error(e)
                        return Response({
                            'type': 'error',
                            'status': 'برخی منابع سرور در دسترس نیست.'
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # Response Status is not 200
                else:
                    return Response({
                        'type': 'error',
                        'message': 'خطا از سوی سرویس پیامکی.'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

                # Everything is OK
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


class VerifyResetPasswordCodeAPIView(APIView):
    @staticmethod
    def post(req):
        try:
            json_body = json.loads(req.body)
            actual_verification_key = json_body['verification']
            mobile = json_body['mobile']

            # Check Verification key
            if reset_pass_redis.exists(mobile):
                expected_verification_key = reset_pass_redis.get(mobile).decode("utf-8")  # byto to string

                # It is not equal
                if expected_verification_key != actual_verification_key:
                    return JsonResponse({
                        'type': 'error',
                        'message': 'کد تایید معتبر نیست.'
                    }, status=status.HTTP_200_OK)

                # Confirmed
                try:
                    user = User.objects.get(mobile=mobile)
                    first_name = user.first_name
                    last_name = user.last_name
                    return JsonResponse({
                        'type': 'ok',
                        'message': 'کد تایید اعتبارسنجی شد.',
                        'data': {
                            'user': {
                                'firstname': first_name,
                                'lastname': last_name,
                            }
                        }
                    }, status=status.HTTP_200_OK)

                # Mobile is not in database
                except Exception as e:
                    logger.error(e)
                    return JsonResponse({
                        'type': 'error',
                        'message': 'این شماره قبلا ثبت نشده.'
                    }, status=status.HTTP_400_BAD_REQUEST)



            # Invalid Request
            else:
                return JsonResponse({
                    'type': 'error',
                    'message': 'کد منقضی شده است.'
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(e)
            return Response({
                'type': 'error',
                'status': 'خطا از سمت سرور.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetPasswordAPIView(APIView):
    @staticmethod
    def post(request):
        try:
            serialized = serializers.ChangePasswordSerializer(data=request.data)
            if serialized.is_valid():
                mobile = serialized.data.get('mobile')
                password = serialized.data.get('password')
            else:
                return Response({
                    'type': 'error',
                    'message': 'درخواست نامعتبر'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get user and change its password
            user = User.objects.get(mobile=mobile)
            user.set_password(password)
            user.save()

            return Response({
                "type": "ok",
                "message": "رمز عبور تغییر کرد."
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(e)
            return Response({
                'type': 'error',
                'status': 'خطا از سمت سرور.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Override simple-jwt serializer (modifying default error messages)
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def update(self, instance, validated_data):
        pass

    default_error_messages = {
        'no_active_account': 'اطلاعات ورود اشتباه است.'
    }
    
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
