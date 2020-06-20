from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.status import HTTP_406_NOT_ACCEPTABLE
from rest_framework.utils import json

from core.models import User


def request_send_verify_sms(request):
    json_body = json.loads(request.body)
    mobile = json_body['mobile']

    if User.objects.filter(mobile=mobile).exclude(pk=request.user.pk).exists():
        return JsonResponse({
            'status': 'error',
            'message': 'این شماره قبلا ثبت شده.'
        }, status=406)

    # TODO Generate & Send SMS for VERIFICARION_CODE & Save it together with mobile-number anywhere
    # if response['status'] != 200:  # failed send sms
    #     raise APIException('failed to send sms', HTTP_400_BAD_REQUEST)
    # redisClient.setex(verification_code, SMS_VERIFICATION_CODE_EXPIRED_TIME, mobile_number)

    return JsonResponse({
        'status': 'ok',
        'message': 'کد تایید پیامک شد.'
    }, status=200)


# @csrf_exempt # to avoid CSRF Check
def verify_mobile_number(request):
    json_body = json.loads(request.body)
    verification_code = json_body['verification']

    # TODO Check verification code
    # if redisClient.exists(verification_code):
    #     mobile_number = redisClient.get(verification_code).decode("utf-8")
    #     redisClient.setex(mobile_number, CREATE_USER_EXPIRED_TIME, mobile_number)
    # else:
    #     raise APIException('wrong verification code', code=HTTP_406_NOT_ACCEPTABLE)

    if verification_code != '123456':
        return JsonResponse({
            'status': 'error',
            'message': 'کد تایید معتبر نیست.'
        }, status=200)

    # TODO Create User
    print(verification_code)

    return JsonResponse({
        'status': 'ok',
        'message': 'کد تایید اعتبارسنجی شد.'
    }, status=200)