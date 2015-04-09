; !^+f5::

; click the up button to change date
ImageSearch, FoundX, FoundY, A_ScreenWidth / 2, 0, A_ScreenWidth, A_ScreenHeight / 2, *3 up_date_button_xl.bmp
Sleep, 100
MouseClick, left, FoundX + 5, FoundY + 5, 1, 0

; restart mouse position
MouseMove, FoundX - 200, FoundY - 50, 0

Sleep, 3000

; check is trading day
ImageSearch, FoundM, FoundN, 0, 0, A_ScreenWidth, A_ScreenHeight / 2, *3 trading_day_xl.bmp
Sleep, 100

trading_day_found := 0

if (ErrorLevel = 1)
{
	ImageSearch, Found1, Found2, 0, 0, A_ScreenWidth, A_ScreenHeight / 2, *3 non_trading_day_xl.bmp
	Sleep, 100
	
	if (ErrorLevel = 1) {
		; MsgBox, looking for trading day again
		ErrorLevel := 9
		Found3 := 0
		Found4 := 0
		Sleep, 3000
		ImageSearch, Found3, Found4, 0, 0, A_ScreenWidth, A_ScreenHeight / 2, *3 trading_day_xl.bmp
		Sleep, 100
		
		if (ErrorLevel = 0) {
			; MsgBox, looking for trading day again %Found3% %Found4%	
			trading_day_found := 1
		}
	}
	else {
		; MsgBox, non_trading_day %ErrorLevel% %Found1% %Found2%
	}
	
	
}
else
{
    ; #Include export_file.ahk
	trading_day_found := 1
}

if (trading_day_found = 1) {
	; MsgBox, trading day found
	#Include export_file.ahk
}


; sleep 1 sec
; Sleep, 100