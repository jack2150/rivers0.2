; !^+f5::

; get up image, then click the date section and change date
ImageSearch, FoundX, FoundY, A_ScreenWidth / 2, 0, A_ScreenWidth, A_ScreenHeight / 2, *3 up_date_button_xl.bmp
Sleep, 100
MouseClick, left, FoundX - 20, FoundY + 10, 1, 1

; wait for 0.2 secs
Sleep, 200

; select date text
Send ^a

Sleep, 200

; pass date
; sendinput, %Clipboard%
Send ^v 

; enter to get date
Send {Enter}
; MsgBox % %Clipboard%

; wait for 3 secs
Sleep, 4000

; check is trading day
ImageSearch, FoundM, FoundN, 0, 0, A_ScreenWidth, A_ScreenHeight / 2, *3 trading_day_xl.bmp
Sleep, 100

if ErrorLevel = 2 
	; MsgBox Could not conduct the search.
	Sleep, 200
else if ErrorLevel = 1
	; MsgBox Icon could not be found on the screen.
	Sleep, 200
else {
	; run export
	#Include export_file.ahk
    ; MsgBox The icon was found at %FoundM%x%FoundN%.
}
	