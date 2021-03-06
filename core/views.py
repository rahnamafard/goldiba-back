from datetime import *
from django.core.mail import send_mail
from django.db.models import Q, Count
from django.db.models.functions import TruncMonth, TruncYear
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

from api.settings import sms_api_url, merchant_key, zibal_request_url, zibal_verify_url
from core.serializers import *
from . import serializers

import logging
import os
import secrets
import redis
import requests

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
logger = logging.getLogger(__name__)
register_user_redis = redis.StrictRedis(host=REDIS_HOST)
reset_pass_redis = redis.StrictRedis(host=REDIS_HOST)
empty_list = [None, '', 'null']


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
                        register_user_redis.set(mobile, verify_key)
                        register_user_redis.expire(mobile, 60)  # code expires in 60 seconds
                    except Exception as e:
                        logger.error(e)
                        return Response({
                            'type': 'error',
                            'message': 'برخی منابع سرور در دسترس نیست.'
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
                'message': 'خطا از سمت سرور.'
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
                expected_verification_key = reset_pass_redis.get(mobile).decode("utf-8")  # byte to string

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
        serializer_class = ProductSerializer

        return_object = self.request.query_params.get('return-object', None)
        if return_object not in empty_list:
            if return_object == 'true':
                serializer_class = ProductReturnObjectSerializer

        return serializer_class

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

        title = self.request.query_params.get('title', None)
        if title not in empty_list:
            queryset = queryset.filter(title__contains=title)

        code = self.request.query_params.get('code', None)
        if code not in empty_list:
            queryset = queryset.filter(code__contains=code)

        query = self.request.query_params.get('query', None)
        if query not in empty_list:
            queryset = queryset.filter(Q(title__contains=query) | Q(code__contains=query))

        start_date = self.request.query_params.get('start-date', None)
        if start_date not in empty_list:
            queryset = queryset.filter(Q(created_at__gte=start_date) | Q(updated_at__gte=start_date))

        end_date = self.request.query_params.get('end-date', None)
        if end_date not in empty_list:
            end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d").date()
            actual_end_date = end_date_parsed + timedelta(days=1)
            queryset = queryset.filter(Q(created_at__lte=actual_end_date) | Q(updated_at__lte=actual_end_date))

        category = self.request.query_params.get('category', None)
        if category not in empty_list:
            queryset = queryset.filter(categories__category_id__exact=category)

        categories = self.request.query_params.get('categories', None)
        if categories not in empty_list:
            category_ids = categories.split(',')
            # Turn list of values into list of Q objects
            queries = [Q(categories__category_id=category_id) for category_id in category_ids]
            # Take one Q object from the list
            query = queries.pop()
            # Or the Q object with the ones remaining in the list
            for item in queries:
                query |= item
            # Query the model
            queryset = queryset.filter(query).distinct()

        is_active = self.request.query_params.get('is_active', None)
        if is_active not in empty_list:
            if is_active == 'false':
                is_active = False
                queryset = queryset.filter(is_active=is_active)
            elif is_active == 'true':
                is_active = True
                queryset = queryset.filter(is_active=is_active)

        is_recharged = self.request.query_params.get('is_recharged', None)
        if is_recharged not in empty_list:
            if is_recharged == 'false':
                queryset = queryset.filter(recharged_at__isnull=True)
            elif is_recharged == 'true':
                queryset = queryset.filter(recharged_at__isnull=False)

        limit = self.request.query_params.get('limit', None)
        order_by = self.request.query_params.get('order-by', None)
        if order_by not in empty_list:
            order_params = order_by.split(',')
            if limit not in empty_list:
                queryset = queryset.order_by(*order_params)[:int(limit)]
            else:
                queryset = queryset.order_by(*order_params)

        return queryset

    # required for patching
    def get_object(self):
        passed_id = self.request.query_params.get('id', None)
        return Product.objects.get(product_id=passed_id)

    # create a new object
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    # update an existing object
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    # delete an existing object
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ModelAPIView(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.ListAPIView
):
    # Change serializer upon request method -> (self.request.method == "GET")
    def get_serializer_class(self):
        return ModelSerializer

    def get_permissions(self):
        permission_classes = []
        # if self.request.method == "POST":
        #     permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Model.objects.all()

        model_id = self.request.query_params.get('id', None)
        if model_id not in empty_list:
            queryset = queryset.filter(model_id=model_id)

        is_active = self.request.query_params.get('is_active', None)
        if is_active not in empty_list:
            queryset = queryset.filter(is_active=is_active)

        return queryset

    # required for patching
    def get_object(self):
        passed_id = self.request.query_params.get('id', None)
        return Model.objects.get(model_id=passed_id)

    # create a new object
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    # update an existing object
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

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


class CategoryAPIView(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
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
        queryset = Category.objects.all()

        category_id = self.request.query_params.get('id', None)
        if category_id not in empty_list:
            queryset = queryset.filter(category_id=category_id)

        parent = self.request.query_params.get('parent', None)
        if parent not in empty_list:
            queryset = queryset.filter(parent=parent)
        elif parent == 'null':
            queryset = queryset.filter(parent__isnull=True)

        return queryset

    # required for patching
    def get_object(self):
        passed_id = self.request.query_params.get('id', None)
        return Category.objects.get(category_id=passed_id)

    # create a new object
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    # update an existing object
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

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

        order_id = self.request.query_params.get('id', None)
        if order_id not in empty_list:
            queryset = queryset.filter(order_id=order_id)

        name = self.request.query_params.get('name', None)
        if name not in empty_list:
            queryset = queryset.filter(Q(user__first_name__contains=name) | Q(user__last_name__contains=name))

        mobile = self.request.query_params.get('mobile', None)
        if mobile not in empty_list:
            queryset = queryset.filter(user__mobile__contains=mobile)

        phone = self.request.query_params.get('phone', None)
        if phone not in empty_list:
            queryset = queryset.filter(phone__contains=phone)

        order_status = self.request.query_params.get('order-status', None)
        if order_status not in empty_list:
            queryset = queryset.filter(order_status=order_status)

        # must be change for future when we have multiple transactions for an order
        transaction_method = self.request.query_params.get('transaction-method', None)
        if transaction_method not in empty_list:
            queryset = queryset.filter(transactions__method=transaction_method)

        tracking_code = self.request.query_params.get('tracking-code', None)
        if tracking_code not in empty_list:
            queryset = queryset.filter(tracking_code__contains=tracking_code)

        start_date = self.request.query_params.get('start-date', None)
        if start_date not in empty_list:
            queryset = queryset.filter(created_at__gte=start_date)

        end_date = self.request.query_params.get('end-date', None)
        if end_date not in empty_list:
            end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d").date()
            actual_end_date = end_date_parsed + timedelta(days=1)
            queryset = queryset.filter(created_at__lte=actual_end_date)

        province = self.request.query_params.get('province', None)
        if province not in empty_list:
            queryset = queryset.filter(province_name__contains=province)

        city = self.request.query_params.get('city', None)
        if city not in empty_list:
            queryset = queryset.filter(city_name__contains=city)

        user = self.request.query_params.get('user', None)
        if user not in empty_list:
            queryset = queryset.filter(user=user)

        return queryset

    # required for patching
    def get_object(self):
        passed_id = self.request.query_params.get('id', None)
        return Order.objects.get(order_id=passed_id)

    # create a new object
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    # update an existing object
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

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
            if payment_success == '1':

                transac.status = 'OK'
                transac.save()

                order.order_status = 'AP'
                order.save()

                # Send SMS to user
                user = order.user
                try:
                    api = KavenegarAPI(sms_api_key)
                    params = {
                        'receptor': user.mobile,  # multiple mobile number, split by comma
                        'message': 'سلام ' + user.first_name + ' عزیز؛'
                                                               '\n'
                                                               'سفارشتون ثبت شد. میتونین جزئیاتش رو از بخش سفارشات من ببینین.'
                                                               ' حتما مراحل بعدی رو از طریق پیامک به اطلاعتون میرسونیم.'
                                                               '\n'
                                                               'کد پیگیری: ' + order.tracking_code +
                                   '\n'
                                   'گلدیبا؛ حسی زیبا ❤️'
                    }
                    response = api.sms_send(params)
                    logger.log(1, response)
                except APIException as e:
                    logger.error(e)
                except HTTPException as e:
                    logger.error(e)

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
            transac = Transaction.objects.create(order=order, amount=price_rial, method='OF', paid_at=timezone.now())

            # Create Payment
            offline_payment = OfflinePaymentSerializer(data={
                "transaction": str(transac.transaction_id),
                "amount": price_rial,
                "attachment": json_body['attachment']
            })

            if offline_payment.is_valid(raise_exception=True):
                offline_payment.save()

                # Send SMS to user
                user = None
                if request and hasattr(request, "user"):
                    user = request.user

                try:
                    api = KavenegarAPI(sms_api_key)
                    params = {
                        'receptor': user.mobile,  # multiple mobile number, split by comma
                        'message': 'سلام ' + user.first_name + ' عزیز؛'
                                   '\n'
                                   'سفارشتون ثبت شد. میتونین جزئیاتش رو از بخش سفارشات من ببینین.'
                                   ' حتما مراحل بعدی رو از طریق پیامک به اطلاعتون میرسونیم.'
                                   '\n'
                                   'کد پیگیری: ' + order_tracking_code +
                                   '\n'
                                   'گلدیبا؛ حسی زیبا ❤️'
                    }
                    response = api.sms_send(params)
                    logger.log(1, response)
                except APIException as e:
                    logger.error(e)
                except HTTPException as e:
                    logger.error(e)

                # send order to backup email
                subject = 'فاکتور | ' + str(order.created_at) + ' | ' + order.tracking_code
                message = 'test'
                send_mail(
                    subject,
                    message,
                    'sale@goldiba.com',
                    ['arahnamafard@yahoo.com'],
                    fail_silently=True,
                )

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


# Havaleh Anbar Payment
class HavalehAnbarRequestAPIView(APIView):
    @staticmethod
    def post(request):
        try:
            json_body = json.loads(request.body)

            # Find order
            order_tracking_code = json_body['tracking_code']
            requested_by = json_body['requested_by']
            order = Order.objects.get(tracking_code=order_tracking_code)
            price_rial = order.total_price * 10

            if order.order_status == 'EX':
                return JsonResponse({
                    'type': 'error',
                    'message': 'امکان پرداخت سفارش منقضی شده وجود ندارد.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create Transaction
            transac = Transaction.objects.create(order=order,
                                                 amount=price_rial,
                                                 method='HA',
                                                 paid_at=timezone.now())

            # Create Payment
            havaleh_anbar_payment = HavalehAnbarSerializer(data={
                "transaction": str(transac.transaction_id),
                "amount": price_rial,
                "requested_by": requested_by,
            })

            if havaleh_anbar_payment.is_valid(raise_exception=True):
                havaleh_anbar_payment.save()

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

    @staticmethod
    def patch(request):
        try:
            json_body = json.loads(request.body)

            # Find order
            havaleh_anbar_id = json_body['havaleh_anbar_id']
            requested_by = json_body['requested_by']
            delivered_by = json_body['delivered_by']

            # Update Payment
            havaleh_anbar_payment = HavalehAnbar.objects.get(havaleh_anbar_id=havaleh_anbar_id)
            havaleh_anbar_payment.requested_by = requested_by
            havaleh_anbar_payment.delivered_by = delivered_by
            havaleh_anbar_payment.save()

            return JsonResponse({
                'type': 'ok',
                'message': 'حواله با موفقیت ویرایش شد.',
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
            elif method == 'HA':
                serializer_class = HavalehAnbarSerializer

        return serializer_class

    def get_queryset(self):
        queryset = OfflinePayment.objects.all()

        method = self.request.query_params.get('method', None)
        if method not in empty_list:
            if method == 'ZB':
                queryset = ZibalPayment.objects.all()
            elif method == 'HA':
                queryset = HavalehAnbar.objects.all()

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


class ProvinceAPIView(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.ListAPIView
):
    def get_serializer_class(self):
        serializer_class = ProvinceSerializer
        return serializer_class

    def get_permissions(self):
        permission_classes = []
        # if self.request.method == "POST":
        #     permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Province.objects.all().order_by('name')

        province_id = self.request.query_params.get('id', None)
        if province_id not in empty_list:
            queryset = queryset.filter(province_id=province_id)

        name = self.request.query_params.get('name', None)
        if name not in empty_list:
            queryset = queryset.filter(name__contains=name)

        return queryset

    # required for patching
    def get_object(self):
        passed_id = self.request.query_params.get('id', None)
        return Product.objects.get(province_id=passed_id)

    # create a new object
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    # update an existing object
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    # delete an existing object
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CityAPIView(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.ListAPIView
):
    def get_serializer_class(self):
        serializer_class = CitySerializer
        return serializer_class

    def get_permissions(self):
        permission_classes = []
        # if self.request.method == "POST":
        #     permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = City.objects.all().order_by('name')

        city_id = self.request.query_params.get('id', None)
        if city_id not in empty_list:
            queryset = queryset.filter(city_id=city_id)

        province_id = self.request.query_params.get('province_id', None)
        if province_id not in empty_list:
            queryset = queryset.filter(province_id=province_id)

        name = self.request.query_params.get('name', None)
        if name not in empty_list:
            queryset = queryset.filter(name__contains=name)

        return queryset

    # required for patching
    def get_object(self):
        passed_id = self.request.query_params.get('id', None)
        return Product.objects.get(province_id=passed_id)

    # create a new object
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    # update an existing object
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

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
        queryset = SendMethod.objects.all()

        city_id = self.request.query_params.get('city_id', None)
        if city_id not in empty_list:
            queryset = queryset.filter(citysendmethod__city_id=city_id)

        name = self.request.query_params.get('name', None)
        if name not in empty_list:
            queryset = queryset.filter(name__contains=name)

        return queryset

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


class StatisticsAPIView(APIView):
    @staticmethod
    def get(req):
        try:
            query = req.GET.get('query', None)  # which model
            upon = req.GET.get('upon', None)    # daily, monthly, yearly
            start = req.GET.get('start', None)  # start-date
            end = req.GET.get('end', None)      # end-date
            filter = req.GET.get('filter', None)      # end-date

            if query == 'orders':

                if upon == "month":
                    result = Order.objects \
                        .annotate(period=TruncMonth('created_at')) \
                        .values('period') \
                        .annotate(count=Count('created_at')) \
                        .values('period', 'count')
                elif upon == "year":
                    result = Order.objects \
                        .annotate(period=TruncYear('created_at')) \
                        .values('period') \
                        .annotate(count=Count('created_at')) \
                        .values('period', 'count')
                else:
                    result = Order.objects.extra(select={'period': 'date( created_at )'}) \
                        .values('period') \
                        .annotate(count=Count('created_at'))

                if start is not None:
                    result = result.filter(created_at__gte=start)
                else:
                    result = result.filter(created_at__gte=datetime.now() - timedelta(days=30))

                if end is not None:
                    result = result.filter(created_at__lte=end)
                else:
                    result = result.filter(created_at__lte=datetime.now())

                if filter == 'AP':
                    result = result.filter(order_status='AP')
                elif filter == 'PE':
                    result = result.filter(order_status='PE')
                elif filter == 'EX':
                    result = result.filter(order_status='EX')

                return Response({
                        'type': 'ok',
                        'message': 'عملیات با موفقیت انجام شد.',
                        'data': result
                    }, status=status.HTTP_200_OK)

            elif query == 'users':
                if upon == "month":
                    result = User.objects \
                        .annotate(period=TruncMonth('date_joined')) \
                        .values('period') \
                        .annotate(count=Count('date_joined')) \
                        .values('period', 'count')
                elif upon == "year":
                    result = User.objects \
                        .annotate(period=TruncYear('date_joined')) \
                        .values('period') \
                        .annotate(count=Count('date_joined')) \
                        .values('period', 'count')
                else:
                    result = User.objects.extra(select={'period': 'date( date_joined )'}) \
                        .values('period') \
                        .annotate(count=Count('date_joined'))

                if start is not None:
                    result = result.filter(date_joined__gte=start)
                else:
                    result = result.filter(date_joined__gte=datetime.now() - timedelta(days=30))

                if end is not None:
                    result = result.filter(date_joined__lte=end)
                else:
                    result = result.filter(date_joined__lte=datetime.now())

                return Response({
                    'type': 'ok',
                    'message': 'عملیات با موفقیت انجام شد.',
                    'data': result
                }, status=status.HTTP_200_OK)

            else:
                return Response({
                    'type': 'error',
                    'status': 'نوع آمار نامعتبر است.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        except Exception as e:
            logger.error(e)
            return Response({
                'type': 'error',
                'status': 'خطا از سمت سرور.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
