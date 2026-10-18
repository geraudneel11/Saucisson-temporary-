# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('step_wood.wav', '.'), ('Swordsman_lvl1_Hurt_with_shadow.png', '.'), ('Swordsman_lvl2_attack_with_shadow.png', '.'), ('Shop.png', '.'), ('Citizen2_Walk.png', '.'), ('Mon1k_Idle.png', '.'), ('Text6.png', '.'), ('Dynamite.png', '.'), ('Swordsman_lvl3_Walk_with_shadow.png', '.'), ('Priest_making_spell.png', '.'), ('chapel_interior_objects.png', '.'), ('Swordsman_lvl3_Hurt_with_shadow.png', '.'), ('Swordsman_lvl2_Walk_Attack_with_shadow.png', '.'), ('step_grass.wav', '.'), ('coin.wav', '.'), ('Swordsman_lvl3_Run_Attack_with_shadow.png', '.'), ('Mon1k_Walk.png', '.'), ('hit_enemy.wav', '.'), ('chapel_dragon_body.png', '.'), ('Swordsman_lvl3_Run_with_shadow.png', '.'), ('Interior_objects.png', '.'), ('explosion.wav', '.'), ('Parishioner9.png', '.'), ('Trees_animation.png', '.'), ('Parishioner3.png', '.'), ('Swordsman_lvl2_Run_Attack_with_shadow.png', '.'), ('Parishioner6.png', '.'), ('Interior.png', '.'), ('exterior.png', '.'), ('Priest_speech.png', '.'), ('Swordsman_lvl1_attack_with_shadow.png', '.'), ('Tapis_bleu.png', '.'), ('chapel_interior_walls.png', '.'), ('Mon4k_Walk.png', '.'), ('Swordsman_lvl1_Run_with_shadow.png', '.'), ('Text7.png', '.'), ('dynamite_bounce.wav', '.'), ('Mon4k_Pray.png', '.'), ('ui_click.wav', '.'), ('Dimensional_Portal.png', '.'), ('MonedaD.png', '.'), ('run_down.png', '.'), ('Shop_exit_button.png', '.'), ('Statues.png', '.'), ('Citizen1_Walk.png', '.'), ('Parishioner1.png', '.'), ('Swordsman_lvl2_Walk_with_shadow.png', '.'), ('orc1_hurt_full.png', '.'), ('Parishioner5.png', '.'), ('xp_orb.wav', '.'), ('equip.wav', '.'), ('Health_bar.png', '.'), ('orc1_idle_full.png', '.'), ('Swordsman_lvl3_Idle_with_shadow.png', '.'), ('golden_apple.png', '.'), ('Swordsman_lvl3_Walk_Attack_with_shadow.png', '.'), ('Swordsman_lvl3_attack_with_shadow.png', '.'), ('door.mp3', '.'), ('Text2.png', '.'), ('enemy_death.wav', '.'), ('chapel_exterior.png', '.'), ('Mon2k_Idle.png', '.'), ('Priest_spell.png', '.'), ('Parishioner2.png', '.'), ('Parishioner10.png', '.'), ('buy.wav', '.'), ('eat.wav', '.'), ('Mon4k_Idle.png', '.'), ('Priest_Walk.png', '.'), ('ground_grass_details.png', '.'), ('plaza.png', '.'), ('enemy_attack.wav', '.'), ('page_turn.wav', '.'), ('attack.wav', '.'), ('Smoke_animation.png', '.'), ('dynamite_throw.wav', '.'), ('Text3.png', '.'), ('Swordsman_lvl2_Idle_with_shadow.png', '.'), ('Priest_Idle.png', '.'), ('Mon1k_Pray.png', '.'), ('ui_error.wav', '.'), ('step_stone.wav', '.'), ('Text1.png', '.'), ('Parishioner4.png', '.'), ('settings.json', '.'), ('Citizen1_Idle.png', '.'), ('Citizen2_Idle.png', '.'), ('potion.wav', '.'), ('item_pickup.wav', '.'), ('walls_floor.png', '.'), ('Swordsman_lvl2_Hurt_with_shadow.png', '.'), ('Mon2k_Pray.png', '.'), ('chapel_dragon.png', '.'), ('Mon2k_Walk.png', '.'), ('Text4.png', '.'), ('orc1_run_full.png', '.'), ('Candelabra.png', '.'), ('orc1_death_full.png', '.'), ('Swordsman_lvl3_Death_with_shadow.png', '.'), ('Swordsman_lvl1_Idle_with_shadow.png', '.'), ('apple.png', '.'), ('Xp_bar.png', '.'), ('Herbe.jpg', '.'), ('Swordsman_lvl2_Run_with_shadow.png', '.'), ('level_up.wav', '.'), ('heal.wav', '.'), ('Parishioner7.png', '.'), ('Parishioner8.png', '.'), ('Fiole_de_soin.png', '.'), ('chapel_wall_texture.png', '.'), ('Parishioner11.png', '.'), ('chapel_altar.png', '.'), ('Text5.png', '.'), ('Buttons.png', '.'), ('Swordsman_lvl2_Death_with_shadow.png', '.'), ('orc1_attack_full.png', '.'), ('enemy_hurt.wav', '.')]
binaries = []
hiddenimports = []
tmp_ret = collect_all('pygame')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['pyi_rth_cwd.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Pixsouls',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
