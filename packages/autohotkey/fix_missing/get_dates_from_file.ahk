!^+f5::

; Write to the array:
ArrayCount = 0
Loop, Read, missing_dates.txt   ; This loop retrieves each line from the file, one at a time.
{
    ArrayCount += 1  ; Keep track of how many items are in the array.
    Array%ArrayCount% := A_LoopReadLine  ; Store this line in the next array element.
}

; Read from the array:
Loop %ArrayCount%
{
    ; The following line uses the := operator to retrieve an array element:
    element := Array%A_Index%  ; A_Index is a built-in variable.
    ; Alternatively, you could use the "% " prefix to make MsgBox or some other command expression-capable:
    MsgBox % "Element number " . A_Index . " is " . Array%A_Index%
}
