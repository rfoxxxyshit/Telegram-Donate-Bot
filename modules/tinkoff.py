class Tinkoff:
    def __init__(self):
        """Tinkoff module"""

    def organizer(self, req: str):
        for line in req.splitlines():
            if 'organizerName' in line:
                return line.split(
                    'organizerName'
                )[1].split(''
                           '"CrowdPage">'
                           )[1].split(
                    '</span>')[0]

            else:
                continue
        else:
            return None

    def description(self, req: str):
        for line in req.splitlines():
            if 'CollectMoneyPayForm__description' in line:
                return line.split(
                    'CollectMoneyPayForm__description'
                )[1].split(
                    '"CollectMoneyPayForm">'
                )[1].split('</span>')[0]
            else:
                continue
        else:
            return None

    def name(self, req: str):
        for line in req.splitlines():
            if '<meta property="og:title" content="' in line:
                return line.split(
                    '<meta property="og:title" content="'
                )[1].split('"')[0]
            else:
                continue
        else:
            return None

    def target(self, req: str):
        for line in req.splitlines():
            if '<span class="CollectionInfoHeader__goal' in line:
                temp_target = line.split(
                    '<span class="CollectionInfoHeader__goal'
                )[1].split(
                    '"CollectionInfoHeader">Цель: '
                )[1].split(' ₽</span>')[0]
                temp = str()

                for symbol in temp_target:
                    if symbol in '1234567890,.':
                        temp += symbol

                return int(float(temp.replace(',', '.')))
            else:
                continue
        else:
            return None

    def collected(self, req: str):
        for line in req.splitlines():
            if 'class="CollectionInfoHeader__percents' in line:
                temp_collected = line.split(
                    '"CollectionInfoHeader">Собрано: '
                )[1].split(' ₽</span>')[0]

                temp = str()

                for symbol in temp_collected:
                    if symbol in '1234567890,.':
                        temp += symbol

                return int(float(temp.replace(',', '.')))
            else:
                continue
        else:
            return None
