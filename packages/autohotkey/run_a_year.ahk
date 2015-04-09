!^+f5::
runWeeks = 52

Loop
{
		if a_index > %runWeeks%
			break  ; Terminate the loop

		#Include run_a_week.ahk
		
		; wait for 2 sec
		; Sleep, 250
}


