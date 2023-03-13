from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from user.models import User, UserField, DynamicField
from user.serializers import UserSerializer, UserFieldSerializer, DynamicFieldSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []

    @action(
        methods=['GET'],
        detail=True,
        url_path='internal-detail',
        url_name='internal-detail'
    )
    def internal_detail(self, request, *args, **kwargs):
        user = self.get_object()
        out = UserSerializer(instance=user).data
        for detail in user.user_fields.all():
            out[detail.field_name] = detail.field_value
        return Response(out)


class UserFieldViewSet(ModelViewSet):
    queryset = UserField.objects.all()
    serializer_class = UserFieldSerializer
    permission_classes = []

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['method'] = self.request.method.upper()
        return ctx


class DynamicFieldViewSet(ModelViewSet):
    queryset = DynamicField.objects.all()
    serializer_class = DynamicFieldSerializer
    permission_classes = []
