import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import {
  oneDark,
  oneLight,
} from "react-syntax-highlighter/dist/esm/styles/prism";

function CodeBlock({ className, children, theme }) {
  const [copied, setCopied] = useState(false);

  const match = /language-(\w+)/.exec(className || "");
  const code = String(children).replace(/\n$/, "");
  const language = match?.[1] || "";

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch {
      setCopied(false);
    }
  }

  return (
    <div className="chat-code-block">
      <div className="chat-code-header">
        <span>{language || "code"}</span>
        <button type="button" onClick={handleCopy}>
          {copied ? "Скопировано" : "Скопировать"}
        </button>
      </div>

      <SyntaxHighlighter
        language={language || "text"}
        style={theme === "dark" ? oneDark : oneLight}
        PreTag="div"
        customStyle={{
          margin: 0,
          borderRadius: 0,
          background: "transparent",
          fontSize: "14px",
        }}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
}

function MarkdownMessage({ content, theme }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code({ className, children, ...props }) {
          const isBlock = Boolean(className);

          if (!isBlock) {
            return (
              <code className="chat-inline-code" {...props}>
                {children}
              </code>
            );
          }

          return (
            <CodeBlock className={className} theme={theme}>
              {children}
            </CodeBlock>
          );
        },
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

export default MarkdownMessage;