set visibleWindows to ""
set message to ""

tell application "System Events"
    set listOfProcesses to (name of every process where background only is false)
    repeat with visibleProcess in listOfProcesses
        try
            tell process visibleProcess to set visibleWindows to visibleWindows & (id of windows whose visible is true)
        on error someError
            set message to "Some error occured :" & someError
        end try
    end repeat
end tell

return {visibleWindows, listOfProcesses, message}
