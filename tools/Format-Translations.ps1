function Format-File {
    param (
        [string]$sourceContent
    )
    $tmp = $sourceContent
    $tmp = $tmp -replace 'xref:aspnetcore-3.0', 'https://docs.microsoft.com/en-us/aspnet/core/release-notes/aspnetcore-3.0'
    $tmp = $tmp -replace 'xref:System.Text.Json', 'https://docs.microsoft.com/en-us/dotnet/api/system.text.json'
    $tmp = $tmp -replace 'xref:Microsoft.AspNetCore.Http.IHttpContextAccessor.HttpContext', 'https://docs.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.http.ihttpcontextaccessor.httpcontext?view=aspnetcore-3.1#Microsoft_AspNetCore_Http_IHttpContextAccessor_HttpContext'
    $tmp = $tmp -replace 'xref:Microsoft.AspNetCore.Http.IHttpContextAccessor', 'https://docs.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.http.ihttpcontextaccessor?view=aspnetcore-3.1#Microsoft_AspNetCore_Http_IHttpContextAccessor'
    $tmp = $tmp -replace 'xref:Microsoft.Extensions.DependencyInjection.IServiceScopeFactory', 'https://docs.microsoft.com/en-us/dotnet/api/microsoft.extensions.dependencyinjection.iservicescopefactory'
    $tmp = $tmp -replace 'xref:(\S+)\*([>\)])', 'https://docs.microsoft.com/en-us/dotnet/api/$1$2'
    $tmp = $tmp -replace 'xref:(\S+)([>\)])', 'https://docs.microsoft.com/en-us/aspnet/core/$1?view=aspnetcore-3.1$2'
    $tmp = $tmp -replace '(\]\()(/)(\S+)(\))', '$1https://docs.microsoft.com/en-us/$3$4'
    $tmp
}

Get-ChildItem ./Newbe.Translations -Filter *.md | ForEach-Object {
    $content = Get-Content $_.FullName -raw
    $resultContent = Format-File -sourceContent $content
    $resultContent | Out-File "..\source\_posts\Newbe.Translations\$($_.Name)" -Force
}