from rest_framework import serializers


class LogoConfigSerializer(serializers.Serializer):
    image = serializers.DictField()
    site_name = serializers.DictField()
    slogan = serializers.DictField()
