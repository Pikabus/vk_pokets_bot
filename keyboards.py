from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# Настройки для инлайн-клавиатуры
settings = dict(one_time=False, inline=True)

# Инлайн-клавиатура для рейда
keyboard_raid = VkKeyboard(**settings)

# Добавление кнопки Вход
keyboard_raid.add_callback_button(
    label='&#9989;Вход', color=VkKeyboardColor.POSITIVE, payload={'type': 'Callback_raid_join'})

# Добавление кнопки Покинуть
keyboard_raid.add_callback_button(
    label='Покинуть', color=VkKeyboardColor.NEGATIVE, payload={'type': 'Callback_raid_leave'})
