# X-Drive Stress Test
This script will stress the X-Drive in two ways:
* copying a 500MB file to the local computer
* manually seaching every folder in a large tree
Each will be done 5 times and the result averaged.
* now uses `xcopy` instead of `shutil.copy()`

## Python Solution
Use Python 3 to run the contents of [networkTest.py](networkTest.py)

#### Output
```
walking the entire tree of: X:\Data\DIC2\2014
(1/5) scanned 976 folders in 9.959 seconds
(2/5) scanned 976 folders in 8.234 seconds
(3/5) scanned 976 folders in 6.439 seconds
(4/5) scanned 976 folders in 5.795 seconds
(5/5) scanned 976 folders in 6.651 seconds
Average time for 5 runs: 7.416 seconds

copying a HUGE file: X:\...\2017-05-11 cell3_annotated.tif
(1/5) copy took 11.413 seconds (38.470 MB/s)
(2/5) copy took 12.155 seconds (36.122 MB/s)
(3/5) copy took 15.876 seconds (27.655 MB/s)
(4/5) copy took 25.751 seconds (17.050 MB/s)
(5/5) copy took 24.775 seconds (17.722 MB/s)
Average time for 5 runs: 17.994 seconds
```

# Powershell Solution
_You have to run the one line in AllowScript, then you can execute bandwidthtest2.ps1 from your computer in the Powershell ISE.  If you want to do this you’d need to change the local path to match something on your computer._

**AllowScript:**
```PowerShell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Unrestricted
```

**networkTest:**
```PowerShell
# SET THE SOURCE NETWORK
#$SourcePath = "X:\"
#$SourcePath = "\\192.168.1.100\X_Mirror"
$SourcePath = "\\10.15.132.121\X_Mirror"

# INDICATE WHICH FILE TO COPY
$FileName = "benchBig"
#$FileName = "benchSmall"

# THIS LOCAL PATH MUST EXIST
$TargetPath = "D:\zTemp"
$FileSize = (Get-ChildItem $SourcePath\$FileName -ErrorAction Stop).Length
$OutputFile = 'D:\zTemp\bench.txt'
$iNumTrials = 5
$AveDown=$AveUp=0
For ($i=0;$i -lt $iNumTrials-1; $i++){
   $TimeDown = Measure-Command { Copy-Item $SourcePath\$FileName $TargetPath\$FileName }
   $TimeUp = Measure-Command { Copy-Item $TargetPath\$FileName $SourcePath\$FileName }
   $MbpsDown = [Math]::Round((($FileSize * 8) / $TimeDown.TotalSeconds) / 1048576,2)
   $MbpsUp = [Math]::Round((($FileSize * 8) / $TimeUp.TotalSeconds) / 1048576,2)
   Write-Output "$MbpsDown, $MbpsUp"| Out-File $OutputFile -Append
   Write-Output "   MbpsDown: $MbpsDown    MbpsUp: $MbpsUp"
   $AveDown+=$MbpsDown
   $AveUp+=$MbpsUp
}
 $AveDown/=($iNumTrials-1)
 $AveUp/=($iNumTrials-1)
 Write-Output "   AveDown: $AveDown   AveUp: $AveUp"
```

# Scott's computer - X-Drive as source
```
PS C:\Users\swharden> X:\Users_Public\Frazier\Teagan Science Fair\Bandwidth Test 2.ps1
   MbpsDown: 399.04    MbpsUp: 197.79
   MbpsDown: 400.71    MbpsUp: 199.32
   MbpsDown: 400.15    MbpsUp: 197.74
   MbpsDown: 389.55    MbpsUp: 208.32
   AveDown: 317.89   AveUp: 160.634
```
# Scott's computer - X-Mirror as source
```
PS C:\Users\swharden> X:\Users_Public\Frazier\Teagan Science Fair\Bandwidth Test 2.ps1
   MbpsDown: 214.76    MbpsUp: 607.99
   MbpsDown: 886.3    MbpsUp: 700.08
   MbpsDown: 889.1    MbpsUp: 796.86
   MbpsDown: 887.18    MbpsUp: 786.2
   AveDown: 575.468   AveUp: 578.226
```
#### Output
![](powershell.png)

# Comparison of LAN (192.x) vs Shands (10.x) on 2017-08-31
The above script was run comparing the local gigabit LAN vs. the shands lan accessing the same file on the same shared drive. Be sure to disable the network card you don't intend to test in the network adapter manager.

## Large File Transfer (163 MB)
### ***Internal LAN:*** 
```
   MbpsDown: 858.69    MbpsUp: 593.06
   MbpsDown: 872.56    MbpsUp: 777.98
   MbpsDown: 843.37    MbpsUp: 739.14
   MbpsDown: 874.46    MbpsUp: 501.51
   AveDown: 862.27   AveUp: 652.9225
```

### ***Shands LAN:*** 
```
   MbpsDown: 25.95    MbpsUp: 89.82
   AveDown: 25.95   AveUp: 89.82
```
