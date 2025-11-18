``` execute_command
[execute_command for 'npx tsc --noEmit'] Result:
Command executed.
Output:
⠙⠙

<environment_details>
# Visual Studio Code Visible Files
src/webview/components/FlowGraph.tsx

# Visual Studio Code Open Tabs
src/webview/components/editors/ExecutionTraceCodeEditor.tsx
src/webview/components/editors/MonacoCodeEditor.tsx
src/webview/components/nodes/FunctionNode.tsx
src/webview/styles/function-node.css
src/webview/types/flowGraph.ts
src/webview/hooks/useExecutionTrace.ts
src/webview/hooks/useDebounce.ts
src/webview/utils/graphLayout.ts
src/webview/utils/flowConversion.ts
src/webview/hooks/useMessageBridge.ts
src/webview/hooks/useGraphHighlighting.ts
src/webview/components/toolbar/FlowGraphToolbar.tsx
src/webview/hooks/useRenderGraph.ts
src/webview/components/FlowGraph.tsx
src/models/Node.ts

# Current Time
11/16/2025, 8:49:19 PM (Asia/Saigon, UTC+7:00)

# Current Mode
ACT MODE
</environment_details>
```

``` task: yêu cầu người dùng
<task>
cleancode file FlowGraph thành các file nhỏ hơn để dễ quản lý
</task>


# task_progress RECOMMENDED

When starting a new task, it is recommended to include a todo list using the task_progress parameter.


1. Include a todo list using the task_progress parameter in your next tool call
2. Create a comprehensive checklist of all steps needed
3. Use markdown format: - [ ] for incomplete, - [x] for complete

**Benefits of creating a todo/task_progress list now:**
	- Clear roadmap for implementation
	- Progress tracking throughout the task
	- Nothing gets forgotten or missed
	- Users can see, monitor, and edit the plan

**Example structure:**```
- [ ] Analyze requirements
- [ ] Set up necessary files
- [ ] Implement main functionality
- [ ] Handle edge cases
- [ ] Test the implementation
- [ ] Verify results```

Keeping the task_progress list updated helps track progress and ensures nothing is missed.


<environment_details>
# Visual Studio Code Visible Files
src/webview/components/FlowGraph.tsx

# Visual Studio Code Open Tabs
src/webview/components/editors/ExecutionTraceCodeEditor.tsx
src/webview/components/editors/MonacoCodeEditor.tsx
src/webview/components/nodes/FunctionNode.tsx
src/webview/styles/function-node.css
src/webview/types/flowGraph.ts
src/webview/hooks/useExecutionTrace.ts
src/webview/hooks/useDebounce.ts
src/webview/utils/graphLayout.ts
src/webview/utils/flowConversion.ts
src/webview/hooks/useMessageBridge.ts
src/webview/components/FlowGraph.tsx
src/models/Node.ts

# Current Time
11/16/2025, 8:33:05 PM (Asia/Saigon, UTC+7:00)

# Current Working Directory (/home/khanhromvn/Documents/Coding/GoFlow) Files
.gitignore
.vscode-test.mjs
.vscodeignore
CHANGELOG.md
eslint.config.mjs
LICENSE
package-lock.json
package.json
README.md
tsconfig.json
webpack.config.js
images/
images/icon.png
media/
media/editor.worker.js
media/editor.worker.js.map
media/flow-canvas.css
media/webview.js
media/webview.js.LICENSE.txt
media/webview.js.map
media/vs/
media/vs/_commonjsHelpers-CT9FvmAN.js
media/vs/abap-D-t0cyap.js
media/vs/apex-CcIm7xu6.js
media/vs/azcli-BA0tQDCg.js
media/vs/bat-C397hTD6.js
media/vs/bicep-DF5aW17k.js
media/vs/cameligo-plsz8qhj.js
media/vs/clojure-Y2auQMzK.js
media/vs/coffee-Bu45yuWE.js
media/vs/cpp-CkKPQIni.js
media/vs/csharp-CX28MZyh.js
media/vs/csp-D8uWnyxW.js
media/vs/css-CaeNmE3S.js
media/vs/cssMode-CGp6dFmI.js
media/vs/cypher-DVThT8BS.js
media/vs/dart-CmGfCvrO.js
media/vs/dockerfile-CZqqYdch.js
media/vs/ecl-30fUercY.js
media/vs/editor.api-i0YVFWkl.js
media/vs/elixir-xjPaIfzF.js
media/vs/flow9-DqtmStfK.js
media/vs/freemarker2-CJME-ah8.js
media/vs/fsharp-BOMdg4U1.js
media/vs/go-D_hbi-Jt.js
media/vs/graphql-CKUU4kLG.js
media/vs/handlebars-NccI6MVO.js
media/vs/hcl-DTaboeZW.js
media/vs/html-K7M-xuod.js
media/vs/htmlMode-DtjCNH-N.js
media/vs/ini-CsNwO04R.js
media/vs/java-CI4ZMsH9.js
media/vs/javascript-CUpTMdAr.js
media/vs/jsonMode-CJjR_ECa.js
media/vs/julia-BwzEvaQw.js
media/vs/kotlin-BLeVJFaw.js
media/vs/less-C0eDYdqa.js
media/vs/lexon-iON-Kj97.js
media/vs/liquid-STktYroN.js
media/vs/loader.js
media/vs/lspLanguageFeatures-A02kBDb6.js
media/vs/lua-DtygF91M.js
media/vs/m3-CsR4AuFi.js
media/vs/markdown-C_rD0bIw.js
media/vs/mdx-C6mq4H94.js
media/vs/mips-CiYP61RB.js
media/vs/msdax-C38-sJlp.js
media/vs/mysql-CdtbpvbG.js
media/vs/nls.messages-loader.js
media/vs/nls.messages.de.js
media/vs/nls.messages.es.js
media/vs/nls.messages.fr.js
media/vs/nls.messages.it.js
media/vs/nls.messages.ja.js
media/vs/nls.messages.ko.js
media/vs/nls.messages.ru.js
media/vs/nls.messages.zh-cn.js
media/vs/nls.messages.zh-tw.js
media/vs/objective-c-CntZFaHX.js
media/vs/pascal-r6kuqfl_.js
media/vs/pascaligo-BiXoTmXh.js
media/vs/perl-DABw_TcH.js
media/vs/pgsql-me_jFXeX.js
media/vs/php-D_kh-9LK.js
media/vs/pla-VfZjczW0.js
media/vs/postiats-BBSzz8Pk.js
media/vs/powerquery-Dt-g_2cc.js
media/vs/powershell-B-7ap1zc.js
media/vs/protobuf-BmtuEB1A.js
media/vs/pug-BRpRNeEb.js
media/vs/python-B-Y2SC3b.js
media/vs/qsharp-BzsFaUU9.js
media/vs/r-f8dDdrp4.js
media/vs/razor-JzN5FpSg.js
media/vs/redis-fvZQY4PI.js
media/vs/redshift-45Et0LQi.js
media/vs/restructuredtext-C7UUFKFD.js
media/vs/ruby-CZO8zYTz.js
media/vs/rust-Bfetafyc.js
media/vs/sb-3GYllVck.js
media/vs/scala-foMgrKo1.js
media/vs/scheme-CHdMtr7p.js
media/vs/scss-C1cmLt9V.js
media/vs/shell-ClXCKCEW.js
media/vs/solidity-MZ6ExpPy.js
media/vs/sophia-DWkuSsPQ.js
media/vs/sparql-AUGFYSyk.js
media/vs/sql-32GpJSV2.js
media/vs/st-CuDFIVZ_.js
media/vs/swift-n-2HociN.js
media/vs/systemverilog-Ch4vA8Yt.js
media/vs/tcl-D74tq1nH.js
media/vs/tsMode-i88JHxDY.js
media/vs/twig-C6taOxMV.js
media/vs/typescript-4zug7YwV.js
media/vs/typespec-D-PIh9Xw.js
media/vs/vb-Dyb2648j.js
media/vs/wgsl-BhLXMOR0.js
media/vs/workers-CbP2cVmy.js
media/vs/xml-DRHZuZwg.js
media/vs/yaml-CkWIGXBM.js
media/vs/assets/
media/vs/assets/css.worker-cO8rX8Iy.js
media/vs/assets/editor.worker-DM0G1eFj.js
media/vs/assets/html.worker-BruuIJkK.js
media/vs/assets/json.worker-DghZTZS7.js
media/vs/assets/ts.worker-C4E4vgbE.js
media/vs/basic-languages/
media/vs/basic-languages/monaco.contribution.js
media/vs/editor/
media/vs/editor/editor.main.css
media/vs/editor/editor.main.js
media/vs/language/
media/vs/language/css/
media/vs/language/css/monaco.contribution.js
media/vs/language/html/
media/vs/language/html/monaco.contribution.js
media/vs/language/json/
media/vs/language/json/monaco.contribution.js
media/vs/language/typescript/
media/vs/language/typescript/monaco.contribution.js
src/
src/extension.ts
src/managers/
src/managers/FlowManager.ts
src/models/
src/models/Node.ts
src/parser/
src/parser/CallOrderTracker.ts
src/parser/DeclarationDetector.ts
src/parser/EdgeDetector.ts
src/parser/GoParser.ts
src/parser/NodeFactory.ts
src/types/
src/types/css.d.ts
src/utils/
src/utils/logger.ts
src/utils/webviewLogger.ts
src/views/
src/views/FlowTreeDataProvider.ts
src/webview/
src/webview/index.tsx
src/webview/WebviewPanel.ts
src/webview/components/
src/webview/components/FlowGraph.tsx
src/webview/components/cards/
src/webview/components/cards/ExecutionTraceCard.tsx
src/webview/components/containers/
src/webview/components/containers/FileGroupContainer.tsx
src/webview/components/drawers/
src/webview/components/drawers/ExecutionTraceDrawer.tsx
src/webview/components/drawers/NodeVisibilityDrawer.tsx
src/webview/components/edges/
src/webview/components/edges/CallOrderEdge.tsx
src/webview/components/editors/
src/webview/components/nodes/
src/webview/configs/
src/webview/configs/graphConfig.ts
src/webview/configs/layoutStrategies.ts
src/webview/hooks/
src/webview/hooks/useDebounce.ts
src/webview/hooks/useExecutionTrace.ts
src/webview/hooks/useMessageBridge.ts
src/webview/styles/
src/webview/styles/common.css
src/webview/styles/declaration-node.css
src/webview/styles/execution-trace-code-editor.css
src/webview/styles/file-group-container.css
src/webview/styles/flow-canvas.css
src/webview/styles/flow-graph.css
src/webview/styles/function-node.css
src/webview/styles/node-visibility-drawer.css
src/webview/types/
src/webview/types/flowGraph.ts
src/webview/utils/
src/webview/utils/EdgeHandleOptimizer.ts
src/webview/utils/EdgeTracker.ts
src/webview/utils/flowConversion.ts
src/webview/utils/graphLayout.ts
src/webview/utils/layoutEngines.ts

(File list truncated. Use list_files on specific subdirectories if you need to explore further.)

# Workspace Configuration
{
  "workspaces": {
    "/home/khanhromvn/Documents/Coding/GoFlow": {
      "hint": "GoFlow",
      "associatedRemoteUrls": [
        "origin: git@github.com:KhanhRomVN/GoFlow.git"
      ],
      "latestGitCommitHash": "97e39dae063e13c8f02651dfe3c708989882410e"
    }
  }
}

# Detected CLI Tools
These are some of the tools on the user's machine, and may be useful if needed to accomplish the task: gh, git, docker, aws, npm, pip, cargo, go, curl, jq, make, cmake, node, psql, redis-cli, sqlite3, code, grep, sed, awk, apt, gradle, wget. This list is not exhaustive, and other tools may be available.

# Current Mode
ACT MODE
</environment_details>
```

```
[read_file for 'src/webview/components/FlowGraph.tsx'] Result:
import type {
  FunctionNodeData,
  DeclarationNodeData,
  FlowNode,
  FlowEdge,
  FlowGraphProps,
} from "../types/flowGraph";

const FlowGraph: React.FC<FlowGraphProps> = ({ vscode }) => {
  return (
  );
};

export default FlowGraph;


<environment_details>
# Visual Studio Code Visible Files
src/webview/components/FlowGraph.tsx

# Visual Studio Code Open Tabs
src/webview/components/editors/ExecutionTraceCodeEditor.tsx
src/webview/components/editors/MonacoCodeEditor.tsx
src/webview/components/nodes/FunctionNode.tsx
src/webview/styles/function-node.css
src/webview/types/flowGraph.ts
src/webview/hooks/useExecutionTrace.ts
src/webview/hooks/useDebounce.ts
src/webview/utils/graphLayout.ts
src/webview/utils/flowConversion.ts
src/webview/hooks/useMessageBridge.ts
src/webview/components/FlowGraph.tsx
src/models/Node.ts

# Current Time
11/16/2025, 8:34:08 PM (Asia/Saigon, UTC+7:00)

# Current Mode
ACT MODE
</environment_details>
```

```
[write_to_file for 'src/webview/hooks/useGraphHighlighting.ts'] Result:
The content was successfully saved to src/webview/hooks/useGraphHighlighting.ts.

Along with your edits, the user's editor applied the following auto-formatting to your content:

@@ -83,9 +83,9 @@
               },
               zIndex: 1000,
             };
           }
-            if (isNodeHighlighted) {
+          if (isNodeHighlighted) {
             return {
               ...edge,
               animated: true,
               style: {
@@ -190,9 +190,9 @@
       // Update edges styling
       setEdges((current) =>
         current.map((edge) => {
           const currentKey = `${edge.source}->${edge.target}`;
-            const isLineHighlighted = lineHighlightedEdges.has(currentKey);
+          const isLineHighlighted = lineHighlightedEdges.has(currentKey);
           const isNodeHighlighted = edgeKeys.has(currentKey);
           const originalDashArray = getOriginalDashArray(edge);
 
           if (isLineHighlighted) {


(Note: Pay close attention to changes such as single quotes being converted to double quotes, semicolons being removed or added, long lines being broken into multiple lines, adjusting indentation style, adding/removing trailing commas, etc. This will help you ensure future SEARCH/REPLACE operations to this file are accurate.)

Here is the full, updated content of the file that was saved:

<final_file_content path="src/webview/hooks/useGraphHighlighting.ts">
import { useState, useCallback } from "react";
import { Edge, Node } from "@xyflow/react";
import { EdgeTracker } from "../utils/EdgeTracker";
import { Logger } from "../../utils/webviewLogger";
import type {
  FunctionNodeData,
  DeclarationNodeData,
  FlowEdge,
  FlowNode,
} from "../types/flowGraph";

/**
 * Encapsulates edge/node highlighting logic that was previously inline in FlowGraph.tsx.
 * This reduces cognitive load in the main component and keeps styling / state mutation cohesive.
 */
export interface UseGraphHighlightingParams {
  edges: FlowEdge[];
  nodes: FlowNode[];
  setEdges: React.Dispatch<React.SetStateAction<FlowEdge[]>>;
  setNodes: React.Dispatch<React.SetStateAction<FlowNode[]>>;
  isGraphReady: boolean;
  vscode: any;
}

export interface UseGraphHighlightingResult {
  lineHighlightedEdges: Set<string>;
  nodeHighlightedEdges: Set<string>;
  highlightedNodeId: string | null;
  handleHighlightEdge: (sourceNodeId: string, targetNodeId: string) => void;
  handleClearHighlight: () => void;
  handleNodeHighlight: (targetNodeId: string) => void;
  handleClearNodeHighlight: () => void;
}

/**
 * Derives original dash array (kept identical to previous logic).
 */
const getOriginalDashArray = (edge: FlowEdge): string | undefined => {
  if (edge.style?.strokeDasharray) return edge.style.strokeDasharray as string;
  if ((edge.data as any)?.dashed === true) return "8 4";
  if ((edge.data as any)?.hasReturnValue === false) return "8 4";
  return undefined;
};

export function useGraphHighlighting({
  edges,
  nodes,
  setEdges,
  setNodes,
  isGraphReady,
  vscode,
}: UseGraphHighlightingParams): UseGraphHighlightingResult {
  const [lineHighlightedEdges, setLineHighlightedEdges] = useState<Set<string>>(
    new Set()
  );
  const [nodeHighlightedEdges, setNodeHighlightedEdges] = useState<Set<string>>(
    new Set()
  );
  const [highlightedNodeId, setHighlightedNodeId] = useState<string | null>(
    null
  );

  const handleHighlightEdge = useCallback(
    (sourceNodeId: string, targetNodeId: string) => {
      const edgeKey = `${sourceNodeId}->${targetNodeId}`;
      setLineHighlightedEdges(new Set([edgeKey]));
      setEdges((current) =>
        current.map((edge) => {
          const currentKey = `${edge.source}->${edge.target}`;
          const isLineHighlighted = currentKey === edgeKey;
          const isNodeHighlighted = nodeHighlightedEdges.has(currentKey);
          const originalDashArray = getOriginalDashArray(edge);

          if (isLineHighlighted) {
            return {
              ...edge,
              animated: true,
              style: {
                ...edge.style,
                stroke: "#FFC107",
                strokeWidth: 4,
                strokeDasharray: originalDashArray,
              },
              zIndex: 1000,
            };
          }
          if (isNodeHighlighted) {
            return {
              ...edge,
              animated: true,
              style: {
                ...edge.style,
                stroke: "#FF6B6B",
                strokeWidth: 3,
                strokeDasharray: originalDashArray,
              },
              zIndex: 999,
            };
          }
          return {
            ...edge,
            animated: false,
            style: {
              ...edge.style,
              stroke: "#666",
              strokeWidth: 2,
              strokeDasharray: originalDashArray,
            },
            zIndex: 1,
          };
        })
      );
    },
    [nodeHighlightedEdges, setEdges]
  );

  const handleClearHighlight = useCallback(() => {
    setLineHighlightedEdges(new Set());
    setEdges((current) =>
      current.map((edge) => {
        const currentKey = `${edge.source}->${edge.target}`;
        const isNodeHighlighted = nodeHighlightedEdges.has(currentKey);
        const originalDashArray = getOriginalDashArray(edge);
        if (isNodeHighlighted) {
          return {
            ...edge,
            animated: true,
            style: {
              ...edge.style,
              stroke: "#FF6B6B",
              strokeWidth: 3,
              strokeDasharray: originalDashArray,
            },
            zIndex: 999,
          };
        }
        return {
          ...edge,
          animated: false,
          style: {
            ...edge.style,
            stroke: "#666",
            strokeWidth: 2,
            strokeDasharray: originalDashArray,
          },
          zIndex: 1,
        };
      })
    );
  }, [nodeHighlightedEdges, setEdges]);

  const handleNodeHighlight = useCallback(
    (targetNodeId: string) => {
      if (!isGraphReady || edges.length === 0 || nodes.length === 0) {
        // Defer using window global (keeps behavior parity with original code)
        (window as any).__goflowPendingNodeHighlight = targetNodeId;
        Logger.debug(
          `[useGraphHighlighting] Graph not ready, queued highlight for ${targetNodeId}`
        );
        return;
      }

      const incomingEdges = edges.filter((e) => e.target === targetNodeId);
      const edgeKeys = new Set(
        incomingEdges.map((e) => `${e.source}->${e.target}`)
      );
      setNodeHighlightedEdges(edgeKeys);
      setHighlightedNodeId(targetNodeId);

      // Trace path to root (unchanged logic)
      const allNodesData = nodes
        .filter((n) => n.type === "functionNode")
        .map((n) => ({
          id: n.id,
          label: (n.data as FunctionNodeData).label,
          type: (n.data as FunctionNodeData).type,
          file: (n.data as FunctionNodeData).file,
          line: (n.data as FunctionNodeData).line,
        }));
      const traced = EdgeTracker.tracePathsToRoot(targetNodeId, allNodesData);
      if (traced) {
        const report = EdgeTracker.getFormattedPathReport(traced);
        vscode.postMessage({
          command: "showPathTrace",
          tracedPath: traced,
          formattedReport: report,
        });
      }

      // Update edges styling
      setEdges((current) =>
        current.map((edge) => {
          const currentKey = `${edge.source}->${edge.target}`;
          const isLineHighlighted = lineHighlightedEdges.has(currentKey);
          const isNodeHighlighted = edgeKeys.has(currentKey);
          const originalDashArray = getOriginalDashArray(edge);

          if (isLineHighlighted) {
            return {
              ...edge,
              animated: true,
              style: {
                ...edge.style,
                stroke: "#FFC107",
                strokeWidth: 4,
                strokeDasharray: originalDashArray,
              },
              zIndex: 1000,
            };
          }
          if (isNodeHighlighted) {
            return {
              ...edge,
              animated: true,
              style: {
                ...edge.style,
                stroke: "#FF6B6B",
                strokeWidth: 3,
                strokeDasharray: originalDashArray,
              },
              zIndex: 999,
            };
          }
          return {
            ...edge,
            animated: false,
            style: {
              ...edge.style,
              stroke: "#666",
              strokeWidth: 2,
              strokeDasharray: originalDashArray,
            },
            zIndex: 1,
          };
        })
      );

      // Update node visuals
      setNodes((currentNodes) =>
        currentNodes.map((node) => {
          const isParent = incomingEdges.some((e) => e.source === node.id);
          const isTarget = node.id === targetNodeId;
          if (isParent || isTarget) {
            return {
              ...node,
              style: {
                ...node.style,
                border: isTarget ? "3px solid #FF6B6B" : "2px solid #FFA500",
                boxShadow: isTarget
                  ? "0 0 10px rgba(255,107,107,0.5)"
                  : "0 0 8px rgba(255,165,0,0.4)",
              },
            };
          }
          return {
            ...node,
            style: {
              ...node.style,
              border: undefined,
              boxShadow: undefined,
            },
          };
        })
      );
    },
    [
      isGraphReady,
      edges,
      nodes,
      setEdges,
      setNodes,
      lineHighlightedEdges,
      vscode,
    ]
  );

  const handleClearNodeHighlight = useCallback(() => {
    setNodeHighlightedEdges(new Set());
    setHighlightedNodeId(null);
    setEdges((current) =>
      current.map((edge) => {
        const currentKey = `${edge.source}->${edge.target}`;
        const isLineHighlighted = lineHighlightedEdges.has(currentKey);
        const originalDashArray = getOriginalDashArray(edge);
        if (isLineHighlighted) {
          return {
            ...edge,
            animated: true,
            style: {
              ...edge.style,
              stroke: "#FFC107",
              strokeWidth: 4,
              strokeDasharray: originalDashArray,
            },
            zIndex: 1000,
          };
        }
        return {
          ...edge,
          animated: false,
          style: {
            ...edge.style,
            stroke: "#666",
            strokeWidth: 2,
            strokeDasharray: originalDashArray,
          },
          zIndex: 1,
        };
      })
    );
    setNodes((currentNodes) =>
      currentNodes.map((node) => ({
        ...node,
        style: {
          ...node.style,
          border: undefined,
          boxShadow: undefined,
        },
      }))
    );
  }, [lineHighlightedEdges, setEdges, setNodes]);

  return {
    lineHighlightedEdges,
    nodeHighlightedEdges,
    highlightedNodeId,
    handleHighlightEdge,
    handleClearHighlight,
    handleNodeHighlight,
    handleClearNodeHighlight,
  };
}

export default useGraphHighlighting;

</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.



<environment_details>
# Visual Studio Code Visible Files
src/webview/hooks/useGraphHighlighting.ts

# Visual Studio Code Open Tabs
src/webview/components/editors/ExecutionTraceCodeEditor.tsx
src/webview/components/editors/MonacoCodeEditor.tsx
src/webview/components/nodes/FunctionNode.tsx
src/webview/styles/function-node.css
src/webview/types/flowGraph.ts
src/webview/hooks/useExecutionTrace.ts
src/webview/hooks/useDebounce.ts
src/webview/utils/graphLayout.ts
src/webview/utils/flowConversion.ts
src/webview/hooks/useMessageBridge.ts
src/webview/components/FlowGraph.tsx
src/webview/hooks/useGraphHighlighting.ts
src/models/Node.ts

# Current Time
11/16/2025, 8:36:29 PM (Asia/Saigon, UTC+7:00)

# Current Mode
ACT MODE
</environment_details>
```

```
[replace_in_file for 'src/webview/components/FlowGraph.tsx'] Result:
The content was successfully saved to src/webview/components/FlowGraph.tsx.

Here is the full, updated content of the file that was saved:

<final_file_content path="src/webview/components/FlowGraph.tsx">
import React, { useCallback, useEffect, useState, useRef } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  Panel,
  useReactFlow,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import "../styles/common.css";
import "../styles/flow-graph.css";
import FunctionNode from "./nodes/FunctionNode";
import FileGroupContainer from "./containers/FileGroupContainer";
import { GraphData } from "../../models/Node";
import { detectFramework, FrameworkConfig } from "../configs/layoutStrategies";
import {
  getLayoutedElements,
  calculateFileGroupContainers,
} from "../utils/graphLayout";
import { EdgeTracker } from "../utils/EdgeTracker";
import { Logger } from "../../utils/webviewLogger";
import NodeVisibilityDrawer from "./drawers/NodeVisibilityDrawer";
import DeclarationNode from "./nodes/DeclarationNode";
import CallOrderEdge from "./edges/CallOrderEdge";
import ExecutionTraceDrawer from "./drawers/ExecutionTraceDrawer";
import useDebounce from "../hooks/useDebounce";
import convertToFlowDataExternal from "../utils/flowConversion";
import useExecutionTrace from "../hooks/useExecutionTrace";
import useGraphHighlighting from "../hooks/useGraphHighlighting";

import type {
  FunctionNodeData,
  DeclarationNodeData,
  FlowNode,
  FlowEdge,
  FlowGraphProps,
} from "../types/flowGraph";

const nodeTypes = {
  functionNode: FunctionNode as React.ComponentType<any>,
  declarationNode: DeclarationNode as React.ComponentType<any>,
  fileGroupContainer: FileGroupContainer as React.ComponentType<any>,
};

const edgeTypes = {
  callOrderEdge: CallOrderEdge as React.ComponentType<any>,
};

const FlowGraph: React.FC<FlowGraphProps> = ({ vscode }) => {
  const reactFlowInstance = useReactFlow();
  const [nodes, setNodes, onNodesChange] = useNodesState<FlowNode>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<FlowEdge>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [enableJumpToFile, setEnableJumpToFile] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [detectedFramework, setDetectedFramework] =
    useState<FrameworkConfig | null>(null);
  const [currentFileName, setCurrentFileName] = useState<string>("");
  const [isAutoSorting, setIsAutoSorting] = useState(false);

  const {
    lineHighlightedEdges,
    nodeHighlightedEdges,
    highlightedNodeId,
    handleHighlightEdge,
    handleClearHighlight,
    handleNodeHighlight,
    handleClearNodeHighlight,
  } = useGraphHighlighting({
    edges,
    nodes,
    setEdges,
    setNodes,
    isGraphReady,
    vscode,
  });
  const [pendingHighlightNodeId, setPendingHighlightNodeId] = useState<
    string | null
  >(null);
  const [isGraphReady, setIsGraphReady] = useState(false);

  useEffect(() => {
    return () => {
      (window as any).__goflowGraphReady = false;
      (window as any).__goflowEffectiveGraphReady = false;
      (window as any).__goflowEdges = [];
    };
  }, []);

  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [hiddenNodeIds, setHiddenNodeIds] = useState<Set<string>>(() => {
    try {
      const saved = localStorage.getItem("goflow-hidden-nodes");
      return saved ? new Set<string>(JSON.parse(saved)) : new Set<string>();
    } catch (error) {
      console.error("[FlowGraph] Failed to load hidden nodes", error);
      return new Set<string>();
    }
  });

  const [isTraceDrawerOpen, setIsTraceDrawerOpen] = useState(false);

  // Instrumentation / session tracking
  const renderStartRef = useRef<number>(0);
  const renderInvocationCountRef = useRef<number>(0);
  const queuedNodeHighlightCountsRef = useRef<Record<string, number>>({});
  const queuedEdgeHighlightCountRef = useRef<number>(0);
  const sessionCounterRef = useRef<number>(0);
  const currentSessionIdRef = useRef<number>(0);
  const prevGraphReadyRef = useRef<boolean>(false);
  const midReloadRef = useRef<boolean>(false);
  const prevNodesRef = useRef<FlowNode[]>([]);
  const prevEdgesRef = useRef<FlowEdge[]>([]);

  const debouncedNodes = useDebounce(nodes, 100);
  const lastContainerUpdateRef = useRef<string>("");

  // Logging bridge (declare BEFORE hook usage)
  const logToExtension = useCallback(
    (
      level: "DEBUG" | "INFO" | "WARN" | "ERROR",
      message: string,
      data?: any
    ) => {
      try {
        vscode.postMessage({
          command: "webviewLog",
          level,
          message,
          data:
            data !== undefined
              ? (() => {
                  try {
                    return JSON.parse(JSON.stringify(data));
                  } catch {
                    return String(data);
                  }
                })()
              : undefined,
        });
      } catch (e) {
        console.error("[FlowGraph] Failed to send log", e);
      }
    },
    [vscode]
  );

  // Execution trace hook (encapsulates static + dynamic trace logic)
  const {
    executionTrace,
    buildStaticExecutionTrace,
    clearTrace,
    handleCallEdge,
    recordUnresolvedCalls,
    recordRawLine,
    rootNodeId,
    rootCode,
    rootStartLine,
    setRootIfUnset,
  } = useExecutionTrace({ logFn: logToExtension });

  // Persist hidden node IDs
  useEffect(() => {
    try {
      localStorage.setItem(
        "goflow-hidden-nodes",
        JSON.stringify(Array.from(hiddenNodeIds))
      );
    } catch (error) {
      console.error("[FlowGraph] Failed to persist hidden nodes", error);
    }
  }, [hiddenNodeIds]);

  const getOriginalDashArray = useCallback(
    (edge: FlowEdge): string | undefined => {
      if (edge.style?.strokeDasharray)
        return edge.style.strokeDasharray as string;
      if (edge.data?.dashed === true) return "8 4";
      if (edge.data?.hasReturnValue === false) return "8 4";
      return undefined;
    },
    []
  );

  const handleToggleDrawer = useCallback(
    () => setIsDrawerOpen((prev) => !prev),
    []
  );

  const handleToggleNodeVisibility = useCallback((nodeId: string) => {
    setHiddenNodeIds((prev) => {
      const next = new Set(prev);
      if (next.has(nodeId)) next.delete(nodeId);
      else next.add(nodeId);
      return next;
    });
  }, []);

  const handleShowAllNodes = useCallback(() => setHiddenNodeIds(new Set()), []);
  const handleHideAllNodes = useCallback(() => {
    setHiddenNodeIds(
      new Set(nodes.filter((n) => n.type === "functionNode").map((n) => n.id))
    );
  }, [nodes]);

  const handleHighlightEdge = useCallback(
    (sourceNodeId: string, targetNodeId: string) => {
      const edgeKey = `${sourceNodeId}->${targetNodeId}`;
      setLineHighlightedEdges(new Set([edgeKey]));
      setEdges((current) =>
        current.map((edge) => {
          const currentKey = `${edge.source}->${edge.target}`;
          const isLineHighlighted = currentKey === edgeKey;
          const isNodeHighlighted = nodeHighlightedEdges.has(currentKey);
          const originalDashArray = getOriginalDashArray(edge);

          if (isLineHighlighted) {
            return {
              ...edge,
              animated: true,
              style: {
                ...edge.style,
                stroke: "#FFC107",
                strokeWidth: 4,
                strokeDasharray: originalDashArray,
              },
              zIndex: 1000,
            };
          }
          if (isNodeHighlighted) {
            return {
              ...edge,
              animated: true,
              style: {
                ...edge.style,
                stroke: "#FF6B6B",
                strokeWidth: 3,
                strokeDasharray: originalDashArray,
              },
              zIndex: 999,
            };
          }
          return {
            ...edge,
            animated: false,
            style: {
              ...edge.style,
              stroke: "#666",
              strokeWidth: 2,
              strokeDasharray: originalDashArray,
            },
            zIndex: 1,
          };
        })
      );
    },
    [nodeHighlightedEdges, getOriginalDashArray, setEdges]
  );

  const handleClearHighlight = useCallback(() => {
    setLineHighlightedEdges(new Set());
    setEdges((current) =>
      current.map((edge) => {
        const currentKey = `${edge.source}->${edge.target}`;
        const isNodeHighlighted = nodeHighlightedEdges.has(currentKey);
        const originalDashArray = getOriginalDashArray(edge);
        if (isNodeHighlighted) {
          return {
            ...edge,
            animated: true,
            style: {
              ...edge.style,
              stroke: "#FF6B6B",
              strokeWidth: 3,
              strokeDasharray: originalDashArray,
            },
            zIndex: 999,
          };
        }
        return {
          ...edge,
          animated: false,
          style: {
            ...edge.style,
            stroke: "#666",
            strokeWidth: 2,
            strokeDasharray: originalDashArray,
          },
          zIndex: 1,
        };
      })
    );
  }, [nodeHighlightedEdges, getOriginalDashArray, setEdges]);

  const handleNodeHighlight = useCallback(
    (targetNodeId: string) => {
      if (!isGraphReady || edges.length === 0 || nodes.length === 0) {
        const globalSession = (window as any).__goflowSessionId;
        const canUseBuffered =
          midReloadRef.current &&
          (window as any).__goflowPrevSessionBuffered &&
          Array.isArray(prevNodesRef.current) &&
          prevNodesRef.current.length > 0 &&
          Array.isArray(prevEdgesRef.current) &&
          prevEdgesRef.current.length > 0;

        if (canUseBuffered) {
          Logger.debug(
            `[FlowGraph] Mid-reload highlight using buffered previous graph for ${targetNodeId}. bufferedNodes=${prevNodesRef.current.length} bufferedEdges=${prevEdgesRef.current.length} session=${currentSessionIdRef.current} globalSession=${globalSession}`
          );

          const bufferedIncoming = prevEdgesRef.current.filter(
            (e) => e.target === targetNodeId
          );
          const edgeKeys = new Set(
            bufferedIncoming.map((e) => `${e.source}->${e.target}`)
          );
          setNodeHighlightedEdges(edgeKeys);
          setHighlightedNodeId(targetNodeId);

          setEdges((current) =>
            current.map((edge) => {
              const currentKey = `${edge.source}->${edge.target}`;
              const isLineHighlighted = lineHighlightedEdges.has(currentKey);
              const isNodeHighlighted = edgeKeys.has(currentKey);
              const originalDashArray = getOriginalDashArray(edge);

              if (isLineHighlighted) {
                return {
                  ...edge,
                  animated: true,
                  style: {
                    ...edge.style,
                    stroke: "#FFC107",
                    strokeWidth: 4,
                    strokeDasharray: originalDashArray,
                  },
                  zIndex: 1000,
                };
              }
              if (isNodeHighlighted) {
                return {
                  ...edge,
                  animated: true,
                  style: {
                    ...edge.style,
                    stroke: "#FF6B6B",
                    strokeWidth: 3,
                    strokeDasharray: originalDashArray,
                  },
                  zIndex: 999,
                };
              }
              return {
                ...edge,
                animated: false,
                style: {
                  ...edge.style,
                  stroke: "#666",
                  strokeWidth: 2,
                  strokeDasharray: originalDashArray,
                },
                zIndex: 1,
              };
            })
          );

          setNodes((currentNodes) =>
            currentNodes.map((node) => {
              const isParent = bufferedIncoming.some(
                (e) => e.source === node.id
              );
              const isTarget = node.id === targetNodeId;
              if (isParent || isTarget) {
                return {
                  ...node,
                  style: {
                    ...node.style,
                    border: isTarget
                      ? "3px solid #FF6B6B"
                      : "2px solid #FFA500",
                    boxShadow: isTarget
                      ? "0 0 10px rgba(255,107,107,0.5)"
                      : "0 0 8px rgba(255,165,0,0.4)",
                  },
                };
              }
              return {
                ...node,
                style: {
                  ...node.style,
                  border: undefined,
                  boxShadow: undefined,
                },
              };
            })
          );
          return;
        }

        queuedNodeHighlightCountsRef.current[targetNodeId] =
          (queuedNodeHighlightCountsRef.current[targetNodeId] || 0) + 1;
        const repeatCount = queuedNodeHighlightCountsRef.current[targetNodeId];
        if (repeatCount === 1) {
          Logger.debug(
            `[FlowGraph] Graph not ready. Queued highlight for ${targetNodeId}. nodes=${nodes.length} edges=${edges.length} ready=${isGraphReady} session=${currentSessionIdRef.current} globalSession=${globalSession}`
          );
        } else if (repeatCount % 5 === 0) {
          Logger.debug(
            `[FlowGraph] Graph still not ready after ${repeatCount} attempts for ${targetNodeId}. nodes=${nodes.length} edges=${edges.length} ready=${isGraphReady} session=${currentSessionIdRef.current} globalSession=${globalSession}`
          );
        }
        setPendingHighlightNodeId(targetNodeId);
        return;
      }

      const incomingEdges = edges.filter((e) => e.target === targetNodeId);
      const edgeKeys = new Set(
        incomingEdges.map((e) => `${e.source}->${e.target}`)
      );
      setNodeHighlightedEdges(edgeKeys);
      setHighlightedNodeId(targetNodeId);

      const allNodesData = nodes
        .filter((n) => n.type === "functionNode")
        .map((n) => ({
          id: n.id,
          label: (n.data as FunctionNodeData).label,
          type: (n.data as FunctionNodeData).type,
          file: (n.data as FunctionNodeData).file,
          line: (n.data as FunctionNodeData).line,
        }));
      const traced = EdgeTracker.tracePathsToRoot(targetNodeId, allNodesData);
      if (traced) {
        const report = EdgeTracker.getFormattedPathReport(traced);
        vscode.postMessage({
          command: "showPathTrace",
          tracedPath: traced,
          formattedReport: report,
        });
      }

      setEdges((current) =>
        current.map((edge) => {
          const currentKey = `${edge.source}->${edge.target}`;
          const isLineHighlighted = lineHighlightedEdges.has(currentKey);
          const isNodeHighlighted = edgeKeys.has(currentKey);
          const originalDashArray = getOriginalDashArray(edge);

          if (isLineHighlighted) {
            return {
              ...edge,
              animated: true,
              style: {
                ...edge.style,
                stroke: "#FFC107",
                strokeWidth: 4,
                strokeDasharray: originalDashArray,
              },
              zIndex: 1000,
            };
          }
          if (isNodeHighlighted) {
            return {
              ...edge,
              animated: true,
              style: {
                ...edge.style,
                stroke: "#FF6B6B",
                strokeWidth: 3,
                strokeDasharray: originalDashArray,
              },
              zIndex: 999,
            };
          }
          return {
            ...edge,
            animated: false,
            style: {
              ...edge.style,
              stroke: "#666",
              strokeWidth: 2,
              strokeDasharray: originalDashArray,
            },
            zIndex: 1,
          };
        })
      );

      setNodes((currentNodes) =>
        currentNodes.map((node) => {
          const isParent = incomingEdges.some((e) => e.source === node.id);
          const isTarget = node.id === targetNodeId;
          if (isParent || isTarget) {
            return {
              ...node,
              style: {
                ...node.style,
                border: isTarget ? "3px solid #FF6B6B" : "2px solid #FFA500",
                boxShadow: isTarget
                  ? "0 0 10px rgba(255,107,107,0.5)"
                  : "0 0 8px rgba(255,165,0,0.4)",
              },
            };
          }
          return {
            ...node,
            style: {
              ...node.style,
              border: undefined,
              boxShadow: undefined,
            },
          };
        })
      );
    },
    [
      isGraphReady,
      edges,
      nodes,
      lineHighlightedEdges,
      getOriginalDashArray,
      setEdges,
      setNodes,
      vscode,
    ]
  );

  useEffect(() => {
    if (prevGraphReadyRef.current !== isGraphReady) {
      logToExtension("DEBUG", "[FlowGraph] isGraphReady transition", {
        from: prevGraphReadyRef.current,
        to: isGraphReady,
        sessionId: currentSessionIdRef.current,
        nodeCount: nodes.length,
        edgeCount: edges.length,
      });
      prevGraphReadyRef.current = isGraphReady;
    }
  }, [
    isGraphReady,
    nodes.length,
    edges.length,
    logToExtension,
    currentSessionIdRef.current,
  ]);

  useEffect(() => {
    if (
      isGraphReady &&
      pendingHighlightNodeId &&
      edges.length > 0 &&
      nodes.length > 0
    ) {
      handleNodeHighlight(pendingHighlightNodeId);
      setPendingHighlightNodeId(null);
    }

    if (isGraphReady && edges.length > 0 && nodes.length > 0) {
      const pendingLineClick = (window as any).__goflowPendingLineClick;
      if (pendingLineClick) {
        delete (window as any).__goflowPendingLineClick;
        try {
          vscode.postMessage({
            command: "resolveDefinitionAtLine",
            file: pendingLineClick.file,
            line: pendingLineClick.functionStartLine,
            relativeLine: pendingLineClick.lineNumber,
            lineContent: pendingLineClick.lineContent,
            nodeId: pendingLineClick.nodeId,
            shouldTracePath: false,
          });

          handleNodeHighlight(pendingLineClick.nodeId);

          Logger.info("[FlowGraph] Processed queued line click", {
            nodeId: pendingLineClick.nodeId,
            lineNumber: pendingLineClick.lineNumber,
          });
        } catch (e) {
          Logger.error("[FlowGraph] Failed to process queued line click", e);
        }
      }
    }
  }, [
    isGraphReady,
    pendingHighlightNodeId,
    edges.length,
    nodes.length,
    handleNodeHighlight,
    vscode,
  ]);

  const handleClearNodeHighlight = useCallback(() => {
    setNodeHighlightedEdges(new Set());
    setHighlightedNodeId(null);
    setEdges((current) =>
      current.map((edge) => {
        const currentKey = `${edge.source}->${edge.target}`;
        const isLineHighlighted = lineHighlightedEdges.has(currentKey);
        const originalDashArray = getOriginalDashArray(edge);
        if (isLineHighlighted) {
          return {
            ...edge,
            animated: true,
            style: {
              ...edge.style,
              stroke: "#FFC107",
              strokeWidth: 4,
              strokeDasharray: originalDashArray,
            },
            zIndex: 1000,
          };
        }
        return {
          ...edge,
          animated: false,
          style: {
            ...edge.style,
            stroke: "#666",
            strokeWidth: 2,
            strokeDasharray: originalDashArray,
          },
          zIndex: 1,
        };
      })
    );
    setNodes((currentNodes) =>
      currentNodes.map((node) => ({
        ...node,
        style: {
          ...node.style,
          border: undefined,
          boxShadow: undefined,
        },
      }))
    );
  }, [lineHighlightedEdges, getOriginalDashArray, setEdges, setNodes]);

  useEffect(() => {
    if (isGraphReady && nodes.length > 0 && edges.length > 0) {
      (window as any).__goflowGraphReady = true;
      (window as any).__goflowEdges = edges;
      (window as any).__goflowEffectiveGraphReady = true;
      (window as any).__goflowNodes = nodes;

      const pendingNodeId = (window as any).__goflowPendingNodeHighlight;
      if (pendingNodeId) {
        handleNodeHighlight(pendingNodeId);
        delete (window as any).__goflowPendingNodeHighlight;
      }

      const pendingLineClick = (window as any).__goflowPendingLineClick;
      if (pendingLineClick) {
        delete (window as any).__goflowPendingLineClick;
        try {
          vscode.postMessage({
            command: "resolveDefinitionAtLine",
            file: pendingLineClick.file,
            line: pendingLineClick.functionStartLine,
            relativeLine: pendingLineClick.lineNumber,
            lineContent: pendingLineClick.lineContent,
            nodeId: pendingLineClick.nodeId,
            shouldTracePath: false,
          });
          handleNodeHighlight(pendingLineClick.nodeId);
          Logger.info("[FlowGraph] Processed queued line click", {
            nodeId: pendingLineClick.nodeId,
            lineNumber: pendingLineClick.lineNumber,
          });
        } catch (e) {
          Logger.error("[FlowGraph] Failed to process queued line click", e);
        }
      }
    } else {
      (window as any).__goflowGraphReady = false;
      (window as any).__goflowEffectiveGraphReady = false;
    }
  }, [isGraphReady, nodes, edges, handleNodeHighlight, vscode]);

  useEffect(() => {
    const unsubscribe = EdgeTracker.subscribe((edges) => {});
    return () => unsubscribe();
  }, []);

  const renderGraph = useCallback(
    async (data: GraphData, fileName?: string) => {
      try {
        (window as any).__goflowPendingNodeHighlight = null;
        (window as any).__goflowPendingLineClick = null;
        (window as any).__goflowPendingEdgeHighlights = [];

        renderStartRef.current = performance.now();
        renderInvocationCountRef.current += 1;

        Logger.info(`[FlowGraph] 🚀 START renderGraph`, {
          fileName,
          rawNodeCount: data.nodes.length,
          rawEdgeCount: data.edges.length,
          invocation: renderInvocationCountRef.current,
          sessionId: currentSessionIdRef.current,
          previousReadyState: isGraphReady,
          previousNodeCount: nodes.length,
          previousEdgeCount: edges.length,
        });
        logToExtension("DEBUG", "[FlowGraph] renderGraph start", {
          fileName,
          nodeCount: data.nodes.length,
          edgeCount: data.edges.length,
          isGraphReadyBefore: isGraphReady,
          invocation: renderInvocationCountRef.current,
          sessionId: currentSessionIdRef.current,
        });
        if (fileName) {
          setCurrentFileName(fileName);
          const firstNode = data.nodes[0];
          const fileContent = firstNode?.code || "";
          const detected = detectFramework(fileName, fileContent);
          setDetectedFramework(detected);
          logToExtension("DEBUG", "[FlowGraph] Framework detection", {
            detected: detected?.strategy.description,
          });
        }

        const { nodes: flowNodes, edges: flowEdges } =
          convertToFlowDataExternal(data, {
            vscode,
            detectedDirection: detectedFramework?.strategy.direction,
            lineHighlightedEdges,
            onHighlightEdge: handleHighlightEdge,
            onClearHighlight: handleClearHighlight,
            onNodeHighlight: handleNodeHighlight,
            onClearNodeHighlight: handleClearNodeHighlight,
          });
        const { nodes: layoutedNodes, edges: layoutedEdges } =
          await getLayoutedElements(flowNodes, flowEdges, detectedFramework);

        setNodes(layoutedNodes);
        setEdges(layoutedEdges);
        logToExtension("DEBUG", "[FlowGraph] Layout applied", {
          layoutNodeCount: layoutedNodes.length,
          layoutEdgeCount: layoutedEdges.length,
          invocation: renderInvocationCountRef.current,
        });

        setRootIfUnset(layoutedNodes);

        setIsLoading(false);
        setError(null);
        setIsGraphReady(true);
        logToExtension("INFO", "[FlowGraph] Graph ready", {
          invocation: renderInvocationCountRef.current,
          sessionId: currentSessionIdRef.current,
          queuedNodeHighlightAttempts: Object.entries(
            queuedNodeHighlightCountsRef.current
          ).map(([nodeId, attempts]) => ({ nodeId, attempts })),
          queuedEdgeEventsTotal: queuedEdgeHighlightCountRef.current,
          bufferedPrevGraph: {
            hadBuffer: midReloadRef.current,
            prevNodeCount: prevNodesRef.current.length,
            prevEdgeCount: prevEdgesRef.current.length,
          },
        });
        (window as any).__goflowGraphReady = true;
        (window as any).__goflowSessionId = currentSessionIdRef.current;
        (window as any).__goflowEffectiveGraphReady = true;
        (window as any).__goflowEdges = layoutedEdges;
        window.dispatchEvent(
          new CustomEvent("goflow-effective-ready", {
            detail: {
              sessionId: currentSessionIdRef.current,
              nodeCount: layoutedNodes.length,
              edgeCount: layoutedEdges.length,
            },
          })
        );
        midReloadRef.current = false;
        prevNodesRef.current = [];
        prevEdgesRef.current = [];
        try {
          const pendingNodeId = (window as any).__goflowPendingNodeHighlight;
          if (pendingNodeId) {
            delete (window as any).__goflowPendingNodeHighlight;
            handleNodeHighlight(pendingNodeId);
          }
          const pendingEdges =
            (window as any).__goflowPendingEdgeHighlights || [];
          if (Array.isArray(pendingEdges) && pendingEdges.length > 0) {
            pendingEdges.forEach((h: any) =>
              handleHighlightEdge(h.source, h.target)
            );
            delete (window as any).__goflowPendingEdgeHighlights;
          }
        } catch {}

        buildStaticExecutionTrace(layoutedEdges, layoutedNodes);
        const elapsed = performance.now() - renderStartRef.current;
        logToExtension("INFO", "[FlowGraph] Graph layout completed", {
          layoutNodeCount: layoutedNodes.length,
          layoutEdgeCount: layoutedEdges.length,
          elapsedMs: Math.round(elapsed),
          pendingHighlightNodeId:
            (window as any).__goflowPendingNodeHighlight || null,
          pendingEdgeQueueSize: Array.isArray(
            (window as any).__goflowPendingEdgeHighlights
          )
            ? (window as any).__goflowPendingEdgeHighlights.length
            : 0,
        });
      } catch (err) {
        console.error("[FlowGraph] Failed to render graph:", err);
        logToExtension("ERROR", "[FlowGraph] renderGraph failure", {
          error: err instanceof Error ? err.message : String(err),
        });
        setError(err instanceof Error ? err.message : "Unknown error");
        setIsLoading(false);
        setIsGraphReady(false);
      }
    },
    [
      setNodes,
      setEdges,
      detectedFramework,
      getLayoutedElements,
      buildStaticExecutionTrace,
      lineHighlightedEdges,
      handleHighlightEdge,
      handleClearHighlight,
      handleNodeHighlight,
      handleClearNodeHighlight,
      isGraphReady,
      nodes,
      logToExtension,
      setRootIfUnset,
    ]
  );

  const onNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      if (enableJumpToFile && node.type === "functionNode") {
        const data = node.data as FunctionNodeData;
        vscode.postMessage({
          command: "jumpToDefinition",
          file: data.file,
          line: data.line,
        });
      }
    },
    [vscode, enableJumpToFile]
  );

  const processQueuedInteractions = useCallback(() => {
    const pendingLineClick = (window as any).__goflowPendingLineClick;
    if (pendingLineClick) {
      Logger.info(`[FlowGraph] Processing queued line click`, {
        nodeId: pendingLineClick.nodeId,
        lineNumber: pendingLineClick.lineNumber,
        queueTime: Date.now() - pendingLineClick.timestamp,
      });

      vscode.postMessage({
        command: "resolveDefinitionAtLine",
        file: pendingLineClick.file,
        line: pendingLineClick.functionStartLine,
        relativeLine: pendingLineClick.lineNumber,
        lineContent: pendingLineClick.lineContent,
        nodeId: pendingLineClick.nodeId,
        shouldTracePath: false,
      });

      handleNodeHighlight(pendingLineClick.nodeId);

      delete (window as any).__goflowPendingLineClick;
    }

    const pendingNodeHighlight = (window as any).__goflowPendingNodeHighlight;
    if (pendingNodeHighlight) {
      handleNodeHighlight(pendingNodeHighlight);
      delete (window as any).__goflowPendingNodeHighlight;
    }
  }, [vscode, handleNodeHighlight]);

  useEffect(() => {
    const isEffectivelyReady =
      isGraphReady && nodes.length > 0 && edges.length > 0;

    if (isEffectivelyReady) {
      (window as any).__goflowGraphReady = true;
      (window as any).__goflowEdges = edges;
      (window as any).__goflowNodes = nodes;
      (window as any).__goflowEffectiveGraphReady = true;

      Logger.info(`[FlowGraph] Graph marked as ready`, {
        nodeCount: nodes.length,
        edgeCount: edges.length,
        sessionId: currentSessionIdRef.current,
      });

      processQueuedInteractions();
    } else {
      (window as any).__goflowGraphReady = false;
      (window as any).__goflowEffectiveGraphReady = false;
    }
  }, [isGraphReady, nodes, edges, processQueuedInteractions]);

  const handleAutoSort = useCallback(async () => {
    if (!detectedFramework || isAutoSorting) return;
    setIsAutoSorting(true);
    try {
      const codeNodes = nodes.filter((n) => n.type === "functionNode");
      const { nodes: layoutedNodes, edges: layoutedEdges } =
        await getLayoutedElements(codeNodes, edges, detectedFramework);
      setNodes(layoutedNodes);
      setEdges(layoutedEdges);
      buildStaticExecutionTrace(layoutedEdges, layoutedNodes);
    } catch (err) {
      console.error("[FlowGraph] Auto-sort failed:", err);
      setError(err instanceof Error ? err.message : "Auto-sort failed");
    } finally {
      setIsAutoSorting(false);
    }
  }, [
    nodes,
    edges,
    detectedFramework,
    isAutoSorting,
    setNodes,
    setEdges,
    getLayoutedElements,
    buildStaticExecutionTrace,
  ]);

  const handleExport = useCallback(
    () => vscode.postMessage({ command: "export" }),
    [vscode]
  );
  const handleFit = useCallback(
    () => vscode.postMessage({ command: "fitView" }),
    [vscode]
  );

  useEffect(() => {
    const codeNodes = debouncedNodes.filter((n) => n.type === "functionNode");
    const declarationNodes = debouncedNodes.filter(
      (n) => n.type === "declarationNode"
    );
    const currentContainers = debouncedNodes.filter(
      (n) => n.type === "fileGroupContainer"
    );
    if (codeNodes.length === 0 && declarationNodes.length === 0) {
      return;
    }
    const containerNodes = calculateFileGroupContainers(debouncedNodes);

    const currentSignature = JSON.stringify({
      codeNodeCount: codeNodes.length,
      containerCount: currentContainers.length,
      containerPositions: currentContainers.map((c: any) => ({
        id: c.id,
        x: c.position.x,
        y: c.position.y,
      })),
    });
    const newSignature = JSON.stringify({
      codeNodeCount: codeNodes.length,
      containerCount: containerNodes.length,
      containerPositions: containerNodes.map((c) => ({
        id: c.id,
        x: c.position.x,
        y: c.position.y,
      })),
    });

    if (
      currentSignature === newSignature &&
      currentSignature === lastContainerUpdateRef.current
    ) {
      return;
    }
    lastContainerUpdateRef.current = newSignature;

    setNodes((current) => {
      const withoutContainers = current.filter(
        (n) => n.type !== "fileGroupContainer"
      );
      return [...containerNodes, ...withoutContainers];
    });
  }, [debouncedNodes, calculateFileGroupContainers, setNodes]);

  useEffect(() => {
    vscode.postMessage({ command: "ready" });
  }, [vscode]);

  useEffect(() => {
    const messageHandler = async (event: MessageEvent) => {
      const message = event.data;
      if (!message || typeof message.command !== "string") {
        return;
      }
      try {
        switch (message.command) {
          case "setNodeDraggable":
            setNodes((curr) =>
              curr.map((n) =>
                n.id === message.nodeId
                  ? { ...n, draggable: !!message.draggable }
                  : n
              )
            );
            break;
          case "renderGraph":
            Logger.info(
              `[FlowGraph] renderGraph command received (prevReady=${isGraphReady}) nodesInPayload=${
                message.data?.nodes?.length ?? 0
              } edgesInPayload=${message.data?.edges?.length ?? 0} invocation=${
                renderInvocationCountRef.current + 1
              } nextSession=${sessionCounterRef.current + 1}`
            );
            sessionCounterRef.current += 1;
            currentSessionIdRef.current = sessionCounterRef.current;
            (window as any).__goflowSessionId = currentSessionIdRef.current;
            logToExtension("DEBUG", "[FlowGraph] renderGraph init", {
              sessionId: currentSessionIdRef.current,
              invocation: renderInvocationCountRef.current + 1,
              prevReadyState: isGraphReady,
              timestamp: Date.now(),
              prevNodeCount: nodes.length,
              prevEdgeCount: edges.length,
            });
            (window as any).__goflowGraphReady = false;
            (window as any).__goflowSessionId = currentSessionIdRef.current;
            (window as any).__goflowEffectiveGraphReady = false;
            (window as any).__goflowEdges = [];
            (window as any).__goflowEdgesClearedAt = Date.now();
            try {
              prevNodesRef.current = nodes;
              prevEdgesRef.current = edges;
              midReloadRef.current = true;
              (window as any).__goflowPrevSessionBuffered = {
                nodeCount: prevNodesRef.current.length,
                edgeCount: prevEdgesRef.current.length,
                sessionId: currentSessionIdRef.current - 1,
              };
            } catch {}
            setIsGraphReady(false);
            if (message.config) {
              setEnableJumpToFile(message.config.enableJumpToFile);
            }
            if (message.theme && typeof message.theme.isDark === "boolean") {
              if (!(window as any).__monacoAppliedTheme) {
                (window as any).__goflowTheme = message.theme;
              } else {
                Logger.debug(
                  "[FlowGraph] Ignored theme payload (theme already locked)"
                );
              }
            } else if (message.theme) {
              Logger.debug(
                "[FlowGraph] Ignored invalid theme payload (missing isDark boolean)"
              );
            }
            await renderGraph(message.data, message.data?.fileName);
            break;
          case "refresh":
            if (message.data) {
              await renderGraph(message.data, message.data?.fileName);
            }
            break;
          case "highlightEdge":
            {
              const globalReady = !!(window as any).__goflowGraphReady;
              const globalEdges = (window as any).__goflowEdges;
              const globalEdgeCount = Array.isArray(globalEdges)
                ? globalEdges.length
                : 0;
              const effectiveReady =
                isGraphReady && nodes.length > 0 && edges.length > 0;
              const fallbackReady =
                globalReady && globalEdgeCount > 0 && nodes.length === 0;

              if (!effectiveReady && !fallbackReady) {
                queuedEdgeHighlightCountRef.current += 1;
                const edgeQueueLen =
                  ((window as any).__goflowPendingEdgeHighlights || []).length +
                  1;
                if (
                  queuedEdgeHighlightCountRef.current === 1 ||
                  queuedEdgeHighlightCountRef.current % 5 === 0
                ) {
                  Logger.debug(
                    `[FlowGraph] Graph not ready. Queued edge highlight ${message.sourceNodeId}->${message.targetNodeId}`,
                    {
                      totalQueuedEdgeEvents:
                        queuedEdgeHighlightCountRef.current,
                      queueLen: edgeQueueLen,
                      reactReady: isGraphReady,
                      reactNodeCount: nodes.length,
                      reactEdgeCount: edges.length,
                      globalReady,
                      globalEdgeCount,
                    }
                  );
                }
                const pending =
                  (window as any).__goflowPendingEdgeHighlights || [];
                pending.push({
                  source: message.sourceNodeId,
                  target: message.targetNodeId,
                });
                (window as any).__goflowPendingEdgeHighlights = pending;
                return;
              }

              if (
                fallbackReady &&
                prevNodesRef.current.length > 0 &&
                prevEdgesRef.current.length > 0
              ) {
                Logger.info(
                  `[FlowGraph] Using buffered graph for edge highlight (React state not synced yet)`,
                  {
                    bufferedNodeCount: prevNodesRef.current.length,
                    bufferedEdgeCount: prevEdgesRef.current.length,
                    sourceNodeId: message.sourceNodeId,
                    targetNodeId: message.targetNodeId,
                  }
                );
                setNodes(prevNodesRef.current);
                setEdges(prevEdgesRef.current);
                setIsGraphReady(true);
              }

              handleHighlightEdge(message.sourceNodeId, message.targetNodeId);

              // Delegate dynamic execution trace update to hook
              handleCallEdge(
                message.sourceNodeId,
                message.targetNodeId,
                typeof message.sourceCallLine === "number"
                  ? message.sourceCallLine
                  : undefined
              );
            }
            break;
          case "clearHighlight":
            handleClearHighlight();
            break;
          case "recordTraceLine":
            if (
              Array.isArray(message.functionCalls) &&
              typeof message.relativeLine === "number"
            ) {
              const sourceFnNode = nodes.find(
                (n) =>
                  n.id === message.sourceNodeId && n.type === "functionNode"
              );
              const sourceCode =
                sourceFnNode && (sourceFnNode.data as FunctionNodeData).code
                  ? (sourceFnNode.data as FunctionNodeData).code
                  : undefined;
              const sourceLines = sourceCode ? sourceCode.split("\n") : [];
              const srcLineContent =
                sourceLines[message.relativeLine - 1] ||
                message.lineContent ||
                "";
              recordUnresolvedCalls(
                message.sourceNodeId,
                message.relativeLine,
                message.functionCalls,
                srcLineContent
              );
            }
            break;
          case "recordTraceLineRaw":
            if (typeof message.relativeLine === "number") {
              const sourceFnNode = nodes.find(
                (n) =>
                  n.id === message.sourceNodeId && n.type === "functionNode"
              );
              const sourceCode =
                sourceFnNode && (sourceFnNode.data as FunctionNodeData).code
                  ? (sourceFnNode.data as FunctionNodeData).code
                  : undefined;
              const sourceLines = sourceCode ? sourceCode.split("\n") : [];
              const srcLineContent =
                sourceLines[message.relativeLine - 1] ||
                message.lineContent ||
                "";
              recordRawLine(
                message.sourceNodeId,
                message.relativeLine,
                srcLineContent
              );
            }
            break;
          case "tracePathForLineClick":
            handleNodeHighlight(message.targetNodeId);
            break;
          default:
            Logger.debug(
              `[FlowGraph] Ignored unknown command: ${message.command}`
            );
        }
      } catch (err) {
        console.error("[FlowGraph] Error handling message:", err);
        setError(err instanceof Error ? err.message : "Unknown error");
        setIsLoading(false);
      }
    };
    window.addEventListener("message", messageHandler);
    return () => window.removeEventListener("message", messageHandler);
  }, [
    renderGraph,
    handleHighlightEdge,
    handleClearHighlight,
    handleNodeHighlight,
    isGraphReady,
    nodes,
    edges,
    handleCallEdge,
    recordUnresolvedCalls,
    recordRawLine,
    setNodes,
    setEdges,
  ]);

  return (
    <div style={{ width: "100vw", height: "100vh" }}>
      {error ? (
        <div className="loading-container">
          <div className="loading-text" style={{ color: "#ef4444" }}>
            ❌ Error: {error}
            <div style={{ marginTop: "16px", fontSize: "14px" }}>
              Check the browser console (F12) for details
            </div>
          </div>
        </div>
      ) : isLoading ? (
        <div className="loading-container">
          <div className="loading-text">
            Loading GoFlow Canvas...
            <div style={{ marginTop: "8px", fontSize: "12px", opacity: 0.7 }}>
              If this takes too long, check the console
            </div>
          </div>
        </div>
      ) : (
        <ReactFlow
          nodes={nodes.filter((n) => {
            if (n.type === "functionNode") {
              return !hiddenNodeIds.has(n.id);
            }
            if (n.type === "declarationNode") {
              const declData = n.data as DeclarationNodeData;
              if (!declData.usedBy || declData.usedBy.length === 0)
                return false;
              const hasVisibleCaller = declData.usedBy.some(
                (callerId) => !hiddenNodeIds.has(callerId)
              );
              return hasVisibleCaller;
            }
            if (n.type === "fileGroupContainer") {
              const fileName = (n.data as any).fileName;
              const visibleNodesInContainer = nodes.filter((node) => {
                if (node.type === "functionNode") {
                  return (
                    (node.data as FunctionNodeData).file === fileName &&
                    !hiddenNodeIds.has(node.id)
                  );
                }
                if (node.type === "declarationNode") {
                  const declData = node.data as DeclarationNodeData;
                  const usedBy = declData.usedBy || [];
                  const hasVisibleCaller = usedBy.some(
                    (callerId) =>
                      nodes.find((fn) => fn.id === callerId) &&
                      !hiddenNodeIds.has(callerId)
                  );
                  return hasVisibleCaller;
                }
                return false;
              });
              return visibleNodesInContainer.length > 0;
            }
            return true;
          })}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          fitView
          minZoom={0.1}
          maxZoom={2}
          nodesDraggable={true}
          nodesConnectable={false}
          elementsSelectable={true}
        >
          <Background />
          <Controls />
          <MiniMap
            nodeColor={(node) => {
              if (node.type === "fileGroupContainer")
                return "rgba(251,191,36,0.3)";
              if (node.type === "declarationNode") {
                const data = node.data as any;
                const colorMap: Record<string, string> = {
                  class: "#a855f7",
                  struct: "#06b6d4",
                  interface: "#f59e0b",
                  enum: "#84cc16",
                  type: "#6366f1",
                };
                return colorMap[data.type] || "#6b7280";
              }
              const data = node.data as any;
              return data.type === "function" ? "#4CAF50" : "#2196F3";
            }}
            nodeStrokeWidth={3}
            zoomable
            pannable
          />
          <Panel
            position="top-right"
            className="flow-graph-panel flow-graph-panel-modern"
          >
            <div className="flow-graph-button-group">
              <button
                onClick={handleToggleDrawer}
                className="fg-btn"
                title="Node Visibility"
              >
                👁️
              </button>
              <button
                onClick={() => setEnableJumpToFile(!enableJumpToFile)}
                className={`fg-btn ${
                  enableJumpToFile ? "fg-btn-active" : "fg-btn-inactive"
                }`}
                title={
                  enableJumpToFile ? "Jump to file: ON" : "Jump to file: OFF"
                }
              >
                {enableJumpToFile ? "🔗" : "⛔"}
              </button>
              <button
                onClick={handleAutoSort}
                className="fg-btn"
                title={
                  detectedFramework
                    ? `Auto Sort: ${detectedFramework.strategy.description}`
                    : "Auto Sort Layout"
                }
                disabled={!detectedFramework || isAutoSorting}
              >
                {isAutoSorting ? "⏳" : "🔄"}
              </button>
              <button onClick={handleFit} className="fg-btn" title="Fit view">
                ⊡
              </button>
              <button
                onClick={handleExport}
                className="fg-btn"
                title="Export diagram"
              >
                💾
              </button>
              <button
                onClick={() => {
                  const stats = EdgeTracker.getStats();
                  EdgeTracker.logCurrentState();
                  vscode.postMessage({
                    command: "showEdgeStats",
                    stats,
                    edges: EdgeTracker.getAllEdges(),
                    formattedReport: EdgeTracker.getEdgeListFormatted(),
                  });
                }}
                className="fg-btn"
                title="Edge statistics"
              >
                📊
              </button>
              <button
                onClick={() => setIsTraceDrawerOpen((p) => !p)}
                className={`fg-btn ${isTraceDrawerOpen ? "fg-btn-active" : ""}`}
                title="Execution Flow List"
              >
                🗒️
              </button>
            </div>
          </Panel>
          {detectedFramework && (
            <Panel position="bottom-left" className="flow-graph-info-panel">
              <div className="flow-graph-info-content">
                <div className="flow-graph-info-label">Detected:</div>
                <div className="flow-graph-info-value">
                  {detectedFramework.strategy.description}
                </div>
                <div className="flow-graph-info-hint">
                  {detectedFramework.rationale}
                </div>
              </div>
            </Panel>
          )}
        </ReactFlow>
      )}
      <NodeVisibilityDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        nodes={nodes
          .filter((n) => n.type === "functionNode")
          .map((n) => ({
            id: n.id,
            label: (n.data as FunctionNodeData).label,
            type: (n.data as FunctionNodeData).type,
            file: (n.data as FunctionNodeData).file,
            line: (n.data as FunctionNodeData).line,
          }))}
        hiddenNodeIds={hiddenNodeIds}
        onToggleNode={handleToggleNodeVisibility}
        onShowAll={handleShowAllNodes}
        onHideAll={handleHideAllNodes}
      />
      <ExecutionTraceDrawer
        isOpen={isTraceDrawerOpen}
        onClose={() => setIsTraceDrawerOpen(false)}
        trace={executionTrace}
        rootNodeId={rootNodeId}
        rootCode={rootCode}
        rootStartLine={rootStartLine}
        onClear={() => {
          clearTrace();
        }}
        onJumpToNode={(nodeId) => {
          handleNodeHighlight(nodeId);
          try {
            const target = nodes.find((n) => n.id === nodeId);
            if (target && reactFlowInstance) {
              const w =
                (target.style?.width as number) ||
                (target.width as number) ||
                600;
              const h =
                (target.style?.height as number) ||
                (target.height as number) ||
                300;
              reactFlowInstance.setCenter(
                target.position.x + w / 2,
                target.position.y + h / 2,
                {
                  zoom: 1,
                  duration: 400,
                }
              );
            }
          } catch (e) {
            logToExtension(
              "WARN",
              "[ExecutionFlow] Failed to center on node",
              e
            );
          }
        }}
      />
    </div>
  );
};

export default FlowGraph;

</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.



New problems detected after saving the file:
src/webview/components/FlowGraph.tsx
- [ts Error] Line 70: Cannot redeclare block-scoped variable 'handleHighlightEdge'.
- [ts Error] Line 71: Cannot redeclare block-scoped variable 'handleClearHighlight'.
- [ts Error] Line 72: Cannot redeclare block-scoped variable 'handleNodeHighlight'.
- [ts Error] Line 73: Cannot redeclare block-scoped variable 'handleClearNodeHighlight'.
- [ts Error] Line 79: Block-scoped variable 'isGraphReady' used before its declaration.
- [ts Error] Line 79: Variable 'isGraphReady' is used before being assigned.
- [ts Error] Line 211: Cannot redeclare block-scoped variable 'handleHighlightEdge'.
- [ts Error] Line 214: Cannot find name 'setLineHighlightedEdges'. Did you mean 'lineHighlightedEdges'?
- [ts Error] Line 265: Cannot redeclare block-scoped variable 'handleClearHighlight'.
- [ts Error] Line 266: Cannot find name 'setLineHighlightedEdges'. Did you mean 'lineHighlightedEdges'?
- [ts Error] Line 300: Cannot redeclare block-scoped variable 'handleNodeHighlight'.
- [ts Error] Line 323: Cannot find name 'setNodeHighlightedEdges'. Did you mean 'nodeHighlightedEdges'?
- [ts Error] Line 324: Cannot find name 'setHighlightedNodeId'. Did you mean 'highlightedNodeId'?
- [ts Error] Line 426: Cannot find name 'setNodeHighlightedEdges'. Did you mean 'nodeHighlightedEdges'?
- [ts Error] Line 427: Cannot find name 'setHighlightedNodeId'. Did you mean 'highlightedNodeId'?
- [ts Error] Line 599: Cannot redeclare block-scoped variable 'handleClearNodeHighlight'.
- [ts Error] Line 600: Cannot find name 'setNodeHighlightedEdges'. Did you mean 'nodeHighlightedEdges'?
- [ts Error] Line 601: Cannot find name 'setHighlightedNodeId'. Did you mean 'highlightedNodeId'?

<environment_details>
# Visual Studio Code Visible Files
src/webview/components/FlowGraph.tsx

# Visual Studio Code Open Tabs
src/webview/components/editors/ExecutionTraceCodeEditor.tsx
src/webview/components/editors/MonacoCodeEditor.tsx
src/webview/components/nodes/FunctionNode.tsx
src/webview/styles/function-node.css
src/webview/types/flowGraph.ts
src/webview/hooks/useExecutionTrace.ts
src/webview/hooks/useDebounce.ts
src/webview/utils/graphLayout.ts
src/webview/utils/flowConversion.ts
src/webview/hooks/useMessageBridge.ts
src/webview/hooks/useGraphHighlighting.ts
src/webview/components/FlowGraph.tsx
src/models/Node.ts

# Current Time
11/16/2025, 8:37:22 PM (Asia/Saigon, UTC+7:00)

# Current Mode
ACT MODE
</environment_details>
```

```
The user provided the following feedback:
<feedback>
[domains/image_processing/ocr_session_store.py:93] [INFO] [OCRSessionStore] Created session 9e6b1fad-81a7-44d1-a690-5c55a94a6c94
2025-11-16 21:15:18.010 | INFO     | manga_ocr.ocr:__init__:16 - Loading OCR model from kha-white/manga-ocr-base
2025-11-16 21:15:22.627 | INFO     | manga_ocr.ocr:__init__:28 - Using CPU
2025-11-16 21:15:23.342 | INFO     | manga_ocr.ocr:__init__:35 - OCR ready
[W1116 21:15:23.678536751 init.cpp:772] Warning: nvfuser is no longer supported in torch script, use _jit_set_nvfuser_enabled is deprecated and a no-op (function operator())
2025-11-16 21:15:23.690 | INFO     | lama_cleaner.model.lama:init_model:39 - Load LaMa model from: /home/khanhromvn/.cache/torch/hub/checkpoints/text_inpainting_manga.pt
[domains/image_processing/service.py:176] [INFO] ═════════════════ [STEP1] - BUBBLES SEGMENTATION ═════════════════
[domains/image_processing/service.py:191] [INFO] [STEP] Bubble Segmentation(Boundaries): /temp/step1_boundaries_8e153a1a91ae4a58ab3c71c370703502.jpg
[domains/image_processing/service.py:197] [INFO] ═════════════════ [STEP2] - BUBBLES TEXTS DETECTION AND RECTANGLE CALCULATED ═════════════════
[domains/image_processing/service.py:266] [INFO] [STEP2] [INSIDE BUBBLE] Use Black Canvas (Use From Step1) /temp/step2_blank_canvas_d5db51c9686647879f41ae507727745f.jpg
[domains/image_processing/service.py:270] [INFO] [STEP2] [INSIDE BUBBLE] Apply Text Masks And Caculated Boxes: /temp/step2_text_masks_016c8a2db87e42ea9eb59a7c23732823.jpg
[domains/image_processing/service.py:274] [INFO] [STEP2] [INSIDE BUBBLE] Clean Texts And Return To Background: /temp/cleaned_text_f0648b329838472da5c644e4471dc8c8.jpg
[domains/image_processing/service.py:283] [INFO] [STEP2] [INSIDE BUBBLE] Final Calculated Rectangle: /temp/step2_rectangles_fe9d0299f9dc4b58b69ae8505ffc5bc2.jpg
[domains/image_processing/service.py:314] [INFO] [STEP2] [INSIDE BUBBLE] Final Result: /temp/inside_final_result_5cd994d7022942f784ff861f645e2e03.jpg
2025-11-16 21:15:50.607 | INFO     | lama_cleaner.model.base:__call__:66 - hd_strategy: Original
2025-11-16 21:15:50.608 | INFO     | lama_cleaner.model.base:_pad_forward:49 - final forward pad size: (1600, 1120, 3)
[domains/image_processing/service.py:360] [INFO] [STEP2] [OUTSIDE] Apply Text Masks: /temp/outside_text_masks_44960537d84542329e7368714d696b35.jpg
[domains/image_processing/service.py:360] [INFO] [STEP2] [OUTSIDE] Use Black Canvas: /temp/outside_black_canvas_332b454f54b248b6baed1f5192b1bb13.jpg
[domains/image_processing/service.py:360] [INFO] [STEP2] [OUTSIDE] Apply Filter To Add Boxes Filter: /temp/outside_filtered_boxes_c3a3909ff79c47ab8cafc4494b1fe364.jpg
[domains/image_processing/service.py:360] [INFO] [STEP2] [OUTSIDE] Remove Text Mask Filter Boxes And Return To Background: /temp/outside_filtered_masks_9d721f1c935040e880cca1fa2cdfe0be.jpg
[domains/image_processing/service.py:360] [INFO] [STEP2] [OUTSIDE] Calculated Rectangle: /temp/outside_calculated_rectangle_b7858e1f39aa40bcb44c0540ea1d2920.jpg
[domains/image_processing/service.py:360] [INFO] [STEP2] [OUTSIDE] Clean Text Mask Using InPainting: /temp/outside_inpainted_0093ff889d604d3989d4e09da858ca21.jpg
[domains/image_processing/service.py:397] [INFO] [STEP2] [OUTSIDE] Final Result: /temp/outside_final_result_a86af60b0e9e4e64bfe4f2a9b478e44f.jpg
[domains/image_processing/service.py:443] [INFO] [STEP2] [INSIDE&OUTSIDE] Final Result: /temp/inside_outside_final_result_e32277b4a4d54db79a1508e1dc7bb360.jpg
[domains/image_processing/service.py:454] [INFO] ═════════════════ [STEP3] OCR ═════════════════
[domains/image_processing/service.py:465] [INFO] [STEP3] OCR Inside Texts: ['文化祭模擬店の試食会を始めます！', '審査は我々文化祭実行委員が執り行います！', 'それでは．．．', 'がんばってルナちゃ～ん！']
[domains/image_processing/service.py:476] [INFO] [STEP3] OCR Outside Texts: ['２０１４年くんが切り替えていたので、大変だなあ．．．', '彼女は、文化祭神経には、', '第０話・吸血鬼ちゃんと試写会']
INFO:     127.0.0.1:33794 - "POST /api/v1/ocr-session/init HTTP/1.1" 200 OK

dựa vào api /ocr-session/init  thì trong log tôi thấy có orc lại có các log như "Clean Texts And Return To Background" và "[STEP2] [OUTSIDE] Remove Text Mask Filter Boxes And Return To Background" vì orc ko cần phải cleantext. ngoài ra PanelCraft client chỉ đang hiển thị kết quả của INSIDE. nó phải xử lý cả ousside và inside giống "[STEP2] [INSIDE&OUTSIDE] Final Result" nhưng giữu text.
</feedback>

[execute_command for 'python backend/run.py'] Result:
The user denied this operation.

<environment_details>
# Visual Studio Code Visible Files
src/renderer/src/config/api.config.ts

# Visual Studio Code Open Tabs
src/renderer/src/presentation/pages/Home/components/Control/components/OCRResultsTable.tsx
src/renderer/src/presentation/pages/Home/components/Canvas/components/ProcessPanel.tsx
src/renderer/src/components/common/CustomCombobox.tsx
backend/app/api/schemas/ocr_session.py
backend/app/domains/image_processing/ocr_session_store.py
backend/app/api/routes/processing.py
src/renderer/src/config/api.config.ts
src/renderer/src/services/backend.service.ts
src/renderer/src/contexts/ProcessingContext.tsx
src/renderer/src/presentation/pages/Home/index.tsx
src/renderer/src/presentation/pages/Home/components/Canvas/index.tsx
src/renderer/src/presentation/pages/Home/components/Control/index.tsx
src/renderer/src/presentation/pages/Home/components/Canvas/components/OriginalPanel.tsx

# Current Time
11/16/2025, 9:43:44 PM (Asia/Saigon, UTC+7:00)

# Current Mode
ACT MODE
</environment_details>
```

```
[ask_followup_question for 'Bổ sung chi tiết còn thiếu để mình cố định logic: 1) Mỗi tay giữ: a) một stack đầy đủ (có thể 64) hay b) chỉ đúng 1 item? 2) Nếu tay đang có stack chưa full và bạn nhặt item cùng loại trên đất thì cho gộp vào stack hay chặn? 3) Khi cả hai tay đều đầy (theo quy tắc ở trên) và item rơi không thể gộp: a) bỏ qua (item vẫn nằm trên đất) hay b) đẩy ra thành entity mới (thực ra giống a) hoặc c) gửi cảnh báo cho người chơi và vẫn bỏ qua? 4) Khi mở chest/barrel: chỉ cho phép kéo item trực tiếp vào hai ô (main/offhand) và nếu hai tay full thì không thể chuyển thêm — đúng chứ? 5) Có cần hiển thị hai ô lớn thay vì toàn bộ lưới inventory trong màn hình Inventory (phím E) hay chỉ ẩn phần lưới và để hotbar vẫn hiển thị? (Hotbar thực chất sẽ vô dụng vì chỉ 2 tay, nên mình dự định ẩn toàn bộ slot inventory + hotbar, chỉ để lại armor + offhand + crafting 2x2 nếu bạn vẫn muốn) 6) Crafting trong GUI mặc định (2x2) có giữ nguyên không? Nếu có thì người chơi có thể đặt item từ tay vào grid và sản phẩm craft sẽ xuất hiện ở ô kết quả: ô kết quả này có được lấy nếu một tay trống hay cần mod khác xử lý? 7) Cần file config (server) để bật/tắt: cho gộp stack, hiển thị hotbar, bật crafting 2x2? 8) Khi chết: rơi hai món đang cầm như bình thường (yes/no)? 9) Thông báo khi không thể nhặt thêm: chat message, action bar hay title? Chọn giúp cho mỗi mục hoặc ghi rõ khác nếu muốn.'] Result:
<answer>
1/ a) cs thể cầm 1 stack
2/ cho gộp nếu cùng item
3/ bỏ qua
4/ đúng
5/ đúng
8/ yes
</answer>

<environment_details>
# Visual Studio Code Visible Files
build.gradle

# Visual Studio Code Open Tabs
README.md
build.gradle

# Current Time
11/16/2025, 9:22:48 PM (Asia/Saigon, UTC+7:00)

# Current Mode
ACT MODE
</environment_details>
```

```
[ask_followup_question for 'Bạn muốn áp dụng giống hệt MonacoCodeEditor (xóa toàn bộ các background highlight và fade dòng trong ExecutionTraceCodeEditor) hay chỉ muốn chỉnh lại phần gutter / padding số dòng (giữ nguyên highlight phân đoạn thực thi)?'] Result:
<answer>
chỉ áp dụng cho phần số dòng thêm padding. ko sửa các phần khác\
</answer>

<environment_details>
# Visual Studio Code Visible Files
src/webview/components/editors/ExecutionTraceCodeEditor.tsx

# Visual Studio Code Open Tabs
src/webview/components/nodes/FunctionNode.tsx
src/webview/styles/function-node.css
src/webview/components/editors/MonacoCodeEditor.tsx
src/webview/components/editors/ExecutionTraceCodeEditor.tsx

# Current Time
11/16/2025, 10:37:25 PM (Asia/Saigon, UTC+7:00)

# Current Mode
ACT MODE
</environment_details>
```

còn lại search_files, list_files, list_code_definition_names, attempt_completion tôi chưa có

đây là docs mẫu
```
<search_files>
<path>src</path>
<regex>function\s+\w+\(</regex>
<file_pattern>*.ts</file_pattern>
</search_files>
```


