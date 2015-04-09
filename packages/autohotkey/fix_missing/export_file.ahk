; !^+f5::
; Move the mouse to a new position:
CoordMode Pixel  
CoordMode, ToolTip, Screen  

; click the up date button
ImageSearch, FoundX, FoundY, 0, 0, A_ScreenWidth, A_ScreenHeight, *3 export_button_xl.bmp
Sleep, 100
MouseClick, left, FoundX, FoundY, 1, 0

; wait for popup
Sleep, 500

; click export file 
ImageSearch, FoundA, FoundB, 0, 0, A_ScreenWidth, A_ScreenHeight, *3 export_file_xl.bmp
Sleep, 100
MouseClick, left, FoundA, FoundB, 1, 0

; press enter to export data
Sleep, 200
Send {Enter}

; wait for 0.5 sec
Sleep, 500
