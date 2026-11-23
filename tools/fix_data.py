"""Fix of the Day: Nov 22 2026 to Jan 31 2027, posted 2 PM ET. Edit here, then run build_month_tree.py."""
PS = "Open PowerShell as Administrator and run:"
PSU = "Open PowerShell and run:"
CMD = "Open Command Prompt as Administrator and run:"
CMDU = "Open Command Prompt and run:"

FIXES = [
 dict(date="2026-11-22", res="spooler", problem="PRINT JOB STUCK IN THE QUEUE?",
  sub="Windows 10 and 11. Needs admin. About 30 seconds.",
  david="Printer says \"printing\" for three hours? Don't reinstall it. Restart the spooler and clear the queue.",
  runin=PS, code=["# Run PowerShell as Administrator", "Stop-Service -Name Spooler -Force",
   "Remove-Item \"$env:SystemRoot\\System32\\spool\\PRINTERS\\*\" -Force", "Start-Service -Name Spooler"],
  warn="Clears every queued print job. Save your work first.",
  why="jobs wait in a folder. One bad file blocks the rest.", tags="#PrinterProblems #PowerShell"),

 dict(date="2026-11-23", res="restore point", problem="ABOUT TO CHANGE SOMETHING RISKY?",
  sub="Windows PowerShell 5.1. Needs admin. System Protection must be on.",
  david="Before you touch the registry, drivers or updates, make a restore point. It takes ten seconds and saves the weekend.",
  runin=PS, code=["# Run Windows PowerShell as Administrator", "Checkpoint-Computer -Description \"Before the fix\" `",
   "  -RestorePointType MODIFY_SETTINGS"],
  warn="Windows allows one restore point per 24 hours by default.",
  why="you get a clean way back if the fix makes things worse.", tags="#Backup #PowerShell"),

 dict(date="2026-11-24", res="sfc and DISM", problem="WINDOWS ACTING WEIRD FOR NO REASON?",
  sub="Windows 10 and 11. Needs admin. Takes 10 to 30 minutes.",
  david="Random crashes, broken apps, odd errors? Repair the Windows image first, then scan the system files.",
  runin=CMD, code=["# Run Command Prompt as Administrator", "DISM /Online /Cleanup-Image /RestoreHealth", "sfc /scannow"],
  warn="Let both finish. Closing the window halfway helps nobody.",
  why="DISM repairs the source files, then sfc uses them to fix the rest.", tags="#Windows11 #SFC"),

 dict(date="2026-11-25", res="new IP", problem="WI-FI CONNECTED BUT NO INTERNET?",
  sub="Windows 10 and 11. Needs admin. Not for static IP setups.",
  david="Connected, no internet? Release the old address, ask for a new one, and flush the DNS cache.",
  runin=CMD, code=["# Run Command Prompt as Administrator", "ipconfig /release", "ipconfig /renew", "ipconfig /flushdns"],
  warn="This drops the connection for a few seconds. Don't run it over a remote session.",
  why="a stale address or cache is a common cause of no internet.", tags="#WiFi #Networking"),

 dict(date="2026-11-26", res="it was DNS", problem="IS IT DNS OR IS IT THE NETWORK?",
  sub="Windows 10 and 11. No admin needed. Takes 5 seconds.",
  david="Two commands tell you which one. Name lookup first, then a connection test. It's DNS more often than anyone admits.",
  runin=PS, code=["Resolve-DnsName microsoft.com", "Test-NetConnection microsoft.com -Port 443"],
  warn="Lookup fails? DNS. Lookup works but the test fails? Check the network or firewall.",
  why="the first command tests names, the second tests the path.", tags="#DNS #Networking"),

 dict(date="2026-11-27", res="explorer restarted", problem="TASKBAR OR START MENU FROZEN?",
  sub="Windows 10 and 11. No admin needed. Takes 5 seconds.",
  david="Taskbar dead? Start menu stuck? Restart Explorer. Windows brings it back on its own.",
  runin=PS, code=["# Windows relaunches it in a second", "Stop-Process -Name explorer -Force"],
  warn="Open File Explorer windows will close. Save anything in them first.",
  why="the desktop shell is just a process, and it can be restarted.", tags="#Windows11 #Explorer"),

 dict(date="2026-11-28", res="killed", problem="APP FROZEN AND WON'T CLOSE?",
  sub="Windows 10 and 11. No admin needed for your own apps.",
  david="Look at what's frozen before you kill anything. Step one lists it. Step two closes it.",
  runin=PS, code=["# Step 1: list the frozen ones", "Get-Process | Where-Object { -not $_.Responding }",
   "# Step 2: close them", "Get-Process | Where-Object { -not $_.Responding } | Stop-Process -Force"],
  warn="Unsaved work in those apps is gone. Check the list first.",
  why="Windows flags apps that stop answering, so you can target only those.", tags="#TaskManager #PowerShell"),

 dict(date="2026-11-29", res="restart (the real one)", problem="THIS PC HAS BEEN UP 43 DAYS?",
  sub="Windows 10 and 11. No admin needed. Takes 5 seconds.",
  david="\"I restart it every night.\" Let's check. Shut down is not restart when Fast Startup is on.",
  runin=PS, code=["$boot = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime", "(Get-Date) - $boot"],
  warn="Use Restart, not Shut down, for a full reboot.",
  why="Fast Startup saves the kernel session, so Shut down skips a true boot.", tags="#FastStartup #Windows11"),

 dict(date="2026-11-30", res="update unstuck", problem="WINDOWS UPDATE STUCK OR FAILING?",
  sub="Windows 10 and 11. Needs admin. Restart afterward.",
  david="Update stuck at the same percent? Stop the update services, rename the download cache, start them again.",
  runin=PS, code=["Stop-Service -Name wuauserv, bits -Force",
   "Rename-Item \"$env:SystemRoot\\SoftwareDistribution\" `", "  -NewName SoftwareDistribution.old",
   "Start-Service -Name wuauserv, bits"],
  warn="Update history resets. Delete the .old folder later once updates work.",
  why="a corrupt download cache blocks every retry. Windows rebuilds a fresh one.", tags="#WindowsUpdate #Patching"),

 dict(date="2026-12-01", res="drive remapped", problem="MAPPED DRIVE SHOWS A RED X?",
  sub="Windows 10 and 11. No admin needed.",
  david="Drop the dead mapping and map it again. Swap in your own drive letter and path.",
  runin=CMD, code=["net use Z: /delete", "net use Z: \\\\fileserver\\share /persistent:yes"],
  warn="Z: and \\\\fileserver\\share are examples. Use your own.",
  why="a stale session to the server keeps the old mapping broken.", tags="#FileShare #Networking"),

 dict(date="2026-12-02", res="temp cleared", problem="PC SLOW AND DISK ALMOST FULL?",
  sub="Windows 10 and 11. No admin needed. Takes a minute.",
  david="Your temp folder is a junk drawer. Empty it. Anything in use is skipped, so it's safe.",
  runin=PS, code=["Remove-Item \"$env:TEMP\\*\" -Recurse -Force -ErrorAction SilentlyContinue"],
  warn="Close your apps first so fewer files are locked.",
  why="apps leave temp files behind and rarely clean up.", tags="#DiskSpace #Cleanup"),

 dict(date="2026-12-03", res="clock synced", problem="LOGIN OR CERTIFICATE ERRORS? CHECK THE CLOCK.",
  sub="Windows 10 and 11. Needs admin.",
  david="Wrong time breaks sign-in and HTTPS. Check the offset, then force a sync.",
  runin=CMD, code=["# Run Command Prompt as Administrator", "w32tm /query /status", "w32tm /resync"],
  warn="Domain PCs sync from the domain. A bad offset can mean a deeper problem.",
  why="Kerberos and certificates need clocks within minutes of each other.", tags="#Kerberos #TimeSync"),

 dict(date="2026-12-04", res="disk checked", problem="WORRIED ABOUT DISK ERRORS?",
  sub="Windows 10 and 11. Needs admin. The scan runs while Windows is on.",
  david="Run the online scan first. It checks the disk without taking the PC down.",
  runin=CMD, code=["# Run Command Prompt as Administrator", "chkdsk C: /scan",
   "# Errors found? chkdsk C: /f (needs a reboot)"],
  warn="Back up first if the disk is making noises or SMART is failing.",
  why="most file system problems show up in a scan before they become a crash.", tags="#Chkdsk #Storage"),

 dict(date="2026-12-05", res="safe mode", problem="OUTLOOK STUCK ON LOADING PROFILE?",
  sub="Microsoft 365 and Outlook desktop. No admin needed.",
  david="Start Outlook without add-ins. Press Win+R and type one of these.",
  runin="Press Win+R and run:", code=["outlook.exe /safe", "# Still odd? Reset the navigation pane", "outlook.exe /resetnavpane"],
  warn="/resetnavpane resets your folder pane layout and favorites.",
  why="a bad add-in is a common reason Outlook hangs on startup.", tags="#Outlook #Microsoft365"),

 dict(date="2026-12-06", res="reindexed", problem="WINDOWS SEARCH FINDS NOTHING?",
  sub="Windows 10 and 11. Needs admin.",
  david="Search finds nothing? Restart the search service before you rebuild anything.",
  runin=PS, code=["Restart-Service -Name WSearch", "Get-Service -Name WSearch"],
  warn="Still empty after that? Rebuild the index in Indexing Options.",
  why="the service can hang, and a restart is quicker than a rebuild.", tags="#WindowsSearch #Windows11"),

 dict(date="2026-12-07", res="sound back", problem="NO SOUND AND THE VOLUME IS FINE?",
  sub="Windows 10 and 11. Needs admin.",
  david="Before you reinstall drivers, restart the audio service.",
  runin=PS, code=["Restart-Service -Name Audiosrv -Force"],
  warn="Audio may cut out for a second while it restarts.",
  why="the audio service can stall after sleep, a dock change or an update.", tags="#Audio #Troubleshooting"),

 dict(date="2026-12-08", res="policy applied", problem="GROUP POLICY NOT APPLYING?",
  sub="Domain-joined PCs. Needs admin.",
  david="Force a refresh, then see which policies actually landed.",
  runin=CMD, code=["# Run Command Prompt as Administrator", "gpupdate /force", "gpresult /r"],
  warn="Some settings only apply after a sign-out or a restart.",
  why="gpresult shows what applied and which policies were filtered out.", tags="#GroupPolicy #ActiveDirectory"),

 dict(date="2026-12-09", res="scanned", problem="WANT A QUICK DEFENDER SCAN?",
  sub="Windows 10 and 11. Needs admin. Microsoft Defender only.",
  david="Update the definitions, run a quick scan, then list anything it found.",
  runin=PS, code=["Update-MpSignature", "Start-MpScan -ScanType QuickScan", "Get-MpThreat"],
  warn="Another antivirus in charge? Defender may be in passive mode.",
  why="fresh definitions matter more than the scan itself.", tags="#Defender #Security"),

 dict(date="2026-12-10", res="serial found", problem="SUPPORT WANTS THE SERIAL NUMBER?",
  sub="Windows 10 and 11. No admin needed. Takes 5 seconds.",
  david="No flipping the laptop over. Ask Windows for the serial number, make and model.",
  runin=PS, code=["Get-CimInstance Win32_BIOS | Select-Object SerialNumber",
   "Get-CimInstance Win32_ComputerSystem |", "  Select-Object Manufacturer, Model"],
  warn="Some custom builds return a blank or placeholder serial.",
  why="the BIOS stores it, so Windows can read it without a screwdriver.", tags="#AssetManagement #PowerShell"),

 dict(date="2026-12-11", res="space reclaimed", problem="WHAT IS EATING THE DISK?",
  sub="Windows 10 and 11. No admin needed for your own files.",
  david="Find the ten biggest files under Users before you delete anything.",
  runin=PS, code=["Get-ChildItem C:\\Users -Recurse -File -ErrorAction SilentlyContinue |",
   "  Sort-Object Length -Descending |", "  Select-Object -First 10 FullName, Length"],
  warn="Slow on big drives. Don't delete anything you haven't checked.",
  why="Length is in bytes, sorted largest first.", tags="#DiskSpace #PowerShell"),

 dict(date="2026-12-12", res="stack reset", problem="NETWORK STACK TOTALLY CONFUSED?",
  sub="Windows 10 and 11. Needs admin. Restart afterward.",
  david="When nothing else works, reset the Winsock catalog and the IP stack, then reboot.",
  runin=CMD, code=["# Run Command Prompt as Administrator", "netsh winsock reset", "netsh int ip reset"],
  warn="Custom network settings, including static IPs, may be reset. Note them first.",
  why="VPN clients and security tools can corrupt the network stack.", tags="#Winsock #Networking"),

 dict(date="2026-12-13", res="port freed", problem="PORT ALREADY IN USE?",
  sub="Windows 10 and 11. No admin needed to look.",
  david="Find the process that owns the port before you start killing things.",
  runin=PS, code=["$conn = Get-NetTCPConnection -LocalPort 8080 -State Listen", "Get-Process -Id $conn.OwningProcess"],
  warn="8080 is an example. Use your port. Don't kill system processes.",
  why="the connection shows which process ID is listening.", tags="#Networking #DevOps"),

 dict(date="2026-12-14", res="key located", problem="BITLOCKER ASKING FOR A RECOVERY KEY?",
  sub="Windows 10 and 11 Pro and up. Needs admin.",
  david="Find the key before the prompt becomes a crisis. Check the protectors and the status.",
  runin=CMD, code=["# Run Command Prompt as Administrator", "manage-bde -protectors -get C:", "manage-bde -status C:"],
  warn="The output shows a recovery password. Treat it like a password. Never post it.",
  why="the key is usually also stored in AD or your account.", tags="#BitLocker #Security"),

 dict(date="2026-12-15", res="unlocked", problem="USER LOCKED OUT AGAIN?",
  sub="Needs RSAT Active Directory tools and unlock rights.",
  david="Find who is locked, then unlock them. Check why before it happens again.",
  runin=PS, code=["Search-ADAccount -LockedOut | Select-Object Name, SamAccountName", "Unlock-ADAccount -Identity jsmith"],
  warn="jsmith is an example. Old saved passwords on phones are a top cause.",
  why="a stale saved password somewhere keeps retrying and re-locks the account.", tags="#ActiveDirectory #Helpdesk"),

 dict(date="2026-12-16", res="trust restored", problem="TRUST RELATIONSHIP FAILED?",
  sub="Domain-joined PCs. Run on the affected PC. Needs domain credentials.",
  david="\"The trust relationship failed.\" Test the secure channel first. Repair it if it's broken.",
  runin=PS, code=["Test-ComputerSecureChannel -Verbose", "Test-ComputerSecureChannel -Repair -Credential (Get-Credential)"],
  warn="Needs a network path to a domain controller and rights to reset the account.",
  why="the PC's password with the domain drifted, and this resets it.", tags="#ActiveDirectory #Domain"),

 dict(date="2026-12-17", res="session found", problem="WHO IS SIGNED IN ON THAT PC?",
  sub="Needs admin rights on the target PC.",
  david="Before you restart it, check who's on it. A quick look at the sessions.",
  runin=CMD, code=["# Who is signed in on PC01?", "quser /server:PC01", "# Shows user, session, state and idle time"],
  warn="PC01 is an example. A firewall may block remote queries.",
  why="restarting a PC someone is using is a good way to make a new ticket.", tags="#RemoteSupport #Helpdesk"),

 dict(date="2026-12-18", res="restart announced", problem="NEED TO RESTART A REMOTE PC POLITELY?",
  sub="Needs admin rights on the target PC. Cancel option included.",
  david="Give people a five-minute warning and a message. Changed your mind? Abort it.",
  runin=CMD, code=["shutdown /r /t 300 /m \\\\PC01 /c \"IT restart in 5 minutes. Save your work.\"",
   "# Changed your mind?", "shutdown /a /m \\\\PC01"],
  warn="PC01 is an example. 300 is seconds.",
  why="the timer gives users a warning, and /a cancels it.", tags="#RemoteSupport #SysAdmin"),

 dict(date="2026-12-19", res="adapter restarted", problem="NETWORK ADAPTER STUCK?",
  sub="Windows 10 and 11. Needs admin.",
  david="List the adapters, then restart the one that's misbehaving. Quicker than a full reboot.",
  runin=PS, code=["Get-NetAdapter", "Restart-NetAdapter -Name \"Wi-Fi\""],
  warn="Drops that connection briefly. Don't do it over a remote session on that adapter.",
  why="it resets the driver and link without a reboot.", tags="#Networking #WiFi"),

 dict(date="2026-12-20", res="crash explained", problem="PC REBOOTED ON ITS OWN?",
  sub="Windows 10 and 11. No admin needed to read the log.",
  david="Event 41 means it restarted without a clean shutdown. Look at the last five.",
  runin=PS, code=["Get-WinEvent -FilterHashtable @{ LogName = 'System'; Id = 41 } |", "  Select-Object -First 5 TimeCreated, Id"],
  warn="No results means no unexpected restarts were logged.",
  why="Kernel-Power 41 is Windows noting the last shutdown was not clean.", tags="#EventViewer #Troubleshooting"),

 dict(date="2026-12-21", res="battery diagnosed", problem="LAPTOP BATTERY DIES IN AN HOUR?",
  sub="Windows 10 and 11 laptops. No admin needed.",
  david="Don't guess. Generate the battery report and compare design capacity to full charge capacity.",
  runin=PS, code=["powercfg /batteryreport /output \"$env:USERPROFILE\\battery.html\"", "Start-Process \"$env:USERPROFILE\\battery.html\""],
  warn="Laptops only. A big gap between the two numbers means the battery is worn.",
  why="the report tracks health, cycles and recent usage.", tags="#Laptop #Battery"),
]

BASE_FB = "#ITHumor #HelpDesk #SysAdmin #FixOfTheDay #TicketClosed"
BASE_IG = "#ITHumor #HelpDesk #SysAdmin #FixOfTheDay #ITSupport #TechHumor #ITLife #DesktopSupport #TicketClosed"


def caption(f, ig=False):
    code = "\n".join(l for l in f["code"] if not l.startswith("# Run "))
    lead = f["david"]
    cap = f"{lead}\n\n{f['runin']}\n{code}\n\nHeads up: {f['warn']} Why it works: {f['why']} Ticket closed. (Resolution: {f['res']}.)"
    if ig:
        cap += "\nSave this for the next time you need it."
    cap += "\n" + f["tags"] + " " + (BASE_IG if ig else BASE_FB)
    return cap
