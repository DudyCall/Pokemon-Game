"""
ui_manager.py - Aggregator for all UI screens, menus, dialogue boxes, and overlays.
Provides 100% backward compatibility for all modules importing from ui_manager.
"""
from ui_menus import (
    TitleScreen,
    SaveSlotSelectScreen,
    SaveDialog,
    TrainerCustomizationScreen,
    PauseMenu,
    ShopScreen
)
from ui_dialogs import (
    DialogueBox,
    MoveRerollScreen
)
from ui_screens import (
    PokedexScreen,
    PartySummaryScreen,
    BagScreen,
    PCBoxScreen,
    TrainerCardScreen,
    QuestLogScreen
)

# StarterSelectScreen alias / compatibility if needed
StarterSelectScreen = TrainerCustomizationScreen

__all__ = [
    "TitleScreen",
    "SaveSlotSelectScreen",
    "SaveDialog",
    "TrainerCustomizationScreen",
    "StarterSelectScreen",
    "PauseMenu",
    "ShopScreen",
    "DialogueBox",
    "MoveRerollScreen",
    "PokedexScreen",
    "PartySummaryScreen",
    "BagScreen",
    "PCBoxScreen",
    "TrainerCardScreen",
    "QuestLogScreen",
]
