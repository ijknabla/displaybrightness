
import pyautogui
import ctypes
from ctypes import byref
from ctypes import wintypes
from ctypes import windll


# user32.dll の関数への宣言

user32   = windll.user32

from enum import Enum
class MONITOR_FLAG(int, Enum):
    DEFAULTTONULL    = 0x00000000
    DEFAULTTOPRIMARY = 0x00000001
    DEFAULTTONEAREST = 0x00000002

user32.MonitorFromPoint.restype = wintypes.HANDLE
user32.MonitorFromPoint.argtypes = (
    wintypes.POINT  , # pt
    wintypes.DWORD  , # dwFlags
    )


# Dxva.dll の関数への宣言

Dxva2DLL = windll.Dxva2

PHYSICAL_MONITOR_DESCRIPTION_SIZE = 128
class PHYSICAL_MONITOR(ctypes.Structure):
    _fields_ = [
        ("hPhysicalMonitor",
         wintypes.HANDLE),
        ("szPhysicalMonitorDesctiption",
         wintypes.WCHAR * PHYSICAL_MONITOR_DESCRIPTION_SIZE),
        ]

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"hPhysicalMonitor={self.hPhysicalMonitor!r}, "
            f"szPhysicalMonitorDesctiption={self.szPhysicalMonitorDesctiption!r}"
            f")"
            )

LPPHYSICAL_MONITOR = ctypes.POINTER(
    PHYSICAL_MONITOR
    )

Dxva2DLL.GetNumberOfPhysicalMonitorsFromHMONITOR.restype = wintypes.BOOL
Dxva2DLL.GetNumberOfPhysicalMonitorsFromHMONITOR.argtypes = (
    wintypes.HANDLE , # hMonitor
    wintypes.LPDWORD, # pdwNumberOfPhysicalMonitors
)

Dxva2DLL.GetPhysicalMonitorsFromHMONITOR.restype = wintypes.BOOL
Dxva2DLL.GetPhysicalMonitorsFromHMONITOR.argtypes = (
    wintypes.HANDLE , # hMonitor
    wintypes.DWORD  , # dwPhysicalMonitorArraySize
    LPPHYSICAL_MONITOR, # pPhysicalMonitorArray
    ) 

Dxva2DLL.GetMonitorBrightness.restype = wintypes.BOOL
Dxva2DLL.GetMonitorBrightness.argtypes = (
    wintypes.HANDLE , # hMonitor
    wintypes.LPDWORD, # pdwMinimumBrightness
    wintypes.LPDWORD, # pdwCurrentBrightness
    wintypes.LPDWORD, # pdwMaximumBrightness
)

Dxva2DLL.SetMonitorBrightness.restype = wintypes.BOOL
Dxva2DLL.SetMonitorBrightness.argtypes = (
    wintypes.HANDLE , # hMonitor
    wintypes.DWORD  , # dwNewBrightness
    )

def getCurrentPositionWinPoint():
    return wintypes.POINT(*pyautogui.position())

def getCurrentPositionMonitorHandle():
    return user32.MonitorFromPoint(
        getCurrentPositionWinPoint(),
        MONITOR_FLAG.DEFAULTTONEAREST
        )


def getMonitorBrightness(hMonitor = None):
    if hMonitor is None:
        hMonitor = getCurrentPositionMonitorHandle()

    numberOfPhysicalMonitors = wintypes.DWORD()

    result = Dxva2DLL.GetNumberOfPhysicalMonitorsFromHMONITOR(
        hMonitor,
        numberOfPhysicalMonitors,
        )

    physicalMonitorArray = (PHYSICAL_MONITOR * numberOfPhysicalMonitors.value) ()

    result = Dxva2DLL.GetPhysicalMonitorsFromHMONITOR(
        hMonitor,
        numberOfPhysicalMonitors,
        physicalMonitorArray,
        )
    
    result = Dxva2DLL.GetNumberOfPhysicalMonitorsFromHMONITOR(
        hMonitor,
        numberOfPhysicalMonitors,
        )

    minimumBrightness = wintypes.DWORD()
    currentBrightness = wintypes.DWORD()
    maximumBrightness = wintypes.DWORD()

    result = Dxva2DLL.GetMonitorBrightness(
        physicalMonitorArray[0].hPhysicalMonitor,
        minimumBrightness,
        currentBrightness,
        maximumBrightness,
        )

    from operator import attrgetter

    return tuple(map(
        attrgetter("value"),
        [
            minimumBrightness,
            currentBrightness,
            maximumBrightness,
            ]
        ))

def setMonitorBrightness(brightness, hMonitor = None):
    if hMonitor is None:
        hMonitor = getCurrentPositionMonitorHandle()

    numberOfPhysicalMonitors = wintypes.DWORD()

    result = Dxva2DLL.GetNumberOfPhysicalMonitorsFromHMONITOR(
        hMonitor,
        numberOfPhysicalMonitors,
        )

    physicalMonitorArray = (PHYSICAL_MONITOR * numberOfPhysicalMonitors.value) ()

    result = Dxva2DLL.GetPhysicalMonitorsFromHMONITOR(
        hMonitor,
        numberOfPhysicalMonitors,
        physicalMonitorArray,
        )
    
    result = Dxva2DLL.GetNumberOfPhysicalMonitorsFromHMONITOR(
        hMonitor,
        numberOfPhysicalMonitors,
        )

    minimumBrightness = wintypes.DWORD()
    currentBrightness = wintypes.DWORD()
    maximumBrightness = wintypes.DWORD()

    result = Dxva2DLL.SetMonitorBrightness(
        physicalMonitorArray[0].hPhysicalMonitor,
        brightness,
        )

    return

def changeBrightness(diff):
    minBright, currentBright, maxBright = getMonitorBrightness()
    changedBrightNess = currentBright + diff
    setMonitorBrightness(max(minBright, min(maxBright, changedBrightNess)))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--brighten", type=int)
    parser.add_argument("--darken"  , type=int)

    args = parser.parse_args()

    if args.brighten:
        changeBrightness(+args.brighten)
    else:
        changeBrightness(-args.darken)
    
    
    
