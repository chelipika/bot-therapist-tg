from aiogram.fsm.state import StatesGroup, State


class Reg(StatesGroup):
    user_id = State()
    ai_name = State()
    name = State()
    Experience = State()
    Approach = State()
    Mission = State()
    Commitment = State()
    CallToAction = State() 

class AdvMsg(StatesGroup):
    img = State()
    audio = State()
    txt = State()
    inline_link_name = State()
    inline_link_link = State()
    
class GroupMsg(StatesGroup):
    img = State()
    audio = State()
    txt = State()
    inline_link_name = State()
    inline_link_link = State()

class Gen(StatesGroup):
    wait = State()