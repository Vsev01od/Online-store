from django.core import validators


# Простой способ создания своего валидатора
def validators_item(value):
    word = "Описание"
    if word not in value:
        raise validators.ValidationError(f"Обязательно используйте слово: {word}")
    return value
