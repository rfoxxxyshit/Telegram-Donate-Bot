import logging
import hwinfo
import requests
import json
import sys
from modules.moduleResolver import ModuleResolver

from aiogram import Bot, Dispatcher, executor, types

version = '1.5'


def printLogo():
    print("  __      __                      ")
    print(" / /____ / /__ ___ ________ ___ _ ")
    print("/ __/ -_) / -_) _ `/ __/ _ `/  ' \\")
    print("\\__/\\__/_/\\__/\\_, /_/  \\_,_/_/_/_/")
    print("             /___/                ")
    print("     __               __        __        __ ")
    print(" ___/ /__  ___  ___ _/ /____   / /  ___  / /_")
    print("/ _  / _ \\/ _ \\/ _ `/ __/ -_) / _ \\/ _ \\/ __/")
    print("\\_,_/\\___/_//_/\\_,_/\\__/\\__/ /_.__/\\___/\\__/ ")
    print("                                             ")
    print("\n")


def printHelp():
    return print("Usage: python3 __main__.py (--no-logo) (--not-clear)"
                 " (--kek) (--minimize) (--help/-h)")


if "--not-clear" not in sys.argv:
    hwinfo.tools.clearConsole()
if "--no-logo" not in sys.argv:
    printLogo()
if "--help" in sys.argv or "-h" in sys.argv:
    printHelp()
    exit()
if "--minimize" not in sys.argv:
    print('Staring Telegram Donate Bot v{}'.format(version))
else:
    print('Starting...')


def percentStyleConfigurator():
    hwinfo.tools.clearConsole()
    printLogo()
    while True:
        style = input('Выберите стиль прогресса сбора.\n\n'
                      '1. Windows 95 (█░░░░)\n'
                      '2. Modern (▰▱▱▱▱)\n'
                      'Выбор (1): ').strip()

        if style not in ('1', '2'):
            if style == '':
                style = '1'
                break
            print('Пожалуйста, выберите стиль.\n')
        else:
            break
    return style


def donateModuleConfigurator():
    hwinfo.tools.clearConsole()
    printLogo()
    donate_modules = ['Tinkoff']
    moduleList = ""
    for i in range(len(donate_modules)):
        moduleList += "{}. {}\n".format(i+1, donate_modules[i])
    while True:
        module = input('Выберите модуль для приема донатов.\n\n'
                       f'{moduleList}'
                       'Выбор (1): ').strip()

        if module not in (range(len(donate_modules) + 1)):
            if module == '':
                module = '1'
                break
            print('Пожалуйста, выберите модуль.\n')
        else:
            break
    moduleSelected = int(module) - 1
    return donate_modules[moduleSelected].lower()


def configurator():
    hwinfo.tools.clearConsole()
    printLogo()

    Token = input('Пожалуйста, введите токен бота: ').strip()
    hwinfo.tools.clearConsole()
    printLogo()

    module = donateModuleConfigurator()
    hwinfo.tools.clearConsole()
    printLogo()

    Link = input('Пожалуйста, введите ссылку на сбор: ').strip()
    hwinfo.tools.clearConsole()
    printLogo()

    Text = input('Пожалуйста, введите текст для кнопки: ').strip()
    hwinfo.tools.clearConsole()
    printLogo()

    style = percentStyleConfigurator()
    hwinfo.tools.clearConsole()
    printLogo()

    print('Подождите, идет настройка...')

    with open('config.json', 'w') as file:
        json.dump({'botToken': Token,
                   'donationLink': Link,
                   'buttonText': Text,
                   'progressBar': style,
                   'using_module': module}, file, indent=4)

    print('Настройка завершена. Пожалуйста, перезагрузите скрипт.')
    exit(0)


if "--configurator" in sys.argv:
    configurator()


try:
    with open('config.json', 'r') as f:
        config = json.loads(f.read())

    botToken = config['botToken']
    donationLink = config['donationLink']
    buttonText = config['buttonText']
    progress_style = config.get('progressBar')
    using_module = config.get('using_module')
    if not using_module or not progress_style:
        while True:
            update = input("WARNING! Ваш конфиг устарел. "
                           "Вы хотите обновить его? (y/N): ")
            if update.lower() in ('y', 'yes', 'да'):
                configurator()
                break
            else:
                print("Обновление не запущено. Будут использованы "
                      "нативные настройки.")
                if not using_module:
                    using_module = 'tinkoff'
                if not progress_style:
                    progress_style = '1'
                break
    resolve = ModuleResolver(using_module)
    if "--minimize" not in sys.argv:
        print('Using module \"{}\"'.format(using_module).title())
        print('Progress style: {}'.format(
            'Windows 95' if progress_style == '1' else "Modern" if progress_style == '2' else "Linux"  # noqa
        ))
except (KeyError, FileNotFoundError, json.decoder.JSONDecodeError):
    configurator()
    botToken = 'pep8 иди нахуй'

logging.basicConfig(level=logging.INFO, filename='aiogram_logs')

bot = Bot(token=botToken)

dp = Dispatcher(bot)


def remains(tar, coll):
    try:
        return int(int(tar) - int(coll))
    except TypeError:
        return None


def progressPercentage(collect, targ):
    try:
        return round(collect / targ * 100)
    except TypeError:
        return None


def progressBar(progressPercent):
    try:
        if progress_style == '1':
            progressBar_icon_empty = '░'
            progressBar_icon_full = '█'
            progressBar_container = None
        elif progress_style == '2':
            progressBar_icon_empty = '▱'
            progressBar_icon_full = '▰'
            progressBar_container = '[]'
        else:
            progressBar_icon_empty = '-'
            progressBar_icon_full = '#'
            progressBar_container = '[]'
        if progressPercent >= 100:
            return progressBar_icon_full * 20
        else:
            collect = (round(progressPercent / 5)) * progressBar_icon_full
            residual = (20 - len(collect)) * progressBar_icon_empty
            if progressBar_container is not None:
                return "{}{}".format(collect,
                                     residual).join(
                                         progressBar_container
                                     )
            else:
                return collect + residual
    except TypeError as e:
        print(e)
        return None


@dp.message_handler(content_types=['text'])
async def text_handler(message: types.Message):
    inline_kb_full = types.InlineKeyboardMarkup(row_width=1)
    inline_kb_full.add(
        types.InlineKeyboardButton(buttonText, url=donationLink))

    tempMessage = await message.reply('<i>Загрузка...</i>', parse_mode='html')

    try:
        request = requests.get(donationLink).text

        donationName = resolve.name(request)
        donationOrganizer = resolve.organizer(request)
        donationDescription = resolve.description(request)
        donationTarget = resolve.target(request)
        donationCollected = resolve.collected(request)
        donationProgressPercentage = progressPercentage(donationCollected,
                                                        donationTarget)
        donationProgressBar = progressBar(donationProgressPercentage)
        donationRemains = remains(donationTarget, donationCollected)

        message = str()

        if donationName is not None:
            message += f'<b>{donationName}</b>\n\n'

        if donationOrganizer is not None:
            message += f'<b>Организатор сбора:</b> <i>{donationOrganizer}</i>\n'  # noqa

        if donationTarget is not None:
            message += f'<b>Цель:</b> <i>{donationTarget} ₽</i>\n'

        if donationCollected is not None:
            message += f'<b>Собрано:</b> <i>{donationCollected} ₽</i>\n'

        if donationRemains is not None:
            message += f'<b>Осталось:</b> <i>{donationRemains} ₽</i>\n\n'

        if donationProgressBar is not None and donationProgressPercentage is not None:  # noqa
            message += f'<b>Прогресс:</b>\n<b>{donationProgressBar}</b> {donationProgressPercentage} %\n\n'  # noqa

        if donationDescription is not None:
            message += f'<b>Описание:</b>\n<i>{donationDescription}</i>'

        return await tempMessage.edit_text(message, parse_mode='html',
                                           reply_markup=inline_kb_full)
    except Exception as e:
        return await tempMessage.edit_text(
            '<b>Произошла ошибка:</b> <code>{}</code>'.format(str(e)),
            parse_mode="html"
        )


if __name__ == '__main__':
    if '--kek' in sys.argv:
        print("""[Интро]
Sayonara boy
Sayonara boy

[Припев]
Детка, ты любишь рваные джинсы
О-о-о-о-о-очень рваные джинсы
Детка, ты любишь рваные джинсы
О-о-о-о-о-очень рваные джинсы

[Куплет 1]
Бейбе, твои глаза, твои дреды
Люди вокруг нас — всего лишь скелеты
Я хочу тебя даже одетой
Быть такими-такими-такими как мы — под запретом
В твоем лофте, ты-ты-ты-ты в моей кофте
Фотки-фотки-фотки-фотки-фотки если мы на тусовке
Любимые кроссовки топчут с тобою вместе
Мы жуем мятную жовку под одну из моих песен

[Припев 2]
Детка, ты любишь рваные джинсы
О-о-о-о-о-очень рваные джинсы
Детка, ты любишь рваные джинсы
О-о-о-о-о-очень рваные джинсы
О-о-о-о-о, о-о-о!
О-о-о-о-о-очень рваные джинсы
О-о-о-о-о, о-о-о!

[Куплет 2]
Девочка — чупа-чупс, перегазировка чувств
Я торчу на тебе, ведь я этого хочу
И ты тоже (тоже, тоже)
Бегут мурашки по коже (коже, коже)
Глаза-стекляшки
В стакане газировка с ягодным сиропом
У нас передозировка, не звоните копам
В стакане газировка с ягодным сиропом
У нас передозировка, не звоните копам

[Припев 2]
Детка, ты любишь рваные джинсы
О-о-о-о-о-очень рваные джинсы
Детка, ты любишь рваные джинсы
О-о-о-о-о-очень рваные джинсы
О-о-о-о-о, о-о-о!
О-о-о-о-о, очень рваные джинсы
О-о-о-о-о, о-о-о!

[Аутро]
Sayonara boy-boy-boy-boy-boy
Sayonara boy""")
    skip_updates = False
    if "--skip" in sys.argv:
        skip_updates = True
    print('Started!')
    executor.start_polling(dp, skip_updates=skip_updates)
