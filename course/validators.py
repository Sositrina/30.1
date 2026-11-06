from urllib.parse import urlparse
from rest_framework import serializers


def validate_youtube_url(value):
    """Проверяет, что ссылка ведёт на YouTube."""
    domain = urlparse(value).hostname

    if domain not in ['youtube.com', 'www.youtube.com']:
        raise serializers.ValidationError(
            'Разрешены только ссылки на youtube.com.'
        )