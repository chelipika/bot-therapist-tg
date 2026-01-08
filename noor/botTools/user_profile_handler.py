import json
from aiogram import Router
from aiogram import F, Bot
from aiogram.types import Query, CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command, CommandObject

from noor.botTools.subscription import sub_chek
from noor.botClasses import Reg
import noor.keyboards as kb
from config import CHANNEL_LINK
from noor.aiMsg.chat_history import USER_PROFILE_FILE, user_chat_histories, save_chat_history

router = Router()


@router.callback_query(F.data == "profile")
async def profileus(callback: CallbackQuery, state: FSMContext):
    await callback.answer("😍")
    await callback.message.edit_text("Here you can create or see your profile💼", reply_markup=kb.profile_settings)
    
@router.callback_query(F.data == "show_users_profliee")
async def show_users_profliee(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    try:
        await callback.message.edit_text(f"Here is your profile: \n👤 Your_name: {user_profile[user_id]['name']} \n💼 Your_exp_job: {user_profile[user_id]['Experience']} \n💡 My_Approach: {user_profile[user_id]['Approach']} \n🚀 My_Mission: {user_profile[user_id]['Mission']} \n🔒 My_Commitment: {user_profile[user_id]['Commitment']} \n📞 Your_CallToAction: {user_profile[user_id]['CallToAction']} \n🤖 My_ai_name: {user_profile[user_id]['ai_name']}", reply_markup=kb.profile_settings)
    except KeyError:
        await callback.message.edit_text("You dont have a profile yet so you should create one", reply_markup=kb.profile_creating)


@router.callback_query(F.data == "create_update_profile")
async def create_update_profile(callback: CallbackQuery, state: FSMContext):
    await callback.answer("💼")
    await state.set_state(Reg.name)
    await callback.message.answer("How should I call you? Write just your name (e.g. Noor, Licensed Therapist) \n Как мне к вам обращаться? Напишите только имя (например, Нур, лицензированный терапевт)")



@router.message(Command("reg"))
async def reg_name(message: Message, state: FSMContext):
    if not await sub_chek(message.from_user.id):
        await message.answer(f"Subscribe first, Подпишитесь: \n{CHANNEL_LINK}", reply_markup=kb.subscribe_channel)
        return
    await state.set_state(Reg.name)
    await message.answer("How should i call you?(e.g. Noor, Licensed Therapist) \n Как мне к вам обращаться? Напишите только имя (например, Нур, лицензированный терапевт)")

@router.message(Reg.name)
async def reg_exp(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.Experience)
    await message.answer('What do you do(e.g. junior designer, pro programmer, actor. If private leave "private") \n Чем вы занимаетесь (например, младший дизайнер, профессиональный программист, актер. Если вы частный, оставьте «частный»)')

@router.message(Reg.Experience)
async def reg_approach(message: Message, state: FSMContext):
    await state.update_data(Experience=message.text)
    await state.set_state(Reg.Approach)
    await message.answer("How should i approach you? e.g.: \n(Direct, data-driven, and pragmatic—no fluff, just solutions)\n Как мне к вам обращаться? (Прямо, основано на данных и прагматично — без лишних слов, только решения)\n(Слыш, просто на чилях, не веди себя как чушпан, пиши только годные вещи)")

@router.message(Reg.Approach)
async def reg_Mission(message: Message, state: FSMContext):
    await state.update_data(Approach=message.text)
    await state.set_state(Reg.Mission)
    await message.answer('What is my mission?(e.g. Helping you overcome obstacles and optimize mental performance, Help me to overcome procrastination) \n Какова моя миссия? (Например: Помогать вам преодолевать препятствия и оптимизировать умственную продуктивность, Помоги мне справиться с прокрастинацией)')


@router.message(Reg.Mission)
async def reg_Commitment(message: Message, state: FSMContext):
    await state.update_data(Mission=message.text)
    await state.set_state(Reg.Commitment)
    await message.answer("How should i be commited?(e.g. Absolute confidentiality and clear guidance)\n Как я должен быть предан делу? (Например: Абсолютная конфиденциальность и четкие инструкции) \n (Сделай шутки про мои проблемы и в конце добавь какой фильм соответствует моей проблеме)")

@router.message(Reg.Commitment)
async def reg_CallToAction(message: Message, state: FSMContext):
    await state.update_data(Commitment=message.text)
    await state.set_state(Reg.CallToAction)
    await message.answer("Write your typical Call-To-Action(e.g. Ready to tackle challenges? Let's get to work) \n Какой у тебя типичный призыв к действию? (Например: Готов разобраться с проблемами? Давай работать) \n (Слыш ты как телка небудь, давай ради родителей и детей пахай, ты через 5 лет собой будешь гордится)")

@router.message(Reg.CallToAction)
async def reg_ainame(message: Message, state: FSMContext):
    await state.update_data(CallToAction=message.text)
    await state.set_state(Reg.ai_name)
    await message.answer("What name you prefer to me(e.g. Alex, Noor, Optimus, Elon, Temur, SquidPuppy) \n Какое имя ты предпочитаешь для меня? (Например: Алекс, Нур, Оптимус, Илон, Темур, SquidPuppy)")

@router.message(Reg.ai_name)
async def reg_finish(message: Message, state:FSMContext):
    userid = str(message.from_user.id)
    await state.update_data(ai_name=message.text)
    await state.update_data(user_id=userid)
    data = await state.get_data()
    data = {
            userid: {
                'ai_name': data["ai_name"],
                'name': data["name"],
                'Experience': data["Experience"],
                'Approach': data["Approach"],
                'Mission': data["Mission"],
                'Commitment': data["Commitment"],
                'CallToAction': data["CallToAction"]
            }
            
    }
    userid_data = data[userid]
    one_row_data = '"' + "userid: " + ", ".join(f"{key}={value}" for key, value in userid_data.items()) + '"'
    if userid not in user_chat_histories:
            user_chat_histories[userid] = []

        # Add user message to history
    user_chat_histories[userid].append({
        "role": "user",
        "parts": [{"text": one_row_data}]
    })
    save_chat_history()
    with open(USER_PROFILE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

    global user_profile  # Important: Access the global variable
    user_profile.update(data) # Update in-memory data
    # user_profile = load_user_profile() # <--- OLD CODE
    await message.answer(f"You fineshed up you registration.....🎊 \n Вы завершили регистрацию... \n {data}")
    await state.clear()