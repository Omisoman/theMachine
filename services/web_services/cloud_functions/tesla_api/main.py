from wake_up_tesla import wake_up_tesla as tesla_wake
from honk_tesla import honk_tesla as tesla_honk
from flash_lights import flash_lights as tesla_flash
from set_climate_keeper_mode import set_climate_keeper_mode as tesla_climate
from set_bioweapon_mode import set_bioweapon_mode as tesla_bioweapon
from start_max_defrost import start_max_defrost as tesla_defrost
from vent_windows import vent_windows as tesla_vent_windows
from close_windows import close_windows as tesla_close_windows
from lock_car import lock_car as tesla_lock
from unlock_car import unlock_car as tesla_unlock

# Entry point for waking up Tesla
def wake_up_tesla(request):
    return tesla_wake(request)

# Entry point for honking the Tesla
def honk_tesla(request):
    return tesla_honk(request)

# Entry point for flashing Tesla lights
def flash_lights(request):
    return tesla_flash(request)

# Entry point for setting climate keeper mode
def set_climate_keeper_mode(request):
    return tesla_climate(request)

# Entry point for setting bioweapon mode
def set_bioweapon_mode(request):
    return tesla_bioweapon(request)

# Entry point for starting max defrost
def start_max_defrost(request):
    return tesla_defrost(request)

# Entry point for venting windows
def vent_windows(request):
    return tesla_vent_windows(request)

# Entry point for closing windows
def close_windows(request):
    return tesla_close_windows(request)

# Entry point for locking the Tesla
def lock_car(request):
    return tesla_lock(request)

# Entry point for unlocking the Tesla
def unlock_car(request):
    return tesla_unlock(request)
