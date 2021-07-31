from enum import IntEnum
from img.common import Box
from utils.log import get_logger
from ..common import ark_intf

intf = ark_intf

logger = get_logger('Nav')


class Scene(IntEnum):
    Unknown = -1
    Main = 0
    Shop = 1
    Terminal = 2
    Request = 3
    LevelSelect = 4
    BattlePre = 5
    BattleIn = 6
    BattlePost = 7
    Base = 8
    ExitConfirm = 9
    GetResource = 10


PURCHASE_CENTER = 'main/采购中心.png'
RECRUIT = 'main/公开招募.png'
GACHA = 'main/干员寻访.png'
NOTICE = 'main/公告.png'
FRIEND = 'main/好友.png'
REQUEST = 'main/任务.png'
BASE = 'main/基建.png'
TERMINAL = 'main/终端.png'

NO = 'no.png'
OK = 'ok.png'
LAST_BATTLE = 'terminal/前往上一次作战.png'
COLLECT_ALL = 'request/收集全部.png'
COLLECT_REWARD_BOX = Box((619, 619), (658, 657))

Scene_pivot = {
    Scene.Main: [PURCHASE_CENTER, RECRUIT, GACHA, BASE,
                 NOTICE, TERMINAL, FRIEND],
    Scene.Shop: ['shop/信用交易所.png', 'shop/源石交易所.png',
                 'shop/时装商店.png', 'shop/家具商店.png', ],
    Scene.Terminal: ['terminal/main-theme-pivot.png', 'terminal/前往上一次作战.png',
                     'terminal/终端-1.png', 'terminal/终端-2.png', 'terminal/终端-3.png',
                     'terminal/主题曲-1.png', 'terminal/主题曲-2.png', 'terminal/主题曲-3.png',
                     'terminal/资源收集-1.png', 'terminal/资源收集-2.png', ],
    Scene.Request: ['request/日常任务-1.png', 'request/日常任务-2.png',
                    'request/周常任务-1.png', 'request/周常任务-2.png',
                    'request/报酬已领取.png', ],
    # Note: Item order matters
    Scene.BattlePre: ['battle/san.png', 'battle/开始行动-1.png', ],
    Scene.LevelSelect: ['terminal/当前进度.png',
                        'terminal/OPERATION-1.png', 'terminal/OPERATION-2.png', ],
    Scene.BattleIn: ['battle/代理指挥作战正常运行中.png',
                     'battle/speed-1.png', 'battle/speed-2.png', ],
    Scene.BattlePost: ['battle/全员信赖.png', 'battle/行动结束.png', 'battle/剿灭结束.png', ],
    Scene.ExitConfirm: '是否确认退出游戏.png',
    Scene.GetResource: ['获得物资-1.png', '获得物资-2.png']
}


def get_current_scene() -> Scene:
    scr = intf.screen()
    for scene, pivot in Scene_pivot.items():
        if isinstance(pivot, str):
            pivot = [pivot]
        if any(intf.img_match(img, scr) for img in pivot):
            return scene
    return Scene.Unknown
