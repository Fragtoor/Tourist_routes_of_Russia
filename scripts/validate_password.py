from password_strength import PasswordStats


def validate_on_password(password):
    stats = PasswordStats(password)
    if stats.length < 8:
        return {'message': 'Минимальная длина пароля должна быть 8 символов'}
    if stats.letters_uppercase < 3:
        return {'message': 'Пароль должен содержать хотя бы 3 прописных буквы'}
    if stats.numbers < 3:
        return {'message': 'Пароль должен содержать хотя бы 3 цифры'}
    if stats.special_characters < 1:
        return {'message': 'Пароль должен содержать хотя бы один специальный символ'}

    return {'message': 'OK'}
