var WshNetwork = new ActiveXObject("WScript.Network");
var userName = WshNetwork.UserName;

Shell = new ActiveXObject("WScript.Shell");
var currentDirectory = Shell.CurrentDirectory;

// Split the current directory path by the backslash delimiter
var pathParts = currentDirectory.split("\\");
var grandparentDirectoryName = pathParts[pathParts.length - 3];

link = Shell.CreateShortcut(currentDirectory + "\\" + grandparentDirectoryName + "_Houdini_" + userName + ".lnk");
link.WorkingDirectory = currentDirectory;
link.Description = "Starts Houdini in a pipelined environment";
link.IconLocation = currentDirectory + "\\Houdini.ico,0";
link.TargetPath = currentDirectory + "\\start_Windows_Houdini_in_this_job.bat";
link.WindowStyle = 7;
link.Save();

