// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";
import * as os from "os";
import { spawn } from "child_process";

function getRootWorkspaceFolder(): string | null {
    const folders = vscode.workspace.workspaceFolders;
    
    if (!folders || folders.length !== 1) {
        return null;
    }

    return folders[0].uri.fsPath;
}

// temp dir cache
let lastTempDir: string | null = null;

function getTempDir() {
    if (lastTempDir) return lastTempDir;

    const tempDirPrefix = path.join(os.tmpdir(), "yepper-build");
    return lastTempDir = fs.mkdtempSync(tempDirPrefix);
}

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {
    
    // Use the console to output diagnostic information (console.log) and errors (console.error)
    // This line of code will only be executed once when your extension is activated
    console.log('Congratulations, your extension "yapper" is now active!');
    
    // The command has been defined in the package.json file
    // Now provide the implementation of the command with registerCommand
    // The commandId parameter must match the command field in package.json
    const commandHello = vscode.commands.registerCommand('yapper.helloWorld', () => {
        // The code you place here will be executed every time your command is executed
        // Display a message box to the user
        vscode.window.showInformationMessage('Hello World from Yapper!');
    });

    const commandRun = vscode.commands.registerCommand("yapper.build", async () => {
        const editor = vscode.window.activeTextEditor;
        
        if (!editor) {
            vscode.window.showErrorMessage("No active editor.");
            return;
        }

        // mark-github, beaker, compose
        const targetOptions = [
            {value: null, label: "$(file) None"},
            {value: "md", label: "$(markdown) Markdown"},
            {value: "html", label: "$(file-code) HTML"},
            {value: "pdf", label: "$(sparkle) PDF"}
        ];
        let target = await vscode.window.showQuickPick(
            targetOptions,
            {
                placeHolder: "Target",
                canPickMany: false
            }
        );
        if (!target)
            target = targetOptions[0];

        const config = vscode.workspace.getConfiguration("yapper");
        const cfgEnvironmentPath = config.get<string>("environmentPath") || "";
        const cfgVerbose = config.get<string>("verbose");

        // pick the python inside the venv
        const pythonPath =
        process.platform === "win32"
            ? path.join(cfgEnvironmentPath, "Scripts", "python.exe")
            : path.join(cfgEnvironmentPath, "bin", "python");

        if (!fs.existsSync(pythonPath)) {
            vscode.window.showErrorMessage("YapTeX location not configured.");
            return;
        }

        let workdir = getRootWorkspaceFolder() || getTempDir()
        workdir = path.join(workdir, "yaptex-out")
        
        vscode.window.showInformationMessage("Building...");

        const shouldUseStdin = editor.document.isUntitled

        const args = ["-m", "yaptex", shouldUseStdin ? "-" : editor.document.uri.fsPath, "--output", workdir];
        if (cfgVerbose)
            args.push("--verbose");
        if (target.value)
            args.push("--target", target.value);
        
        const child = spawn(pythonPath, args, {
            stdio: ["pipe", "pipe", "pipe"]
        });

        const outputChannel = vscode.window.createOutputChannel("YapTeX");
        outputChannel.show(true);

        if (shouldUseStdin) {
            const code = editor.document.getText();
            child.stdin.write(code);
        }
        child.stdin.end();

        child.stdout.on("data", (data) => {
            outputChannel.append(data.toString());
        });

        child.stderr.on("data", (data) => {
            outputChannel.append(data.toString());
        });

        child.on("close", (code) => {
            if (code == 0)
                vscode.window.showInformationMessage("Done");
            else
                vscode.window.showErrorMessage(`YapTeX exited with ${code}`);

            switch (target.value) {
                case "md":
                    vscode.commands.executeCommand('markdown.showPreviewToSide', vscode.Uri.file(path.join(workdir, "md", "index.md")));
                    break;
                case "html":
                    vscode.commands.executeCommand(
                        "livePreview.start.internalPreview.atFile",
                        vscode.Uri.file(path.join(workdir, "html", "index.html")),
                        { viewColumn: vscode.ViewColumn.Beside }
                    );
                    break;
            }
        });
    });
    
    context.subscriptions.push(commandHello, commandRun);
}

// This method is called when your extension is deactivated
export function deactivate() {}
