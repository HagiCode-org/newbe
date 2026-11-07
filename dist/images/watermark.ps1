function Mark {
    param (
        [string]$file,
        [string]$text
    )
    magick.exe convert $file -fill grey -pointsize 20 -gravity NorthWest -draw "text 20,20 '$text'" -gravity SouthWest -draw "text 20,20 '$text'" -gravity SouthEast -draw "text 20,20 '$text'" $file
}

$cacheFilename = "watered_files.txt"
if (-not (Test-Path $cacheFilename)) {
    New-Item $cacheFilename -ItemType File
}
$cache = Get-Content $cacheFilename
Get-ChildItem *-*.* | ForEach-Object {
    if ($cache -contains $_.Name) {
        Write-Output "$($_.Name) has been watered"    
    }
    else {
        Write-Output "processing $($_.Name)"
        Mark -file $_ -text "newbe.hagicode.com"
        $_.Name | Out-File $cacheFilename -Append
        Write-Output "processed $($_.Name)"
    }
}
