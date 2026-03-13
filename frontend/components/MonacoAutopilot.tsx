'use client';

import React, { useRef, useEffect, useState } from 'react';
import Editor, { Monaco } from '@monaco-editor/react';
import * as monaco from 'monaco-editor';
import { getAutopilotClient, Suggestion as AutopilotSuggestion, CorrectionSuggestion } from '@/lib/autopilotClient';

interface MonacoAutopilotProps {
  initialCode?: string;
  onCodeChange?: (code: string) => void;
  language?: 'DIOTEC360';
}

interface EditorState {
  code: string;
  cursorPosition: number;
  selection?: { start: number; end: number };
}

const MonacoAutopilot: React.FC<MonacoAutopilotProps> = ({
  initialCode = '',
  onCodeChange,
  language = 'DIOTEC360'
}) => {
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<Monaco | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [safetyStatus, setSafetyStatus] = useState<'safe' | 'unsafe' | 'analyzing' | 'unknown'>('unknown');
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [corrections, setCorrections] = useState<CorrectionSuggestion[]>([]);
  const decorationsRef = useRef<string[]>([]);

  // Configure DIOTEC360 language when Monaco loads
  const handleEditorWillMount = (monaco: Monaco) => {
    // Register DIOTEC360 language
    monaco.languages.register({ id: 'DIOTEC360' });

    // Define DIOTEC360 language tokens
    monaco.languages.setMonarchTokensProvider('DIOTEC360', {
      keywords: [
        'intent', 'guard', 'verify', 'solve', 'using',
        'let', 'const', 'if', 'else', 'return',
        'true', 'false', 'null'
      ],
      intentTypes: [
        'payment', 'transfer', 'swap', 'mint', 'burn',
        'deposit', 'withdraw', 'stake', 'unstake'
      ],
      operators: [
        '=', '>', '<', '!', '==', '<=', '>=', '!=',
        '+', '-', '*', '/', '%', '&&', '||'
      ],
      symbols: /[=><!~?:&|+\-*\/\^%]+/,
      
      tokenizer: {
        root: [
          // Intent types
          [/\b(payment|transfer|swap|mint|burn|deposit|withdraw|stake|unstake)\b/, 'type.identifier'],
          
          // Keywords
          [/\b(intent|guard|verify|solve|using|let|const|if|else|return)\b/, 'keyword'],
          
          // Identifiers
          [/[a-z_$][\w$]*/, 'identifier'],
          [/[A-Z][\w\$]*/, 'type.identifier'],
          
          // Whitespace
          { include: '@whitespace' },
          
          // Numbers
          [/\d*\.\d+([eE][\-+]?\d+)?/, 'number.float'],
          [/\d+/, 'number'],
          
          // Strings
          [/"([^"\\]|\\.)*$/, 'string.invalid'],
          [/"/, 'string', '@string'],
          
          // Operators
          [/@symbols/, {
            cases: {
              '@operators': 'operator',
              '@default': ''
            }
          }],
          
          // Delimiters
          [/[{}()\[\]]/, '@brackets'],
          [/[;,.]/, 'delimiter'],
        ],
        
        whitespace: [
          [/[ \t\r\n]+/, ''],
          [/\/\*/, 'comment', '@comment'],
          [/\/\/.*$/, 'comment'],
        ],
        
        comment: [
          [/[^\/*]+/, 'comment'],
          [/\*\//, 'comment', '@pop'],
          [/[\/*]/, 'comment']
        ],
        
        string: [
          [/[^\\"]+/, 'string'],
          [/\\./, 'string.escape'],
          [/"/, 'string', '@pop']
        ],
      },
    });

    // Define DIOTEC360 language configuration
    monaco.languages.setLanguageConfiguration('DIOTEC360', {
      comments: {
        lineComment: '//',
        blockComment: ['/*', '*/']
      },
      brackets: [
        ['{', '}'],
        ['[', ']'],
        ['(', ')']
      ],
      autoClosingPairs: [
        { open: '{', close: '}' },
        { open: '[', close: ']' },
        { open: '(', close: ')' },
        { open: '"', close: '"' },
        { open: "'", close: "'" },
      ],
      surroundingPairs: [
        { open: '{', close: '}' },
        { open: '[', close: ']' },
        { open: '(', close: ')' },
        { open: '"', close: '"' },
        { open: "'", close: "'" },
      ],
    });

    // Define DIOTEC360 theme
    monaco.editor.defineTheme('DIOTEC360-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'keyword', foreground: 'C586C0', fontStyle: 'bold' },
        { token: 'type.identifier', foreground: '4EC9B0' },
        { token: 'identifier', foreground: '9CDCFE' },
        { token: 'number', foreground: 'B5CEA8' },
        { token: 'string', foreground: 'CE9178' },
        { token: 'comment', foreground: '6A9955', fontStyle: 'italic' },
        { token: 'operator', foreground: 'D4D4D4' },
      ],
      colors: {
        'editor.background': '#1E1E1E',
        'editor.foreground': '#D4D4D4',
        'editorLineNumber.foreground': '#858585',
        'editorCursor.foreground': '#AEAFAD',
      }
    });
  };

  // Handle editor mount
  const handleEditorDidMount = (editor: monaco.editor.IStandaloneCodeEditor, monacoInstance: Monaco) => {
    editorRef.current = editor;
    monacoRef.current = monacoInstance;
    setIsReady(true);

    // Set DIOTEC360 theme
    monacoInstance.editor.setTheme('DIOTEC360-dark');

    // Register completion provider
    registerCompletionProvider(monacoInstance);

    // Listen for content changes
    editor.onDidChangeModelContent(() => {
      const code = editor.getValue();
      if (onCodeChange) {
        onCodeChange(code);
      }
    });

    // Focus editor
    editor.focus();
  };

  // Get current editor state
  const getEditorState = (): EditorState | null => {
    if (!editorRef.current) return null;

    const editor = editorRef.current;
    const model = editor.getModel();
    if (!model) return null;

    const position = editor.getPosition();
    if (!position) return null;

    const code = model.getValue();
    const cursorPosition = model.getOffsetAt(position);

    const selection = editor.getSelection();
    let selectionRange: { start: number; end: number } | undefined;
    
    if (selection && !selection.isEmpty()) {
      selectionRange = {
        start: model.getOffsetAt(selection.getStartPosition()),
        end: model.getOffsetAt(selection.getEndPosition())
      };
    }

    return {
      code,
      cursorPosition,
      selection: selectionRange
    };
  };

  // Update traffic light based on safety status
  const updateTrafficLight = (status: 'safe' | 'unsafe' | 'analyzing' | 'unknown') => {
    if (status === safetyStatus) return; // No change needed
    
    setIsTransitioning(true);
    setSafetyStatus(status);
    
    // Reset transition after 100ms
    setTimeout(() => setIsTransitioning(false), 100);
  };

  // Display correction tooltips
  const displayCorrectionTooltips = (correctionList: CorrectionSuggestion[]) => {
    if (!editorRef.current || !monacoRef.current) return;
    
    const editor = editorRef.current;
    const monacoInstance = monacoRef.current;
    const model = editor.getModel();
    if (!model) return;
    
    // Update corrections state
    setCorrections(correctionList);
    
    // Clear existing decorations
    decorationsRef.current = editor.deltaDecorations(decorationsRef.current, []);
    
    // Create new decorations for each correction
    const newDecorations: monaco.editor.IModelDeltaDecoration[] = correctionList.map((correction) => {
      const lineNumber = correction.line;
      const lineContent = model.getLineContent(lineNumber);
      const lineLength = lineContent.length;
      
      return {
        range: new monacoInstance.Range(lineNumber, 1, lineNumber, lineLength + 1),
        options: {
          isWholeLine: false,
          className: correction.severity === 'error' ? 'correction-error-line' : 'correction-warning-line',
          glyphMarginClassName: correction.severity === 'error' ? 'correction-error-glyph' : 'correction-warning-glyph',
          hoverMessage: {
            value: `**${correction.message}**\n\n\`\`\`DIOTEC360\n${correction.fix}\n\`\`\`\n\n*Click to apply fix*`,
            isTrusted: true,
          },
          glyphMarginHoverMessage: {
            value: correction.message,
            isTrusted: true,
          },
        },
      };
    });
    
    // Apply decorations
    decorationsRef.current = editor.deltaDecorations([], newDecorations);
  };

  // Register completion provider
  const registerCompletionProvider = (monaco: Monaco) => {
    monaco.languages.registerCompletionItemProvider('DIOTEC360', {
      triggerCharacters: [' ', '.', '(', '{'],
      
      provideCompletionItems: async (
        model: monaco.editor.ITextModel,
        position: monaco.Position,
        context: monaco.languages.CompletionContext,
        token: monaco.CancellationToken
      ) => {
        try {
          // Get current editor state
          const code = model.getValue();
          const cursorPosition = model.getOffsetAt(position);
          
          // Get suggestions from Autopilot
          const autopilotClient = getAutopilotClient();
          const response = await autopilotClient.getSuggestionsDebounced({
            code,
            cursorPosition,
          });
          
          // Task 14.1: Update ALL UI components from response
          // 1. Update traffic light with safety status
          updateTrafficLight(response.safetyStatus.status);
          
          // 2. Display correction tooltips
          displayCorrectionTooltips(response.corrections);
          
          // 3. Transform Autopilot suggestions to Monaco completion items
          const suggestions: monaco.languages.CompletionItem[] = response.suggestions.map((suggestion) => {
            return {
              label: suggestion.label,
              kind: mapSuggestionKindToMonaco(suggestion.kind, monaco),
              insertText: suggestion.insertText,
              detail: suggestion.detail,
              documentation: suggestion.documentation ? {
                value: suggestion.documentation,
                isTrusted: true,
              } : undefined,
              sortText: suggestion.sortText || `${1000 - suggestion.priority}`,
              range: {
                startLineNumber: position.lineNumber,
                startColumn: position.column,
                endLineNumber: position.lineNumber,
                endColumn: position.column,
              },
            };
          });
          
          return {
            suggestions,
            incomplete: false,
          };
        } catch (error) {
          console.error('Error providing completions:', error);
          return {
            suggestions: [],
            incomplete: false,
          };
        }
      },
    });
  };

  // Map Autopilot suggestion kind to Monaco CompletionItemKind
  const mapSuggestionKindToMonaco = (
    kind: AutopilotSuggestion['kind'],
    monaco: Monaco
  ): monaco.languages.CompletionItemKind => {
    switch (kind) {
      case 'keyword':
        return monaco.languages.CompletionItemKind.Keyword;
      case 'guard':
        return monaco.languages.CompletionItemKind.Function;
      case 'verify':
        return monaco.languages.CompletionItemKind.Function;
      case 'solve':
        return monaco.languages.CompletionItemKind.Function;
      case 'variable':
        return monaco.languages.CompletionItemKind.Variable;
      default:
        return monaco.languages.CompletionItemKind.Text;
    }
  };

  // Get traffic light glow class
  const getTrafficLightClass = () => {
    const baseClass = 'w-full h-full border border-gray-700 rounded-lg overflow-hidden transition-all duration-100';
    
    switch (safetyStatus) {
      case 'safe':
        return `${baseClass} shadow-[0_0_20px_rgba(34,197,94,0.4)]`; // Green glow
      case 'unsafe':
        return `${baseClass} shadow-[0_0_20px_rgba(239,68,68,0.4)]`; // Red glow
      case 'analyzing':
        return `${baseClass} shadow-[0_0_20px_rgba(59,130,246,0.3)]`; // Blue glow
      default:
        return baseClass; // No glow
    }
  };

  return (
    <>
      <style jsx global>{`
        .correction-error-line {
          background-color: rgba(239, 68, 68, 0.1);
          border-bottom: 2px wavy rgba(239, 68, 68, 0.6);
        }
        
        .correction-warning-line {
          background-color: rgba(251, 191, 36, 0.1);
          border-bottom: 2px wavy rgba(251, 191, 36, 0.6);
        }
        
        .correction-error-glyph {
          background-color: rgba(239, 68, 68, 0.8);
          width: 4px !important;
          margin-left: 3px;
        }
        
        .correction-warning-glyph {
          background-color: rgba(251, 191, 36, 0.8);
          width: 4px !important;
          margin-left: 3px;
        }
      `}</style>
      <div className={getTrafficLightClass()}>
        <Editor
          height="100%"
          defaultLanguage="DIOTEC360"
          defaultValue={initialCode}
          theme="DIOTEC360-dark"
          beforeMount={handleEditorWillMount}
          onMount={handleEditorDidMount}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            roundedSelection: true,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            wordWrap: 'on',
            wrappingIndent: 'indent',
            padding: { top: 16, bottom: 16 },
            suggestOnTriggerCharacters: true,
            quickSuggestions: {
              other: true,
              comments: false,
              strings: false
            },
            acceptSuggestionOnCommitCharacter: true,
            acceptSuggestionOnEnter: 'on',
            snippetSuggestions: 'top',
            glyphMargin: true,
          }}
        />
      </div>
    </>
  );
};

export default MonacoAutopilot;
