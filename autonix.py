import multiprocessing
import time

from anttehpc import start_anttehpc_bot
from app import start_app_bot
from Autonixadmin import start_admin_bot
from Autonixassistant import start_assistant_bot
from Autonixcardgenerator import start_Autonixcardgenerator_bot
from Autonixcardpayment import start_Autonixcardpayment_bot
from Autonixedge import start_AutonixEdge_bot
from Autonixedgekey import start_Autonixedgekey_bot
from Autonixfree import start_free_bot
from Autonixhub import start_Autonixhub_bot
from Autonixlite import start_basic_bot
from Autonixlitekey import start_basickey_bot
from Autonixpro import start_premium_bot
from Autonixprokey import start_premiumkey_bot

if __name__ == "__main__":
    processes = []

    bot_functions = [
        ("pc watchdog", start_anttehpc_bot),
        ("app", start_app_bot),
        ("admin", start_admin_bot),
        ("assisttant", start_assistant_bot),
        ("card generation", start_Autonixcardgenerator_bot),
        ("card payment", start_Autonixcardpayment_bot),
        ("Autonixedge", start_AutonixEdge_bot),
        ("Autonixedgekey", start_Autonixedgekey_bot),
        ("free", start_free_bot),
        ("Autonix", start_Autonixhub_bot),
        ("lite", start_basic_bot),
        ("lite key", start_basickey_bot),
        ("pro", start_premium_bot),
        ("pro key", start_premiumkey_bot)
    ]

    for bot_name, bot_function in bot_functions:
        p = multiprocessing.Process(target=bot_function)
        p.start()
        processes.append(p)
        time.sleep(15)

    print("\n✅ All bots have been successfully started!")

    for p in processes:
        p.join()
