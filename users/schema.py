"""
Users GraphQL Schema
Provides JWT auth and current user query for admin dashboard
"""
import graphene
from graphene_django import DjangoObjectType
import graphql_jwt
from django.contrib.auth import get_user_model


User = get_user_model()


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "is_staff", "is_superuser")


class UserQuery(graphene.ObjectType):
    me = graphene.Field(UserType, description="Return the currently authenticated user")

    def resolve_me(self, info):
        user = info.context.user
        if user.is_authenticated:
            return user
        return None


class ObtainJSONWebToken(graphql_jwt.ObtainJSONWebToken):
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        result = super().resolve(root, info, **kwargs)
        if info.context.user.is_authenticated:
            result.user = info.context.user
        return result


class UserMutation(graphene.ObjectType):
    token_auth = ObtainJSONWebToken.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    verify_token = graphql_jwt.Verify.Field()


