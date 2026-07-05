#Requires AutoHotkey v2.0
#SingleInstance Force

; Whip mode — Ctrl+Alt+W
; Cracks the whip: swaps the system cursor to a whip, plays a crack sound,
; and has a robot voice tell Claude to get back to work. Auto-restores after ~4s.

SPI_SETCURSORS := 0x57
OCR_IDS := [32512, 32513, 32514, 32515, 32516, 32643, 32644, 32645, 32646,
    32648, 32649, 32650, 32651]  ; Arrow, IBeam, Wait, Cross, UpArrow, SizeNWSE,
                                  ; SizeNESW, SizeWE, SizeNS, SizeAll, No, Hand, AppStarting

restoreTimer := 0

; Created once at script load and kept alive as a global — a local COM object
; released right after an async Speak() call gets torn down mid-playback, which
; is why the voice line was cutting out silently.
try {
    gVoice := ComObject("SAPI.SpVoice")
} catch {
    gVoice := ""
}

^!w:: {
    global restoreTimer, OCR_IDS, SPI_SETCURSORS, gVoice
    curPath := A_ScriptDir "\whip.cur"

    for id in OCR_IDS {
        h := DllCall("LoadCursorFromFileW", "Str", curPath, "Ptr")
        if h
            DllCall("SetSystemCursor", "Ptr", h, "Int", id)
    }

    SoundPlay(A_ScriptDir "\whipcrack.wav")

    if gVoice != "" {
        try {
            ; Flag 0 = synchronous — blocks until the line finishes so playback
            ; can never get cut off by the object going out of scope.
            gVoice.Speak('<pitch absmiddle="-10"/><rate absspeed="1"/>Get back to work, Claude!', 0)
        }
    }

    if restoreTimer
        SetTimer(RestoreCursors, 0)
    restoreTimer := SetTimer(RestoreCursors, -4000)
}

RestoreCursors() {
    global SPI_SETCURSORS
    DllCall("SystemParametersInfo", "UInt", SPI_SETCURSORS, "UInt", 0, "Ptr", 0, "UInt", 0)
}
