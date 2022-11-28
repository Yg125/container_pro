from datetime import date, timedelta

from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.rbac.models import Roles, User
from apps.rbac.serializer import RolesSerializer, UserSerializer
from apps.rbac.utils.my_pagination import MyPageNumberPagination


class RolesAPIView(APIView):
    def get(self, request):
        roles = Roles.objects.all()
        serializer = RolesSerializer(instance=roles, many=True)
        return Response(serializer.data)

    def post(self, request):
        pass


class StuTotalNumber(APIView):
    def get(self, request):
        count = User.objects.filter(role__name='stu').count()
        return Response({"count": count})


class TeaTotalNumber(APIView):
    def get(self, request):
        count = User.objects.filter(role__name='tea').count()
        return Response({"count": count})


class SupTotalNumber(APIView):
    def get(self, request):
        count = User.objects.filter(role__name='sup').count()
        return Response({"count": count})


# 获取日增用户
class UserDayIncrement(APIView):
    def get(self, request):
        # 1, 查询用户日增数量, 注意点: date.today() 获取的不带时分秒
        count = User.objects.filter(date_joined__gte=date.today(), is_staff=False).count()

        # 2, 返回响应
        return Response({
            "count": count
        })


# 获取月增用户
class UserMonthIncrement(APIView):
    def get(self, request):
        # 1, 获取30天前的时间
        old_date = date.today() - timedelta(days=30)

        # 2, 拼接数据
        count_list = []
        for i in range(1, 31):
            # 2,1 获取当天时间
            current_date = old_date + timedelta(days=i)

            # 2,3 获取当天时间的下一天
            next_date = old_date + timedelta(days=i + 1)

            # 2,4, 查询用户日增数量, 注意点: date.today() 获取的不带时分秒
            count = User.objects.filter(date_joined__gte=current_date, date_joined__lt=next_date,
                                        is_staff=False).count()

            count_list.append({
                "count": count,
                "date": current_date
            })

        # 2, 返回响应
        return Response(count_list)


# 获取用户信息
class UserView(ListAPIView, CreateAPIView):
    pagination_class = MyPageNumberPagination
    # queryset = User.objects.filter(role__name='stu')
    serializer_class = UserSerializer

    # 重写get_queryset方法,提供数据
    def get_queryset(self):

        # 1,获取keyword查询参数
        keyword = self.request.query_params.get("keyword")

        # 2,判断是否有keyword
        if keyword:
            return User.objects.filter(role__name='stu', username__contains=keyword).all()
        else:
            return User.objects.filter(role__name='stu').all()
