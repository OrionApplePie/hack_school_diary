from random import choice

from django.core.exceptions import  MultipleObjectsReturned, ObjectDoesNotExist

from datacenter.models import (Chastisement, Commendation, Lesson, Mark,
                               Schoolkid)


COMMENDATIONS = [
    'Молодец!',
    'Отлично!',
    'Хорошо!',
    'Гораздо лучше, чем я ожидал!',
    'Ты меня приятно удивил!',
    'Великолепно!',
    'Прекрасно!',
    'Ты меня очень обрадовал!',
    'Именно этого я давно ждал от тебя!',
    'Сказано здорово – просто и ясно!',
    'Ты, как всегда, точен!',
    'Очень хороший ответ!',
    'Талантливо!',
    'Ты сегодня прыгнул выше головы!',
    'Я поражен!',
    'Уже существенно лучше!',
    'Потрясающе!',
    'Замечательно!',
    'Прекрасное начало!',
    'Так держать!',
    'Ты на верном пути!',
    'Здорово!',
    'Это как раз то, что нужно!',
    'Я тобой горжусь!',
    'С каждым разом у тебя получается всё лучше!',
    'Мы с тобой не зря поработали!',
    'Я вижу, как ты стараешься!',
    'Ты растешь над собой!',
    'Ты многое сделал, я это вижу!',
    'Теперь у тебя точно все получится!',
]

CLASS_LETTERS = ['А', 'Б', 'В']


def get_schoolkid(search_string=''):
    """Поиск профиля ученика по ФИО."""

    if not search_string:
        print('Ошибка! Введите ФИО ученика.')
        return None
    try:
        target_schoolkid = Schoolkid.objects.get(
            full_name__contains=search_string
        )
    except  MultipleObjectsReturned:
        print('Найдено несколько учеников! Введите ФИО полностью.')
        return None
    except ObjectDoesNotExist:
        print('Не найдено учеников! Проверьте ФИО и попробуйте еще раз.')
        return None

    return target_schoolkid


def fix_marks(schoolkid=None):
    """Исправление всех двоек и троек на хорошо или отлично.
    Также убирются плохие заметки учителя из плохой отметки."""

    if schoolkid is None:
        print('Необходим профиль ученика!')
        return None

    marks = Mark.objects.filter(
        schoolkid=schoolkid,
        points__in=[2, 3]
    )
    for mark in marks:
        mark.points = choice([4, 5])
        mark.teacher_note = None
        mark.save()

    if marks.count() == 0:
        print('Плохих оценок не найдено. Изменений не внесено.')
    else:
        print(f'Успешно! Оценок исправлено: {marks.count()}.')


def remove_chastisements(schoolkid=None):
    """Удаление всех жалоб на заданного ученика."""

    if schoolkid is None:
        print('Необходим профиль ученика!')
        return None

    deleted_chastisements, _ = Chastisement.objects.filter(
        schoolkid=schoolkid).delete()

    if deleted_chastisements == 0:
        print('Жалобы не найдены. Изменений не внесено.')
    else:
        print(f'Успешно! Записей жалоб удалено: {deleted_chastisements}.')


def create_commendation(
        schoolkid=None, year_of_study=1, group_letter='А', subject_name=''
    ):
    """Создание похвалы заданному ученику по заданному предмету
    на последнем на данный момент уроке."""

    if schoolkid is None:
        print('Необходим профиль ученика!')
        return None
    
    if (year_of_study not in range(1, 12)
        or group_letter not in CLASS_LETTERS):
        print('Ошибка! Проверьте номер класса!')
        return None

    if not subject_name:
        print('Ошибка! Введите название предмета!')
        return None

    target_lesson = Lesson.objects.filter(
        group_letter=group_letter,
        year_of_study=year_of_study,
        subject__title__contains=subject_name) \
            .order_by('-date') \
            .first()

    if target_lesson is None:
        print('Ошибка! Урок не найден. '
              'Проверьте название урока, год и литеру класса!')
        return None

    comm_by_lesson = Commendation.objects.filter(
        schoolkid=schoolkid, teacher=target_lesson.teacher,
        subject=target_lesson.subject, created=target_lesson.date)

    if comm_by_lesson.exists():
        print(f'Похвала по предмету "{target_lesson.subject}" '
              f'на уроке от {target_lesson.date} уже есть. '
               'Не создается больше одной похвалы на урок.')
        return None

    comm_text = choice(COMMENDATIONS)

    comm = Commendation.objects.create(
        text=comm_text,
        schoolkid=schoolkid,
        teacher=target_lesson.teacher,
        subject=target_lesson.subject,
        created=target_lesson.date
    )

    print(f'Успешно! '
          f'Похвала по предмету "{comm.subject}" создана: "{comm.text}".')


def hack_school_diary(name, year, letter, subject):
    """Весь функционал для исправления оценок и замечаний в одном вместе."""

    target_schoolkid = get_schoolkid(name)

    if target_schoolkid is None:
        return None

    fix_marks(target_schoolkid)
    remove_chastisements(target_schoolkid)
    create_commendation(
        schoolkid=target_schoolkid,
        year_of_study=year,
        group_letter=letter,
        subject_name=subject
    )
