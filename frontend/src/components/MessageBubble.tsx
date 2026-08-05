import { Bot, FileText, User } from "lucide-react";

import { ChatMessage } from "../App";

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  const agentLabel = isUser ? "我" : message.agentName === "summary" ? "文档总结" : "知识问答";

  return (
    <div className={`message ${isUser ? "user" : "assistant"}`}>
      <div className="message-avatar">{isUser ? <User size={15} /> : <Bot size={15} />}</div>
      <div className="message-body">
        <div className="message-agent">{agentLabel}</div>
        <div className="message-content">{message.content}</div>
        {message.citations && message.citations.length > 0 && (
          <div className="citations">
            <div className="citations-title">
              <FileText size={13} />
              来源 {message.citations.length}
            </div>
            {message.citations.slice(0, 4).map((citation) => (
              <div key={citation.chunk_id} className="citation-item">
                <span className="citation-doc">
                  {citation.filename}
                  {citation.page_number ? ` · 第 ${citation.page_number} 页` : ""}
                </span>
                <span className="citation-excerpt">{citation.excerpt}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
