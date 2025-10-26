' 量化投资助手 - 静默启动脚本
' 无命令行窗口，直接后台启动

Set WshShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' 获取脚本所在目录
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' 构建启动命令
strCommand = "cmd /c cd /d """ & strScriptPath & """ && streamlit run main.py --server.port=8503 --server.headless=true"

' 静默启动（0 = 隐藏窗口，True = 等待完成）
WshShell.Run strCommand, 0, False

' 等待2秒后打开浏览器
WScript.Sleep 2000
WshShell.Run "http://localhost:8503", 1, False

' 显示提示
MsgBox "量化投资助手已启动！" & vbCrLf & vbCrLf & _
       "访问地址: http://localhost:8503" & vbCrLf & _
       "关闭浏览器不会停止服务" & vbCrLf & vbCrLf & _
       "要停止服务，请在任务管理器中结束Python进程", _
       vbInformation, "Apple风格量化助手"
