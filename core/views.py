from datetime import datetime
from django.shortcuts import redirect
from django.utils import dateparse, timezone
from rest_framework import generics, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated, IsAdminUser
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token

from core.serializers import *
from . import serializers

import logging
import secrets
import redis
import requests

logger = logging.getLogger(__name__)
register_user_redis = redis.StrictRedis()
reset_pass_redis = redis.StrictRedis()
empty_list = [None, '', 'null']

# kavenegar
# sms_api_key = '6E52696C5047566E49714E6973446E5847747676316648664C7579797043434E2B6C5033365978302F72513D' # arahnamafard@yahoo.com
sms_api_key = '6369352B674A66434345645633586A70352F4674414A61347565557142424A6A6A313053456B76413030673D' # nourifatemeh441@gmail.com
sms_api_url = "https://api.kavenegar.com/v1/{}/verify/lookup.json".format(sms_api_key)

# zibal
zibal_request_url = 'https://gateway.zibal.ir/v1/request'  # post
zibal_verify_url = 'https://gateway.zibal.ir/v1/verify'  # post
merchant_key = '5f81b70318f93473c1e674c9'

def is_json(json_data):
    try:
        real_json=json.loads(json_data)
        is_valid=True
    except ValueError:
        is_valid=False
    return is_valid


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
                # "receptor": mobile,
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
                expected_verification_key = register_user_redis.get(mobile).decode("utf-8")  # byte to string

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

            Token.objects.create(user=new_user)

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
                # "receptor": mobile,
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
                'message': 'خطا از سمت سرور.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Note:
# If you use TokenAuthentication in production
# you must ensure that your API is only available over https.
class LoginAPIView(APIView):
    @staticmethod
    def post(req):
        try:
            json_body = json.loads(req.body)

            user = authenticate(mobile=json_body['mobile'], password=json_body['password'])
            if user is not None:
                try:
                    token = Token.objects.get(user_id=user.user_id)
                except Exception as e:
                    token = Token.objects.create(user=user)

                return Response({
                    "type": "ok",
                    "message": "ورود موفقیت آمیز.",
                    "token": token.key,
                }, status=status.HTTP_200_OK)

            else:
                return Response({
                    "type": "error",
                    "message": "اطلاعات ورود اشتباه است."
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(e)
            return Response({
                'type': 'error',
                'message': 'خطا از سمت سرور.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutAPIVIew(APIView):
    @staticmethod
    def get(req):
        return Response({}, status=status.HTTP_200_OK)


class UserMetaDataAPIVIew(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        serialized_user = UserProfileSerializer(user).data
        serialized_user['permissions'] = user.get_all_permissions()
        return Response({'user': serialized_user})


class NewProductFormInfoAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser,)

    @staticmethod
    def get(req):
        try:
            statuses = Status.objects.all()
            status_serializer = StatusSerializer(statuses, many=True)

            brands = Brand.objects.all()
            brand_serializer = BrandSerializer(brands, many=True)

            # tags = Tag.objects.all()
            # tag_serializer = TagSerializer(tags, many=True)

            colors = Color.objects.all()
            color_serializer = ColorSerializer(colors, many=True)

            categories = Category.objects.all()
            category_serializer = CategoryBase64Serializer(categories, many=True)

            return Response({
                "type": "ok",
                "body": {
                    "statuses": status_serializer.data,
                    "brands": brand_serializer.data,
                    # "tags": tag_serializer.data,
                    "colors": color_serializer.data,
                    "categories": category_serializer.data
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "type": "error",
                "message": "خطا در ارتباط با پایگاه داده."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# POSSIBLY NOT CORRECT, SO CHECK IT
# class CreateTagIfNotExists(APIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated, IsAdminUser)
#
#     @staticmethod
#     def post(req):
#         try:
#             json_tags = json.loads(req.body)
#
#             new_tags = []
#             for tag in json_tags:
#                 print(tag)
#                 new_tag = Tag.objects.get_or_create(tag)
#                 new_tags.append(new_tag)
#
#             return Response({
#                 "type": "ok",
#                 "tags": new_tags
#             }, status=status.HTTP_200_OK)
#
#         except Exception as e:
#             logger.error(e)
#             return Response({
#                 "type": "error",
#                 "message": "خطا از سمت سرور."
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductAPIView(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.ListAPIView
):

    # Change serializer upon request method -> (self.request.method == "GET")
    def get_serializer_class(self):
        return ProductSerializer

    def get_permissions(self):
        permission_classes = []
        # if self.request.method == "POST":
        #     permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Product.objects.all()

        product_id = self.request.query_params.get('id', None)
        if product_id not in empty_list:
            queryset = queryset.filter(product_id=product_id)

        category = self.request.query_params.get('category', None)
        if category not in empty_list:
            queryset = queryset.filter(categories__category_id__exact=category)

        return queryset

    # Get object by id
    # def get_object(self):
    #     request = self.request
    #     passed_id = request.GET.get('id', None) or self.passed_id
    #     queryset = self.queryset
    #     obj = None
    #     if passed_id is not None:
    #         obj = get_object_or_404(queryset, pk=passed_id)
    #         self.check_object_permissions(request, obj)
    #     return obj

    # Get object
    # def get(self, request, *args, **kwargs):
    #     url_passed_id = request.GET.get('id')
    #
    #     json_data = {}
    #     body_ = request.body
    #
    #     if is_json(body_):
    #         json_data = json.loads(request.body)
    #
    #     new_passed_id = json_data.get('id', None)
    #
    #     passed_id = url_passed_id or new_passed_id or None
    #     # self.passed_id = passed_id
    #
    #     if passed_id is not None:
    #         return self.retrieve(request, *args, **kwargs)
    #
    #     return super().get(request, *args, **kwargs)

    # create a new object
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    # update an existing object
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    # delete an existing object
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ModelAPIView(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.ListAPIView
):
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Model.objects.all()
    # parser_classes = [MultiPartParser]

    # Change serializer upon request method -> (self.request.method == "GET")
    def get_serializer_class(self):
        return ModelSerializer

    # Get object by id
    def get_object(self):
        request = self.request
        passed_id = request.GET.get('id', None) or self.passed_id
        queryset = self.queryset
        obj = None
        if passed_id is not None:
            obj = get_object_or_404(queryset, pk=passed_id)
            self.check_object_permissions(request, obj)
        return obj

    # Get object
    def get(self, request, *args, **kwargs):
        url_passed_id = request.GET.get('id')

        json_data = {}
        body_ = request.body

        if is_json(body_):
            json_data = json.loads(request.body)

        new_passed_id = json_data.get('id', None)

        passed_id = url_passed_id or new_passed_id or None
        # self.passed_id = passed_id

        if passed_id is not None:
            return self.retrieve(request, *args, **kwargs)

        return super().get(request, *args, **kwargs)

    # create a new object
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    # update an existing object
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    # delete an existing object
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ColorAPIView(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.ListAPIView
):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = Color.objects.all()
    # parser_classes = [MultiPartParser]

    # Change serializer upon request method -> (self.request.method == "GET")
    def get_serializer_class(self):
        return ColorSerializer

    # Get object by id
    def get_object(self):
        request = self.request
        passed_id = request.GET.get('id', None) or self.passed_id
        queryset = self.queryset
        obj = None
        if passed_id is not None:
            obj = get_object_or_404(queryset, pk=passed_id)
            self.check_object_permissions(request, obj)
        return obj

    # Get object
    def get(self, request, *args, **kwargs):
        url_passed_id = request.GET.get('id')

        json_data = {}
        body_ = request.body

        if is_json(body_):
            json_data = json.loads(request.body)

        new_passed_id = json_data.get('id', None)

        passed_id = url_passed_id or new_passed_id or None
        # self.passed_id = passed_id

        if passed_id is not None:
            return self.retrieve(request, *args, **kwargs)

        return super().get(request, *args, **kwargs)

    # create a new object
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    # create a new object
    # def put(self, request, *args, **kwargs):
    #     return self.create(request, *args, **kwargs)

    # update an existing object
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    # delete an existing object
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CategoryAPIView(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.ListAPIView
):
    queryset = Category.objects.all()

    def get_serializer_class(self):
        return CategoryBase64Serializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method == "POST":
            permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        passed_id = self.kwargs.get('id', None)
        if passed_id is not None:
            return Category.objects.filter(pk=passed_id)
        else:
            return Category.objects.all()

    # create a new object
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    # update an existing object
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    # required for patching
    def get_object(self):
        passed_id = self.kwargs.get('id', None)
        return Category.objects.get(pk=passed_id)

    # delete an existing object
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CategoryParentAPIView(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,  mixins.DestroyModelMixin, generics.ListAPIView
):
    def get_serializer_class(self):
        return CategoryBase64Serializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method == "POST":
            permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        passed_id = self.kwargs.get('id', None)
        if passed_id is not None:
            return Category.objects.filter(parent=passed_id)
        else:
            return Category.objects.filter(parent=None)

    # create a new object
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    # update an existing object
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    # delete an existing object
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class SendMethodAPIView(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.ListAPIView
):
    def get_serializer_class(self):
        return SendMethodSerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method == "POST":
            permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return SendMethod.objects.all()

    # create a new object
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    # update an existing object
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    # required for patching
    def get_object(self):
        passed_id = self.kwargs.get('id', None)
        return Category.objects.get(pk=passed_id)

    # delete an existing object
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class OrderAPIView(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.ListAPIView
):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        serializer_class = OrderSerializer

        return_object = self.request.query_params.get('return-object', None)
        if return_object not in empty_list:
            if return_object == 'true':
                serializer_class = OrderReturnObjectSerializer

        return serializer_class

    def get_queryset(self):
        queryset = Order.objects.all().order_by('-created_at')

        tracking_code = self.request.query_params.get('tracking-code', None)
        if tracking_code not in empty_list:
            queryset = queryset.filter(tracking_code=tracking_code)

        return queryset

    # Get object by id
    def get_object(self):
        request = self.request
        passed_id = request.GET.get('id', None) or self.passed_id
        queryset = self.queryset
        obj = None
        if passed_id is not None:
            obj = get_object_or_404(queryset, pk=passed_id)
            self.check_object_permissions(request, obj)
        return obj

    # Get object
    def get(self, request, *args, **kwargs):
        url_passed_id = request.GET.get('id')

        json_data = {}
        body_ = request.body

        if is_json(body_):
            json_data = json.loads(request.body)

        new_passed_id = json_data.get('id', None)

        passed_id = url_passed_id or new_passed_id or None
        # self.passed_id = passed_id

        if passed_id is not None:
            return self.retrieve(request, *args, **kwargs)

        return super().get(request, *args, **kwargs)

    # create a new object
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    # update an existing object
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    # delete an existing object
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


# Zibal Payment
class ZibalTransactionRequestAPIView(APIView):
    @staticmethod
    def post(request):
        try:
            json_body = json.loads(request.body)

            # Find order
            order_tracking_code = json_body['tracking_code']
            order = Order.objects.get(tracking_code=order_tracking_code)
            price_rial = order.total_price * 10

            if order.order_status == 'EX':
                return JsonResponse({
                    'type': 'error',
                    'message': 'امکان پرداخت سفارش منقضی شده وجود ندارد.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create Transaction
            transac = Transaction.objects.create(order=order, amount=price_rial, method='ZB')

            # Request to zibal for starting a new payment session
            zibal_response = requests.post(zibal_request_url, json={
                "merchant": merchant_key,
                "amount": price_rial,
                "callbackUrl": 'http://localhost:8000/api/payment/callback/',
                "description": "خرید از گلدیبا",
                "orderId": order.tracking_code,
                "mobile": order.user.mobile,
            })

            # API Call Successful
            if zibal_response.ok:
                zibal_json = zibal_response.json()
                zibal_trackId = str(zibal_json['trackId'])

                zibal_payment = ZibalPayment(
                    transaction=transac,
                    amount=price_rial,
                    track_id=zibal_trackId,
                )

                # Response Status is OK
                if zibal_json.get('result') == 100 or zibal_json.get('result') == 201:
                    zibal_payment.save()  # Payment session started
                    return JsonResponse({
                        'type': 'ok',
                        'message': 'درگاه پرداخت آماده است.',
                        'payment_url': "https://gateway.zibal.ir/start/" + zibal_trackId + "/"
                    }, status=status.HTTP_200_OK)

                # Response Status is not OK
                else:
                    return JsonResponse({
                        'type': 'error',
                        'message': zibal_json.get('message')
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            # API Call Failed
            else:
                return JsonResponse({
                    'type': 'error',
                    'message': 'سرویس درگاه پرداخت در دسترس نیست.'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


        except Exception as e:
            logger.error(e)
            return Response({
                'type': 'error',
                'status': 'خطا از سمت سرور گلدیبا.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ZibalPaymentCallbackAPIView(APIView):
    def get(self, request):
        try:
            payment_success = self.request.query_params.get('success', None)
            payment_trackId = self.request.query_params.get('trackId', None)
            payment_orderId = self.request.query_params.get('orderId', None)
            payment_status = self.request.query_params.get('status', None)

            # Find payment & transaction
            zibal_payment = ZibalPayment.objects.get(track_id=payment_trackId)
            transac = zibal_payment.transaction

            zibal_payment.success = payment_success
            zibal_payment.status = payment_status
            zibal_payment.save()

            # Find order
            order = Order.objects.get(tracking_code=payment_orderId)
            print('payment success = ', 1)
            if payment_success == '1':

                transac.status = 'OK'
                transac.save()

                order.order_status = 'AP'
                order.save()

                # send verification to zibal
                zibal_response = requests.post(zibal_verify_url, json={
                      "merchant": merchant_key,
                      "trackId": payment_trackId
                    }
                )

                if zibal_response.ok:
                    zibal_json = zibal_response.json()

                    transac.paid_at = dateparse.parse_datetime(zibal_json['paidAt'])
                    transac.card_number = zibal_json['cardNumber']
                    transac.amount = zibal_json['amount']
                    transac.ref_number = zibal_json['refNumber']
                    transac.description = zibal_json['description']
                    transac.save()

                    zibal_payment.status = zibal_json['status']
                    zibal_payment.amount = zibal_json['amount']
                    zibal_payment.save()

                else:
                    return Response({
                        'type': 'error',
                        'status': 'فرآیند ارسال تاییدیه پرداخت به درگاه زیبال موفقیت آمیز نبود.'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            else:
                transac.status = 'ER'
                transac.save()

                zibal_payment.status = payment_status
                zibal_payment.save()

            return redirect(
                'http://localhost:3000/order/callback/?tracking='
                + payment_orderId
                + '&success='
                + payment_success
            )

        except Exception as e:
            logger.error(e)
            return Response({
                'type': 'error',
                'status': 'خطا از سمت سرور.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Offline Payment
class OfflineTransactionRequestAPIView(APIView):
    @staticmethod
    def post(request):
        try:
            json_body = json.loads(request.body)

            # Find order
            order_tracking_code = json_body['tracking_code']
            order = Order.objects.get(tracking_code=order_tracking_code)
            price_rial = order.total_price * 10

            if order.order_status == 'EX':
                return JsonResponse({
                    'type': 'error',
                    'message': 'امکان پرداخت سفارش منقضی شده وجود ندارد.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create Transaction
            transac = Transaction.objects.create(order=order, amount=price_rial, method='OF', datetime=timezone.now())

            # Create Payment
            offline_payment = OfflinePaymentSerializer(data={
                "transaction": str(transac.transaction_id),
                "amount": price_rial,
                "attachment": json_body['attachment']
            })

            if offline_payment.is_valid(raise_exception=True):
                offline_payment.save()

                return JsonResponse({
                    'type': 'ok',
                    'message': 'سفارش با موفقیت ثبت شد.',
                }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(e)
            return Response({
                'type': 'error',
                'status': 'خطا از سمت سرور گلدیبا.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentAPIView(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.ListAPIView
):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        serializer_class = OfflinePaymentSerializer

        method = self.request.query_params.get('method', None)
        if method not in empty_list:
            if method == 'ZB':
                serializer_class = ZibalPaymentSerializer

        return serializer_class

    def get_queryset(self):
        queryset = OfflinePayment.objects.all()

        method = self.request.query_params.get('method', None)
        if method not in empty_list:
            if method == 'ZB':
                queryset = ZibalPayment.objects.all()

        transac = self.request.query_params.get('transaction', None)
        if transac not in empty_list:
            queryset = queryset.filter(transaction=transac)

        return queryset

    # create a new object
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    # update an existing object
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    # delete an existing object
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class TransactionApproveAPIView(
    mixins.UpdateModelMixin, generics.ListAPIView
):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        serializer_class = TransactionApproveSerializer
        return serializer_class

    def get_queryset(self):
        queryset = Transaction.objects.all()
        return queryset

    # required for patching
    def get_object(self):
        passed_id = self.request.query_params.get('id', None)
        return self.get_queryset().get(pk=passed_id)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)