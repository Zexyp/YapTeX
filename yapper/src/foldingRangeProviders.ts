import * as vscode from 'vscode';

export class RegionFoldingRangeProvider implements vscode.FoldingRangeProvider {
    public provideFoldingRanges(document: vscode.TextDocument, context: vscode.FoldingContext, token: vscode.CancellationToken): vscode.FoldingRange[] {
        const ranges: vscode.FoldingRange[] = [];
        const text = document.getText();
        const lines = text.split('\n');

        const stack: number[] = [];

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];

            if (line.startsWith('#region')) {
                stack.push(i);
            }

            if (line.startsWith('#endregion') && stack.length > 0) {
                const startLine = stack.pop()!;
                const range = new vscode.FoldingRange(startLine, i);
                ranges.push(range);
            }
        }

        return ranges;
    }
}

export class DynheaderFoldingRangeProvider implements vscode.FoldingRangeProvider {
    public provideFoldingRanges(document: vscode.TextDocument, context: vscode.FoldingContext, token: vscode.CancellationToken): vscode.FoldingRange[] {
        const ranges: vscode.FoldingRange[] = [];
        const text = document.getText();
        const lines = text.split('\n');

        const stack: number[] = [];
        const regexDynheader = /^-(#+)\s/;
        const regexHeader = /^#+\s/;
        
        let lastDynheaderLevel: number | null = null;
        let lastInterruptFeature: number | null = -1;

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];

            const match = line.match(regexDynheader);
            if (match) {
                let dynheaderLevel = match[1].length;
                lastInterruptFeature = null;

                if (lastDynheaderLevel === null) {
                    stack.push(i);
                    lastDynheaderLevel = dynheaderLevel;
                } else {
                    if (dynheaderLevel > lastDynheaderLevel) {
                        stack.push(i);
                        lastDynheaderLevel = dynheaderLevel;
                    } else if (dynheaderLevel == lastDynheaderLevel) {
                        ranges.push(new vscode.FoldingRange(stack.pop()!, i - 1));
                        
                        // start new fold
                        stack.push(i);
                    } else {
                        while (stack.length && lastDynheaderLevel > dynheaderLevel) {
                            ranges.push(new vscode.FoldingRange(stack.pop()!, i - 1));
                            lastDynheaderLevel -= 1;
                        }
                    }
                }
            }
            else if (line.match(regexHeader) || line.startsWith("#region") || line.startsWith("#endregion")) { // reset on interrupt feature
                while (stack.length) {
                    ranges.push(new vscode.FoldingRange(stack.pop()!, i - 1));
                }

                // clear for next header
                lastDynheaderLevel = null;
                lastInterruptFeature = i;
            }
        }

        // close open folds
        const end = lastInterruptFeature ?? lines.length;
        while (stack.length) {
            ranges.push(new vscode.FoldingRange(stack.pop()!, end - 1));
        }

        return ranges;
    }
}